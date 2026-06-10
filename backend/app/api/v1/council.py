"""Council endpoints: read auditable reports; request ad-hoc analysis (Pro+)."""
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.api.deps import current_subject, require
from app.core.security import Subject
from app.council.ai_gateway import AIGateway
from app.council.orchestrator import CouncilEngine, CouncilInput

router = APIRouter()


class AnalyzeIn(BaseModel):
    subject: str
    domain: str = "general"
    tier: str = "full"


@router.get("/reports/{report_id}")
async def get_report(report_id: UUID, subject: Subject = Depends(current_subject)):
    # SCAFFOLD: load council_report + agent_traces (tenant-scoped via RLS) and return.
    return {"id": str(report_id), "note": "load from council_reports (RLS-scoped)"}


@router.post("/analyze", status_code=status.HTTP_202_ACCEPTED)
async def analyze(body: AnalyzeIn, subject: Subject = Depends(require("opportunity:read"))):
    engine = CouncilEngine(AIGateway())
    report = await engine.run(CouncilInput(subject=body.subject, domain=body.domain,
                                           estimated_value=0.8, uncertainty=0.7, user_relevance=0.9))
    return {"status": "done", "report": report.__dict__}
