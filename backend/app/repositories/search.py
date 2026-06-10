"""Universal search (Phase 2.7C).

Production runs hybrid BM25 + vector over OpenSearch with RRF fusion and a personalized
rerank. This is the Postgres fallback: a tenant-scoped lexical search over signals and
memory so the feature works on the core stack alone. The mandatory tenant filter is
applied server-side and cannot be removed by the client.
"""
from __future__ import annotations

import time
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import MemoryItem, Signal


class SearchRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search(self, *, tenant_id: UUID, user_id: UUID, q: str,
                     types: set[str] | None, limit: int = 25) -> dict:
        t0 = time.monotonic()
        like = f"%{q.strip()}%"
        results: list[dict] = []

        if not types or "signal" in types:
            res = await self.session.execute(
                select(Signal)
                .where(or_(Signal.tenant_id == tenant_id, Signal.tenant_id.is_(None)),
                       or_(Signal.title.ilike(like), Signal.snippet.ilike(like)))
                .order_by(Signal.impact.desc()).limit(limit))
            for s in res.scalars().all():
                results.append({"type": "signal", "id": str(s.id), "title": s.title,
                                "snippet": s.snippet, "domain": s.domain, "source": s.source,
                                "score": float(s.impact)})

        if not types or "memory" in types:
            res = await self.session.execute(
                select(MemoryItem)
                .where(MemoryItem.tenant_id == tenant_id, MemoryItem.user_id == user_id,
                       MemoryItem.deleted_at.is_(None), MemoryItem.content.ilike(like))
                .limit(limit))
            for m in res.scalars().all():
                results.append({"type": "memory", "id": str(m.id), "title": m.kind,
                                "snippet": m.content, "score": float(m.confidence)})

        results.sort(key=lambda r: r["score"], reverse=True)
        return {"results": results[:limit], "next_cursor": None,
                "took_ms": int((time.monotonic() - t0) * 1000)}
