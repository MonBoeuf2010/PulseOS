"""Data access for briefings + feedback. All queries are RLS-scoped: the session
already carries `app.tenant_id`, so we additionally filter by user_id for ownership.
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import desc, func, select
from sqlalchemy.orm import selectinload

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Briefing, BriefingItem, Feedback, UsageEvent


class BriefingRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def latest(self, tenant_id: UUID, user_id: UUID) -> Briefing | None:
        res = await self.session.execute(
            select(Briefing)
            .where(Briefing.tenant_id == tenant_id, Briefing.user_id == user_id)
            .order_by(desc(Briefing.generated_at))
            .options(selectinload(Briefing.items))
            .limit(1))
        return res.scalar_one_or_none()

    async def get(self, tenant_id: UUID, user_id: UUID, briefing_id: UUID) -> Briefing | None:
        res = await self.session.execute(
            select(Briefing)
            .where(Briefing.id == briefing_id, Briefing.tenant_id == tenant_id,
                   Briefing.user_id == user_id)
            .options(selectinload(Briefing.items)))
        return res.scalar_one_or_none()

    async def list(self, tenant_id: UUID, user_id: UUID, limit: int) -> list[Briefing]:
        res = await self.session.execute(
            select(Briefing)
            .where(Briefing.tenant_id == tenant_id, Briefing.user_id == user_id)
            .order_by(desc(Briefing.generated_at))
            .options(selectinload(Briefing.items))
            .limit(limit))
        return list(res.scalars().all())

    async def create(self, *, tenant_id: UUID, user_id: UUID, summary: str | None,
                     items: list[dict]) -> Briefing:
        briefing = Briefing(tenant_id=tenant_id, user_id=user_id, period="daily", summary=summary)
        self.session.add(briefing)
        await self.session.flush()
        for rank, it in enumerate(items):
            self.session.add(BriefingItem(
                briefing_id=briefing.id, tenant_id=tenant_id, rank=rank,
                category=it.get("category", "general"), title=it["title"],
                rationale=it.get("rationale", ""), confidence=it.get("confidence", 0.6),
                expected_value=it.get("expected_value"),
                cost_of_inaction=it.get("cost_of_inaction"),
                evidence_refs=it.get("evidence_refs", []),
                council_report_id=it.get("council_report_id")))
        await self.session.flush()
        await self.session.refresh(briefing, ["items"])
        return briefing

    async def get_item(self, tenant_id: UUID, item_id: UUID) -> BriefingItem | None:
        res = await self.session.execute(
            select(BriefingItem).where(
                BriefingItem.id == item_id, BriefingItem.tenant_id == tenant_id))
        return res.scalar_one_or_none()

    async def record_feedback(self, *, tenant_id: UUID, user_id: UUID, item_id: UUID,
                              verdict: str, note: str | None) -> None:
        self.session.add(Feedback(tenant_id=tenant_id, user_id=user_id,
                                  briefing_item_id=item_id, verdict=verdict, note=note))
        # 'acted_on' is the North-Star WARU event — also land it on the usage stream.
        if verdict == "acted_on":
            self.session.add(UsageEvent(tenant_id=tenant_id, user_id=user_id,
                                        kind="opportunity_acted", target_id=item_id))

    async def value_summary(self, tenant_id: UUID, user_id: UUID) -> dict:
        """Aggregate realized value for the dashboard hero tiles."""
        acted = await self.session.scalar(
            select(func.count()).select_from(UsageEvent).where(
                UsageEvent.tenant_id == tenant_id, UsageEvent.user_id == user_id,
                UsageEvent.kind == "opportunity_acted"))
        # Time saved proxy: each surfaced+kept item saves an estimated research block.
        items = await self.session.scalar(
            select(func.count()).select_from(BriefingItem).where(
                BriefingItem.tenant_id == tenant_id))
        money = await self.session.scalar(
            select(func.coalesce(func.sum(BriefingItem.expected_value), 0)).select_from(BriefingItem)
            .join(Feedback, Feedback.briefing_item_id == BriefingItem.id)
            .where(BriefingItem.tenant_id == tenant_id, Feedback.verdict == "acted_on"))
        return {"time_saved_min": int((items or 0) * 12), "money_saved_usd": float(money or 0),
                "acted": int(acted or 0)}
