"""Opportunity Engine endpoints (Phase 2.6)."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_subject, db
from app.core.security import Subject
from app.repositories.opportunities import OpportunityRepository
from app.schemas import OpportunityListOut, OpportunityOut

router = APIRouter()


@router.get("", response_model=OpportunityListOut)
async def list_opps(domain: str | None = None, status_filter: str = "open",
                    subject: Subject = Depends(current_subject),
                    session: AsyncSession = Depends(db)):
    rows = await OpportunityRepository(session).list(
        subject.tenant_id, subject.user_id, status=status_filter, domain=domain)
    return OpportunityListOut(items=[OpportunityOut.model_validate(r) for r in rows])


@router.post("/{opp_id}:act", status_code=status.HTTP_204_NO_CONTENT)
async def act(opp_id: UUID, subject: Subject = Depends(current_subject),
              session: AsyncSession = Depends(db)):
    # Records the North-Star WARU event (usage_events: opportunity_acted).
    repo = OpportunityRepository(session)
    opp = await repo.get(subject.tenant_id, subject.user_id, opp_id)
    if opp is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "opportunity not found")
    await repo.mark_acted(opp)
