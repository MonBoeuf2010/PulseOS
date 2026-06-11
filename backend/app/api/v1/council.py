"""Council endpoints: read auditable reports; request ad-hoc analysis (Pro+)."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_subject, db
from app.api.v1.billing import require_premium
from app.core.limits import enforce_ai_quota, record_ai_usage
from app.core.security import Subject
from app.council.ai_gateway import AIGateway
from app.council.orchestrator import CouncilEngine, CouncilInput
from app.repositories.council import CouncilRepository
from app.schemas import AnalyzeIn

router = APIRouter()


@router.get("/reports/{report_id}")
async def get_report(report_id: UUID, subject: Subject = Depends(current_subject),
                     session: AsyncSession = Depends(db)):
    row = await CouncilRepository(session).get(subject.tenant_id, report_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "report not found")
    return {
        "id": str(row.id), "subject": row.subject, "domain": row.domain, "tier": row.tier,
        "executive_summary": row.executive_summary, "consensus": row.consensus,
        "confidence": float(row.confidence), "dissent": row.dissent,
        "recommended_actions": row.recommended_actions,
        "estimated_impact": float(row.estimated_impact) if row.estimated_impact is not None else None,
        "cost_of_inaction": row.cost_of_inaction, "evidence": row.evidence,
        "agent_traces": row.agent_traces, "cost_usd": float(row.cost_usd),
        "latency_ms": row.latency_ms,
    }


@router.post("/analyze", status_code=status.HTTP_200_OK)
async def analyze(body: AnalyzeIn, subject: Subject = Depends(require_premium),
                  session: AsyncSession = Depends(db)):
    # Council deep-dives are the paid Pro action (require_premium gates this).
    # Premium users still get a daily call cap + the global spend kill-switch.
    await enforce_ai_quota(session, user_id=subject.user_id, premium=True)
    engine = CouncilEngine(AIGateway(), gate_threshold=0.6)
    # Ad-hoc analyses are explicitly user-requested (a Pro action) → always run the full
    # council. Force the tier rather than relying on the value×uncertainty×relevance gate.
    force_full = body.tier == "full"
    report = await engine.run(CouncilInput(
        subject=body.subject, domain=body.domain,
        estimated_value=0.95 if force_full else 0.6,
        uncertainty=0.85 if force_full else 0.5,
        user_relevance=0.95 if force_full else 0.6))
    saved = await CouncilRepository(session).save(subject.tenant_id, body.subject, body.domain, report)
    await record_ai_usage(session, tenant_id=subject.tenant_id, user_id=subject.user_id,
                          kind="council", cost_usd=float(report.cost_usd or 0.0))
    return {"status": "done", "report": {"id": str(saved.id), **report.__dict__}}
