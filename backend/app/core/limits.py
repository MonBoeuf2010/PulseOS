"""AI usage entitlements & spend caps (launch hardening, roadmap Step 5.4).

Two independent guards stop one abusive user — or one runaway day — from
draining the Anthropic budget:

1. Per-user daily call cap (free vs premium tier).
2. A global daily USD spend kill-switch across all users.

Both are backed by the existing `usage_events` table (no Redis dependency), so
they work identically in dev and prod. Call `enforce_ai_quota(...)` BEFORE an AI
call and `record_ai_usage(...)` AFTER it with the realized cost.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import Float, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import Subscription, UsageEvent

settings = get_settings()

AI_KINDS = ("chat", "council")  # usage_events.kind values that count toward AI quota


def _today_start() -> datetime:
    return datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)


async def is_premium(session: AsyncSession, user_id: UUID) -> bool:
    sub = (await session.execute(
        select(Subscription).where(Subscription.user_id == user_id))).scalar_one_or_none()
    return bool(sub and sub.status == "active")


async def enforce_ai_quota(session: AsyncSession, *, user_id: UUID, premium: bool) -> None:
    """Raise 429 (per-user cap) or 503 (global spend cap) before an AI call."""
    start = _today_start()

    # Global daily spend kill-switch — sum realized cost across everyone today.
    spent = (await session.execute(
        select(func.coalesce(func.sum(cast(UsageEvent.value["cost_usd"].astext, Float)), 0.0))
        .where(UsageEvent.kind.in_(AI_KINDS), UsageEvent.created_at >= start))).scalar_one()
    if float(spent or 0.0) >= settings.global_daily_ai_spend_cap_usd:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE,
                            "AI temporarily unavailable (daily budget reached) — try again tomorrow")

    # Per-user daily call cap.
    used = (await session.execute(
        select(func.count(UsageEvent.id))
        .where(UsageEvent.user_id == user_id, UsageEvent.kind.in_(AI_KINDS),
               UsageEvent.created_at >= start))).scalar_one()
    cap = settings.premium_daily_ai_limit if premium else settings.free_daily_ai_limit
    if int(used or 0) >= cap:
        detail = (f"daily AI limit reached ({cap}/day). "
                  + ("Try again tomorrow." if premium
                     else "Upgrade to Pro for a much higher limit: POST /api/v1/billing/checkout"))
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, detail)


async def record_ai_usage(session: AsyncSession, *, tenant_id: UUID, user_id: UUID,
                          kind: str, cost_usd: float = 0.0) -> None:
    """Record one AI call so future quota checks see it. kind ∈ {chat, council}."""
    session.add(UsageEvent(tenant_id=tenant_id, user_id=user_id, kind=kind,
                           value={"cost_usd": float(cost_usd)}))
    await session.flush()
