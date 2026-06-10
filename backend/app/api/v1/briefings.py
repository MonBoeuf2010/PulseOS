"""Briefing & Dashboard endpoints (Phase 2.6 contract)."""
from uuid import UUID

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_subject, db, require
from app.core.security import Subject
from app.services.briefing_service import BriefingService

router = APIRouter()


class FeedbackIn(BaseModel):
    verdict: str   # useful | not_useful | wrong | acted_on
    note: str | None = None


@router.get("/dashboard")
async def dashboard(subject: Subject = Depends(current_subject), session: AsyncSession = Depends(db)):
    return await BriefingService(session).dashboard(subject)


@router.get("/briefings")
async def list_briefings(cursor: str | None = None, limit: int = 20,
                         subject: Subject = Depends(current_subject),
                         session: AsyncSession = Depends(db)):
    return await BriefingService(session).list(subject, cursor, min(limit, 100))


@router.post("/briefings:generate", status_code=status.HTTP_202_ACCEPTED)
async def generate(subject: Subject = Depends(require("briefing:read")),
                   session: AsyncSession = Depends(db)):
    job_id = await BriefingService(session).enqueue_generate(subject)
    return {"job_id": job_id, "status": "queued"}


@router.get("/briefings/{briefing_id}")
async def get_briefing(briefing_id: UUID, subject: Subject = Depends(current_subject),
                       session: AsyncSession = Depends(db)):
    return await BriefingService(session).get(subject, briefing_id)


@router.post("/briefing-items/{item_id}/feedback", status_code=status.HTTP_204_NO_CONTENT)
async def feedback(item_id: UUID, body: FeedbackIn,
                   subject: Subject = Depends(current_subject),
                   session: AsyncSession = Depends(db)):
    await BriefingService(session).record_feedback(subject, item_id, body.verdict, body.note)
