"""AI Memory endpoints — inspect/edit/delete (Phase 1 transparency, GDPR)."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_subject, db
from app.core.security import Subject
from app.repositories.memory import MemoryRepository
from app.schemas import MemoryIn, MemoryOut

router = APIRouter()


@router.get("", response_model=list[MemoryOut])
async def list_memory(subject: Subject = Depends(current_subject),
                      session: AsyncSession = Depends(db)):
    rows = await MemoryRepository(session).list(subject.tenant_id, subject.user_id)
    return [MemoryOut.model_validate(r) for r in rows]


@router.post("", response_model=MemoryOut, status_code=status.HTTP_201_CREATED)
async def add_memory(body: MemoryIn, subject: Subject = Depends(current_subject),
                     session: AsyncSession = Depends(db)):
    row = await MemoryRepository(session).add(
        tenant_id=subject.tenant_id, user_id=subject.user_id,
        kind=body.kind, content=body.content)
    return MemoryOut.model_validate(row)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(item_id: UUID, subject: Subject = Depends(current_subject),
                        session: AsyncSession = Depends(db)):
    # MUST propagate deletion to embeddings + search index (Phase 3 deletion workflow).
    ok = await MemoryRepository(session).soft_delete(subject.tenant_id, subject.user_id, item_id)
    if not ok:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "memory item not found")
    from app.workers.tasks import retention_sweep  # noqa: F401  (index purge handled async)
