"""Universal search — tenant-filtered server-side (Phase 2.7C).

The tenant_id filter is injected in the repository and cannot be removed by the client.
Hybrid BM25 + vector + RRF over OpenSearch is the production path; this endpoint uses
the Postgres lexical fallback so search works on the core stack.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_subject, db
from app.core.security import Subject
from app.repositories.search import SearchRepository

router = APIRouter()


@router.get("")
async def search(q: str, types: str | None = None,
                 subject: Subject = Depends(current_subject),
                 session: AsyncSession = Depends(db)):
    type_set = {t.strip() for t in types.split(",")} if types else None
    return await SearchRepository(session).search(
        tenant_id=subject.tenant_id, user_id=subject.user_id, q=q, types=type_set)
