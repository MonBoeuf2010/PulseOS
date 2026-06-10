"""Briefing assembly + ranking. Composes signals → council → ranked, personalized items.
Ranking = expected_value × confidence × relevance, precision-first (Phase 2 PRD FR-8)."""
from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import Subject

MIN_CONFIDENCE = 0.55   # precision-first threshold: don't surface low-confidence noise


class BriefingService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def dashboard(self, subject: Subject) -> dict:
        briefing = await self._latest(subject)
        return {"briefing": briefing, "streams": [], "analytics": await self._value_summary(subject)}

    async def list(self, subject: Subject, cursor: str | None, limit: int) -> dict:
        return {"items": [], "next_cursor": None}   # SCAFFOLD: cursor-paginated query

    async def get(self, subject: Subject, briefing_id: UUID) -> dict:
        return {"id": str(briefing_id), "items": []}  # SCAFFOLD

    async def enqueue_generate(self, subject: Subject) -> str:
        from app.workers.tasks import build_briefing
        job_id = str(uuid4())
        build_briefing.delay(str(subject.tenant_id), str(subject.user_id), job_id)
        return job_id

    async def record_feedback(self, subject: Subject, item_id: UUID, verdict: str, note: str | None):
        # Persist feedback → trains ranking + memory; 'acted_on' is the WARU North-Star event.
        pass  # SCAFFOLD

    @staticmethod
    def rank(items: list[dict]) -> list[dict]:
        scored = [(i["expected_value_norm"] * i["confidence"] * i["relevance"], i) for i in items]
        return [i for s, i in sorted(scored, key=lambda x: x[0], reverse=True)
                if i["confidence"] >= MIN_CONFIDENCE]

    async def _latest(self, subject: Subject) -> dict | None:
        return None   # SCAFFOLD: select latest briefing (+items) for user, RLS-scoped

    async def _value_summary(self, subject: Subject) -> dict:
        return {"time_saved_min": 0, "money_saved_usd": 0, "acted": 0}
