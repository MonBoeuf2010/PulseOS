"""Celery tasks — idempotent consumers (dedupe on event_id). SCAFFOLD bodies."""
import asyncio

from app.workers.celery_app import celery_app
from app.council.ai_gateway import AIGateway
from app.council.orchestrator import CouncilEngine, CouncilInput


@celery_app.task(bind=True, name="app.workers.tasks.enrich_signal")
def enrich_signal(self, raw: dict):
    # normalize → dedupe → enrich → embed/index; emit signal.indexed
    return {"ok": True}


@celery_app.task(bind=True, name="app.workers.tasks.run_council")
def run_council(self, payload: dict):
    engine = CouncilEngine(AIGateway(), gate_threshold=0.6)
    ci = CouncilInput(subject=payload["subject"], domain=payload.get("domain", "general"),
                      evidence=payload.get("evidence", []),
                      estimated_value=payload.get("value", 0.5),
                      uncertainty=payload.get("uncertainty", 0.5),
                      user_relevance=payload.get("relevance", 0.5))
    report = asyncio.run(engine.run(ci))
    # persist council_report + agent_traces; emit council.completed
    return {"tier": report.tier, "confidence": report.confidence, "cost_usd": report.cost_usd}


@celery_app.task(bind=True, name="app.workers.tasks.build_briefing")
def build_briefing(self, tenant_id: str, user_id: str, job_id: str):
    # gather signals → gate council → rank → persist briefing; emit briefing.generated
    return {"job_id": job_id, "status": "done"}


@celery_app.task(name="app.workers.tasks.schedule_briefings")
def schedule_briefings():
    # fan out build_briefing per active user on their schedule
    return {"scheduled": 0}


@celery_app.task(name="app.workers.tasks.notify")
def notify(payload: dict):
    return {"ok": True}


@celery_app.task(name="app.workers.tasks.retention_sweep")
def retention_sweep():
    # delete/crypto-shred past retention (Phase 3 §8)
    return {"swept": 0}


@celery_app.task(name="app.workers.tasks.recompute_calibration")
def recompute_calibration():
    # refit per-domain calibration maps from council_outcomes (Phase 6)
    return {"updated": 0}
