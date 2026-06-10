"""Seed a demo tenant, user, signals, and a first briefing so the dashboard is alive.

Usage (with the datastores up — see infra/docker-compose.yml):
    python -m scripts.seed
Idempotent on the demo email: re-running reuses the existing user/tenant.

Demo login:  demo@pulseos.com / pulsedemo123
"""
from __future__ import annotations

import asyncio

from app.core.bootstrap import init_db
from app.core.db import tenant_session
from app.core.security import hash_password
from app.repositories.opportunities import OpportunityRepository
from app.repositories.users import UserRepository
from app.workers.tasks import build_briefing_sync

DEMO_EMAIL = "demo@pulseos.com"
DEMO_PASSWORD = "pulsedemo123"

SEED_SIGNALS = [
    dict(source="reuters", external_id="seed-rates-1", domain="economy",
         title="Central bank signals a pause in rate hikes", impact=0.8, reliability=0.85,
         snippet="Policymakers hint the tightening cycle may be near its end."),
    dict(source="arxiv", external_id="seed-ai-1", domain="market",
         title="Open-weight models close the gap with frontier labs", impact=0.75, reliability=0.7,
         snippet="A new release matches last year's frontier on key benchmarks at a fraction of cost."),
    dict(source="sec-edgar", external_id="seed-fin-1", domain="career",
         title="Hiring surge in applied-AI roles across mid-market firms", impact=0.7, reliability=0.8,
         snippet="Job postings mentioning practical AI deployment up sharply quarter over quarter."),
]


async def main() -> None:
    await init_db()

    # Identity (no tenant RLS context).
    async with tenant_session(None) as session:
        users = UserRepository(session)
        user = await users.get_by_email(DEMO_EMAIL)
        if user is None:
            user, tenant, _ = await users.create_user_with_tenant(
                email=DEMO_EMAIL, password_hash=hash_password(DEMO_PASSWORD),
                display_name="Demo Operator", tenant_name="Demo Workspace")
            tenant_id, user_id = tenant.id, user.id
            print(f"created demo user {DEMO_EMAIL} (tenant {tenant_id})")
        else:
            membership = (await users.memberships(user.id))[0]
            tenant_id, user_id = membership.tenant_id, user.id
            print(f"reusing demo user {DEMO_EMAIL} (tenant {tenant_id})")

    # Signals (global) + opportunities + first briefing (tenant-scoped).
    from app.models import Signal
    async with tenant_session(tenant_id) as session:
        for raw in SEED_SIGNALS:
            from sqlalchemy import select
            exists = await session.scalar(select(Signal.id).where(Signal.external_id == raw["external_id"]))
            if not exists:
                session.add(Signal(**raw))
        opps = OpportunityRepository(session)
        await opps.create(tenant_id=tenant_id, user_id=user_id, domain="market",
                          title="Pilot an open-weight model for your highest-volume workflow",
                          rationale="Cost/perf crossover makes a low-risk pilot attractive now.",
                          confidence=0.74, expected_value=8000)

    job = await build_briefing_sync(tenant_id, user_id, job_id="seed")
    print(f"built briefing: {job}")
    print(f"\nLogin at the web app with:\n  email:    {DEMO_EMAIL}\n  password: {DEMO_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(main())
