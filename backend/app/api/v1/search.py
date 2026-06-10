"""Universal search — hybrid BM25 + vector, tenant-filtered server-side (Phase 2.7C)."""
from fastapi import APIRouter, Depends
from app.api.deps import current_subject
from app.core.security import Subject

router = APIRouter()


@router.get("")
async def search(q: str, types: str | None = None,
                 subject: Subject = Depends(current_subject)):
    # SCAFFOLD: parallel multi-index query, MANDATORY tenant_id + visibility filter
    # injected server-side (clients cannot remove it), RRF fusion, personalized rerank.
    return {"results": [], "next_cursor": None, "took_ms": 0}
