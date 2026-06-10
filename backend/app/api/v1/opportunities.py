"""Opportunity Engine endpoints (Phase 2.6)."""
from uuid import UUID
from fastapi import APIRouter, Depends, status
from app.api.deps import current_subject
from app.core.security import Subject

router = APIRouter()


@router.get("")
async def list_opps(domain: str | None = None, status_filter: str = "open",
                    subject: Subject = Depends(current_subject)):
    return {"items": [], "next_cursor": None}   # SCAFFOLD: query opportunities (RLS-scoped)


@router.post("/{opp_id}:act", status_code=status.HTTP_204_NO_CONTENT)
async def act(opp_id: UUID, subject: Subject = Depends(current_subject)):
    # Records the North-Star WARU event (usage_events: opportunity_acted).
    return
