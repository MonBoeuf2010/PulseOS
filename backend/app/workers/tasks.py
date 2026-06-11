"""Celery tasks — idempotent consumers (dedupe on event_id / external_id).

Sync Celery task bodies delegate to async helpers via asyncio.run. The async
helpers (`*_sync`) are also importable directly so the API can run them inline in
dev when no broker is configured (see BriefingService.enqueue_generate).
"""
from __future__ import annotations

import asyncio
from uuid import UUID

from sqlalchemy import desc, select

from app.core.db import tenant_session
from app.council.ai_gateway import AIGateway
from app.council.orchestrator import CouncilEngine, CouncilInput
from app.repositories.briefings import BriefingRepository
from app.repositories.council import CouncilRepository
from app.workers.celery_app import celery_app

# Default candidate seeds so a brand-new tenant gets a non-empty, useful first briefing
# even before any connectors are configured (the "win the wedge" cold-start, Phase 1).
_COLD_START_SUBJECTS = [
    ("economy", "Interest-rate trajectory and its effect on your cash runway"),
    ("career", "Highest-leverage skill to compound this quarter"),
    ("market", "An emerging trend in your domain worth a small early bet"),
]
MAX_ITEMS = 8


# ---------------------------------------------------------------- ingestion
async def enrich_signal_sync(raw: dict) -> dict:
    """Normalize → dedupe (external_id) → enrich → persist Signal. Embedding/index async."""
    from app.models import Signal
    async with tenant_session(None) as session:
        ext = raw.get("external_id")
        if ext:
            existing = await session.execute(
                select(Signal.id).where(Signal.external_id == ext))
            if existing.scalar_one_or_none():
                return {"ok": True, "deduped": True}
        sig = Signal(
            source=raw.get("source", "unknown"), external_id=ext,
            domain=raw.get("domain", "general"), title=raw.get("title", "(untitled)"),
            snippet=raw.get("snippet"), url=raw.get("url"),
            reliability=raw.get("reliability", 0.5), impact=raw.get("impact", 0.5),
            entities=raw.get("entities", []))
        session.add(sig)
        await session.flush()
        return {"ok": True, "signal_id": str(sig.id)}


# ---------------------------------------------------------------- council
async def run_council_sync(payload: dict) -> dict:
    engine = CouncilEngine(AIGateway(), gate_threshold=0.6)
    ci = CouncilInput(subject=payload["subject"], domain=payload.get("domain", "general"),
                      evidence=payload.get("evidence", []),
                      estimated_value=payload.get("value", 0.5),
                      uncertainty=payload.get("uncertainty", 0.5),
                      user_relevance=payload.get("relevance", 0.5))
    report = await engine.run(ci)
    return {"tier": report.tier, "confidence": report.confidence, "cost_usd": report.cost_usd}


# ---------------------------------------------------------------- briefing
async def build_briefing_sync(tenant_id: UUID, user_id: UUID, job_id: str) -> dict:
    """Gather signals → gate council per candidate → rank → persist briefing.

    Ranking is precision-first: expected_value × confidence, dropping anything below
    the council's calibrated confidence floor.
    """
    from app.models import Signal
    engine = CouncilEngine(AIGateway(), gate_threshold=0.6)

    async with tenant_session(tenant_id) as session:
        # Pull the freshest, highest-impact signals relevant to this tenant or global.
        res = await session.execute(
            select(Signal).order_by(desc(Signal.impact), desc(Signal.created_at)).limit(MAX_ITEMS))
        signals = list(res.scalars().all())

        candidates: list[tuple[str, str, list[dict]]] = []
        if signals:
            for s in signals:
                ev = [{"id": str(s.id), "source": s.source,
                       "reliability": float(s.reliability), "snippet": s.snippet or s.title}]
                candidates.append((s.domain, s.title, ev))
        else:
            candidates = [(d, subj, []) for d, subj in _COLD_START_SUBJECTS]

        council_repo = CouncilRepository(session)
        items: list[dict] = []
        for domain, subject, evidence in candidates:
            # Briefing candidates are pre-filtered as high-value → run the full council.
            report = await engine.run(CouncilInput(
                subject=subject, domain=domain, evidence=evidence,
                estimated_value=0.9, uncertainty=0.8, user_relevance=0.85))
            saved = await council_repo.save(tenant_id, subject, domain, report)
            expected_value = (report.estimated_impact
                              if report.estimated_impact is not None else 1000.0)
            items.append({
                "category": domain,
                "title": subject,
                "rationale": report.executive_summary or report.consensus or "",
                "confidence": float(report.confidence),
                "expected_value": float(expected_value),
                "cost_of_inaction": report.cost_of_inaction,
                "evidence_refs": [],
                "council_report_id": saved.id,
                "_score": float(report.confidence) * float(expected_value),
            })

        # Precision-first ranking: drop below the calibrated floor, then sort by EV×confidence.
        from app.services.briefing_service import MIN_CONFIDENCE
        items = sorted([i for i in items if i["confidence"] >= MIN_CONFIDENCE],
                       key=lambda i: i["_score"], reverse=True)
        for i in items:
            i.pop("_score", None)

        summary = (f"{len(items)} high-value actions surfaced from "
                   f"{len(signals) or len(candidates)} signals.")
        briefing = await BriefingRepository(session).create(
            tenant_id=tenant_id, user_id=user_id, summary=summary, items=items)
        return {"job_id": job_id, "status": "done", "briefing_id": str(briefing.id),
                "items": len(items)}


# ---------------------------------------------------------------- celery wrappers
@celery_app.task(bind=True, name="app.workers.tasks.enrich_signal")
def enrich_signal(self, raw: dict):
    return asyncio.run(enrich_signal_sync(raw))


@celery_app.task(bind=True, name="app.workers.tasks.run_council")
def run_council(self, payload: dict):
    return asyncio.run(run_council_sync(payload))


@celery_app.task(bind=True, name="app.workers.tasks.build_briefing")
def build_briefing(self, tenant_id: str, user_id: str, job_id: str):
    return asyncio.run(build_briefing_sync(UUID(tenant_id), UUID(user_id), job_id))


async def schedule_briefings_sync() -> dict:
    """Fan out one build_briefing per active user (the daily automation loop)."""
    import uuid as uuid_lib
    from app.models import Membership

    async with tenant_session(None) as session:
        res = await session.execute(select(Membership))
        memberships = list(res.scalars().all())

    count = 0
    for m in memberships:
        job_id = str(uuid_lib.uuid4())
        try:
            # Through the broker when workers are running...
            build_briefing.delay(str(m.tenant_id), str(m.user_id), job_id)
        except Exception:
            # ...inline fallback in dev with no broker.
            await build_briefing_sync(m.tenant_id, m.user_id, job_id)
        count += 1
    return {"scheduled": count}


@celery_app.task(name="app.workers.tasks.schedule_briefings")
def schedule_briefings():
    return asyncio.run(schedule_briefings_sync())


async def moderate_post_sync(post_id: str) -> dict:
    """AI first-pass moderation for new feed posts (BLOCK spam/abuse)."""
    from uuid import UUID as _UUID
    from app.models import Post
    gateway = AIGateway()
    async with tenant_session(None) as session:
        post = await session.get(Post, _UUID(post_id))
        if post is None:
            return {"ok": False}
        verdict = await gateway.complete_fast(
            system=("You are a content moderator. Reply with exactly one word: "
                    "ALLOW, REVIEW, or BLOCK. BLOCK only spam, scams, doxxing, "
                    "or harassment. REVIEW borderline cases."),
            prompt=f"Title: {post.title}\n\nBody: {post.body[:2000]}")
        decision = (verdict or "REVIEW").strip().upper()
        if "BLOCK" in decision:
            await session.delete(post)
            return {"ok": True, "action": "blocked"}
        return {"ok": True, "action": "allowed"}


@celery_app.task(name="app.workers.tasks.moderate_post")
def moderate_post(post_id: str):
    return asyncio.run(moderate_post_sync(post_id))


async def ingest_rss_sync() -> dict:
    """Pull configured RSS feeds → enrich each entry into a Signal (deduped)."""
    from app.ingestion.connectors import pull_rss
    raws = pull_rss()
    ingested = 0
    for raw in raws:
        res = await enrich_signal_sync(raw)
        if res.get("ok") and not res.get("deduped"):
            ingested += 1
    return {"pulled": len(raws), "ingested": ingested}


@celery_app.task(name="app.workers.tasks.ingest_rss")
def ingest_rss():
    return asyncio.run(ingest_rss_sync())


@celery_app.task(name="app.workers.tasks.notify")
def notify(payload: dict):
    return {"ok": True}


@celery_app.task(name="app.workers.tasks.retention_sweep")
def retention_sweep():
    # delete/crypto-shred past retention; purge tombstoned memory from index (Phase 3 §8)
    return {"swept": 0}


@celery_app.task(name="app.workers.tasks.recompute_calibration")
def recompute_calibration():
    # refit per-domain calibration maps from council_outcomes (Phase 6)
    return {"updated": 0}
