"""Data access for the Opportunity Engine (Phase 2.6)."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Opportunity, UsageEvent


class OpportunityRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self, tenant_id: UUID, user_id: UUID, status: str | None,
                   domain: str | None, limit: int = 50) -> list[Opportunity]:
        stmt = (select(Opportunity)
                .where(Opportunity.tenant_id == tenant_id, Opportunity.user_id == user_id)
                .order_by(desc(Opportunity.confidence)).limit(limit))
        if status:
            stmt = stmt.where(Opportunity.status == status)
        if domain:
            stmt = stmt.where(Opportunity.domain == domain)
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def get(self, tenant_id: UUID, user_id: UUID, opp_id: UUID) -> Opportunity | None:
        res = await self.session.execute(
            select(Opportunity).where(
                Opportunity.id == opp_id, Opportunity.tenant_id == tenant_id,
                Opportunity.user_id == user_id))
        return res.scalar_one_or_none()

    async def create(self, *, tenant_id: UUID, user_id: UUID, title: str, domain: str,
                     rationale: str | None, confidence: float,
                     expected_value: float | None) -> Opportunity:
        opp = Opportunity(tenant_id=tenant_id, user_id=user_id, title=title, domain=domain,
                          rationale=rationale, confidence=confidence,
                          expected_value=expected_value, status="open")
        self.session.add(opp)
        await self.session.flush()
        return opp

    async def mark_acted(self, opp: Opportunity) -> None:
        """North-Star WARU event: the user actually acted on the opportunity."""
        opp.status = "acted"
        self.session.add(UsageEvent(tenant_id=opp.tenant_id, user_id=opp.user_id,
                                    kind="opportunity_acted", target_id=opp.id))
