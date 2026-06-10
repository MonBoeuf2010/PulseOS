"""Persistence for auditable Council reports (Phase 6)."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.council.orchestrator import CouncilReport as CouncilReportDC
from app.models import CouncilReport


class CouncilRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, tenant_id: UUID, subject: str, domain: str,
                   report: CouncilReportDC) -> CouncilReport:
        row = CouncilReport(
            tenant_id=tenant_id, subject=subject, domain=domain, tier=report.tier,
            executive_summary=report.executive_summary, consensus=report.consensus,
            confidence=report.confidence, dissent=report.dissent,
            recommended_actions=report.recommended_actions,
            estimated_impact=report.estimated_impact, cost_of_inaction=report.cost_of_inaction,
            evidence=report.evidence, agent_traces=report.agent_traces,
            cost_usd=report.cost_usd, latency_ms=report.latency_ms)
        self.session.add(row)
        await self.session.flush()
        return row

    async def get(self, tenant_id: UUID, report_id: UUID) -> CouncilReport | None:
        res = await self.session.execute(
            select(CouncilReport).where(
                CouncilReport.id == report_id, CouncilReport.tenant_id == tenant_id))
        return res.scalar_one_or_none()
