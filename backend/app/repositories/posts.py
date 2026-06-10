"""Data access for the community feed. Posts are a cross-tenant community surface:
the feed is intentionally NOT tenant-filtered (in prod a permissive RLS read policy
backs this). Reactions are deduped per (post, user)."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Post, PostReaction


class PostRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, author_user_id: UUID, author_name: str, tenant_id: UUID,
                     category: str, title: str, body: str,
                     confidence: float | None) -> Post:
        post = Post(author_user_id=author_user_id, author_name=author_name, tenant_id=tenant_id,
                    category=category, title=title, body=body, confidence=confidence)
        self.session.add(post)
        await self.session.flush()
        return post

    async def feed(self, limit: int = 50) -> list[Post]:
        res = await self.session.execute(
            select(Post).order_by(desc(Post.created_at)).limit(limit))
        return list(res.scalars().all())

    async def get(self, post_id: UUID) -> Post | None:
        return await self.session.get(Post, post_id)

    async def reacted_ids(self, user_id: UUID, post_ids: list[UUID]) -> set[UUID]:
        if not post_ids:
            return set()
        res = await self.session.execute(
            select(PostReaction.post_id).where(
                PostReaction.user_id == user_id, PostReaction.post_id.in_(post_ids)))
        return set(res.scalars().all())

    async def toggle_reaction(self, *, post: Post, user_id: UUID,
                              kind: str = "insightful") -> bool:
        """Return True if reaction is now ON, False if it was toggled off."""
        res = await self.session.execute(
            select(PostReaction).where(
                PostReaction.post_id == post.id, PostReaction.user_id == user_id))
        existing = res.scalar_one_or_none()
        if existing:
            await self.session.delete(existing)
            post.reaction_count = max(0, post.reaction_count - 1)
            return False
        self.session.add(PostReaction(post_id=post.id, user_id=user_id, kind=kind))
        post.reaction_count += 1
        return True
