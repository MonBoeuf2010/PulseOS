"""Data access for the AI Memory store (Phase 1 transparency / GDPR)."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import MemoryItem


class MemoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self, tenant_id: UUID, user_id: UUID) -> list[MemoryItem]:
        res = await self.session.execute(
            select(MemoryItem)
            .where(MemoryItem.tenant_id == tenant_id, MemoryItem.user_id == user_id,
                   MemoryItem.deleted_at.is_(None))
            .order_by(desc(MemoryItem.confidence)))
        return list(res.scalars().all())

    async def add(self, *, tenant_id: UUID, user_id: UUID, kind: str, content: str,
                  embedding: list[float] | None = None) -> MemoryItem:
        item = MemoryItem(tenant_id=tenant_id, user_id=user_id, kind=kind,
                          content=content, embedding=embedding)
        self.session.add(item)
        await self.session.flush()
        return item

    async def soft_delete(self, tenant_id: UUID, user_id: UUID, item_id: UUID) -> bool:
        """GDPR deletion: tombstone now; a worker propagates to embeddings + search index."""
        res = await self.session.execute(
            select(MemoryItem).where(
                MemoryItem.id == item_id, MemoryItem.tenant_id == tenant_id,
                MemoryItem.user_id == user_id))
        item = res.scalar_one_or_none()
        if item is None:
            return False
        item.deleted_at = datetime.now(timezone.utc)
        return True
