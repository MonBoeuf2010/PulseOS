"""Briefing assembly + ranking. Composes signals → council → ranked, personalized items.
Ranking = expected_value × confidence × relevance, precision-first (Phase 2 PRD FR-8)."""
from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import Subject
from app.repositories.briefings import BriefingRepository

MIN_CONFIDENCE = 0.55   # precision-first threshold: don't surface low-confidence noise


class BriefingService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = BriefingRepository(session)

    async def dashboard(self, subject: Subject) -> dict:
        briefing = await self.repo.latest(subject.tenant_id, subject.user_id)
        return {
            "briefing": _briefing_to_dict(briefing) if briefing else None,
            "streams": [],
            "analytics": await self.repo.value_summary(subject.tenant_id, subject.user_id),
        }

    async def list(self, subject: Subject, cursor: str | None, limit: int) -> dict:
        rows = await self.repo.list(subject.tenant_id, subject.user_id, limit)
        return {"items": [_briefing_to_dict(b) for b in rows], "next_cursor": None}

    async def get(self, subject: Subject, briefing_id: UUID) -> dict:
        briefing = await self.repo.get(subject.tenant_id, subject.user_id, briefing_id)
        if briefing is None:
            from fastapi import HTTPException, status
            raise HTTPException(status.HTTP_404_NOT_FOUND, "briefing not found")
        return _briefing_to_dict(briefing)

    async def enqueue_generate(self, subject: Subject) -> str:
        from app.core.config import get_settings
        job_id = str(uuid4())
        # With no background worker (default on free/single-box hosting), build the
        # briefing inline in the request. Only hand off to Celery when a worker is
        # actually deployed — otherwise .delay() would silently enqueue a job that
        # nothing ever consumes and the briefing would never appear.
        if get_settings().enable_background_jobs:
            from app.workers.tasks import build_briefing
            try:
                build_briefing.delay(str(subject.tenant_id), str(subject.user_id), job_id)
                return job_id
            except Exception:
                pass  # broker unreachable → fall through to inline build
        from app.workers.tasks import build_briefing_sync
        await build_briefing_sync(subject.tenant_id, subject.user_id, job_id)
        return job_id

    async def record_feedback(self, subject: Subject, item_id: UUID, verdict: str,
                              note: str | None):
        item = await self.repo.get_item(subject.tenant_id, item_id)
        if item is None:
            from fastapi import HTTPException, status
            raise HTTPException(status.HTTP_404_NOT_FOUND, "item not found")
        await self.repo.record_feedback(tenant_id=subject.tenant_id, user_id=subject.user_id,
                                        item_id=item_id, verdict=verdict, note=note)

    @staticmethod
    def rank(items: list[dict]) -> list[dict]:
        scored = [(i["expected_value_norm"] * i["confidence"] * i["relevance"], i) for i in items]
        return [i for s, i in sorted(scored, key=lambda x: x[0], reverse=True)
                if i["confidence"] >= MIN_CONFIDENCE]


def _briefing_to_dict(b) -> dict:
    items = sorted(b.items, key=lambda i: i.rank)
    return {
        "id": str(b.id),
        "generated_at": b.generated_at.isoformat() if b.generated_at else None,
        "period": b.period,
        "summary": b.summary,
        "items": [{
            "id": str(i.id),
            "category": i.category,
            "title": i.title,
            "rationale": i.rationale,
            "confidence": float(i.confidence),
            "expected_value": float(i.expected_value) if i.expected_value is not None else None,
            "cost_of_inaction": i.cost_of_inaction,
            "evidence_refs": [str(r) for r in (i.evidence_refs or [])],
            "council_report_id": str(i.council_report_id) if i.council_report_id else None,
            "rank": i.rank,
        } for i in items],
    }
