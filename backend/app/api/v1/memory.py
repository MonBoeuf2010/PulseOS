"""AI Memory endpoints — inspect/edit/delete (Phase 1 transparency, GDPR)."""
from uuid import UUID
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from app.api.deps import current_subject
from app.core.security import Subject

router = APIRouter()


class MemoryIn(BaseModel):
    kind: str   # interest | goal | profession | preference | episodic
    content: str


@router.get("")
async def list_memory(subject: Subject = Depends(current_subject)):
    return []   # SCAFFOLD: select memory_items for user (RLS-scoped)


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_memory(body: MemoryIn, subject: Subject = Depends(current_subject)):
    return {"id": "...", **body.model_dump()}


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_memory(item_id: UUID, subject: Subject = Depends(current_subject)):
    # MUST propagate deletion to embeddings + search index (Phase 3 deletion workflow).
    return
