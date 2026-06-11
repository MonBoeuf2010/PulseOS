"""Stripe subscription billing (Checkout + Webhooks + premium gating).

How money flows (the whole picture in 5 steps):
1. Frontend calls POST /billing/checkout → we create a Stripe Checkout Session
   and return its URL. The user pays ON STRIPE'S PAGE — card numbers never
   touch your server (this is what keeps you out of PCI-compliance scope).
2. Stripe redirects back to your /dashboard?upgraded=1.
3. Stripe calls POST /billing/webhook (server-to-server) with the signed event.
   THE WEBHOOK IS THE SOURCE OF TRUTH — never trust the redirect alone, since a
   user can fake a URL but cannot fake Stripe's signature.
4. We upsert a Subscription row (status=active) for the user.
5. Any premium endpoint adds `Depends(require_premium)` and is instantly gated.

Setup checklist (why each step):
- Stripe Dashboard → Products → create "PulseOS Pro" with a monthly and/or
  yearly recurring Price. Copy the price IDs into env (PRICE_* below).
- Developers → API keys → secret key → STRIPE_SECRET_KEY env.
- Developers → Webhooks → add endpoint https://yourdomain/api/v1/billing/webhook
  listening to: checkout.session.completed, customer.subscription.updated,
  customer.subscription.deleted → copy signing secret → STRIPE_WEBHOOK_SECRET.
- `pip install stripe` and add it to backend/pyproject.toml dependencies.
- Local testing: `stripe listen --forward-to localhost:8000/api/v1/billing/webhook`
  then pay with test card 4242 4242 4242 4242.

Wiring:
  - models/__init__.py: add Subscription model below + "Subscription" to __all__
  - router.py: api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
  - config.py already has stripe_secret_key / stripe_webhook_secret — add:
        stripe_price_monthly: str = ""
        stripe_price_yearly: str = ""
        frontend_base_url: str = "http://localhost:3000"
"""
from __future__ import annotations

import os

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_subject, db
from app.core.config import get_settings
from app.core.security import Subject

router = APIRouter()
settings = get_settings()
stripe.api_key = settings.stripe_secret_key


# ---------------------------------------------------------------- model
# Add to backend/app/models/__init__.py:
#
# class Subscription(Base):
#     __tablename__ = "subscriptions"
#     id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), unique=True, index=True)
#     stripe_customer_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
#     stripe_subscription_id: Mapped[str | None] = mapped_column(String, nullable=True)
#     plan: Mapped[str] = mapped_column(String, default="free")        # free|monthly|yearly
#     status: Mapped[str] = mapped_column(String, default="inactive")  # active|past_due|canceled|inactive
#     current_period_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
#     updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class CheckoutIn(BaseModel):
    plan: str = "monthly"  # "basic" | "monthly" (Pro) | "yearly" (Pro)


_PRICE_BY_PLAN = {
    "basic": "stripe_price_basic",
    "monthly": "stripe_price_monthly",
    "yearly": "stripe_price_yearly",
}


@router.post("/checkout")
async def create_checkout(body: CheckoutIn,
                          subject: Subject = Depends(current_subject),
                          session: AsyncSession = Depends(db)):
    if not settings.stripe_secret_key:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "billing not configured")
    price = getattr(settings, _PRICE_BY_PLAN.get(body.plan, ""), "")
    if not price:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "unknown plan")

    checkout = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price, "quantity": 1}],
        # client_reference_id is how the webhook maps payment → your user;
        # plan rides through metadata so the webhook can persist it.
        client_reference_id=str(subject.user_id),
        metadata={"plan": body.plan},
        success_url=f"{settings.frontend_base_url}/dashboard?upgraded=1",
        cancel_url=f"{settings.frontend_base_url}/pricing?canceled=1",
        allow_promotion_codes=True,
    )
    return {"checkout_url": checkout.url}


@router.post("/portal")
async def customer_portal(subject: Subject = Depends(current_subject),
                          session: AsyncSession = Depends(db)):
    """Stripe-hosted page where users update cards / cancel — zero UI work for you."""
    from app.models import Subscription
    sub = (await session.execute(select(Subscription).where(
        Subscription.user_id == subject.user_id))).scalar_one_or_none()
    if not sub or not sub.stripe_customer_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "no subscription")
    portal = stripe.billing_portal.Session.create(
        customer=sub.stripe_customer_id,
        return_url=f"{settings.frontend_base_url}/dashboard")
    return {"portal_url": portal.url}


# Pro (ad-free) plans. "basic" is a paid but ad-supported tier; everyone not on
# an active Pro plan sees ads (the ad-revenue gate the frontend reads).
# "ios_iap" comes from the RevenueCat webhook (Apple/Google IAP) — also Pro.
PRO_PLANS = {"monthly", "yearly", "ios_iap"}


@router.get("/status")
async def my_status(subject: Subject = Depends(current_subject),
                    session: AsyncSession = Depends(db)):
    from app.models import Subscription
    sub = (await session.execute(select(Subscription).where(
        Subscription.user_id == subject.user_id))).scalar_one_or_none()
    active = bool(sub and sub.status == "active")
    plan = sub.plan if sub else "free"
    pro = active and plan in PRO_PLANS
    return {"premium": active, "plan": plan,
            "status": sub.status if sub else "inactive",
            "pro": pro, "ads": not pro}  # ads shown to free + basic tiers


@router.post("/webhook")
async def webhook(request: Request, session: AsyncSession = Depends(db),
                  stripe_signature: str = Header(None)):
    """Source of truth. Verifies Stripe's signature, then syncs our DB."""
    from datetime import datetime, timezone
    from uuid import UUID as _UUID

    from app.models import Subscription

    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.stripe_webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "invalid signature")

    obj = event["data"]["object"]

    async def _upsert(user_id, **fields):
        sub = (await session.execute(select(Subscription).where(
            Subscription.user_id == user_id))).scalar_one_or_none()
        if sub is None:
            sub = Subscription(user_id=user_id)
            session.add(sub)
        for k, v in fields.items():
            setattr(sub, k, v)

    if event["type"] == "checkout.session.completed":
        user_id = _UUID(obj["client_reference_id"])
        plan = (obj.get("metadata") or {}).get("plan", "monthly")
        await _upsert(user_id,
                      stripe_customer_id=obj["customer"],
                      stripe_subscription_id=obj.get("subscription"),
                      status="active", plan=plan)

    elif event["type"] in ("customer.subscription.updated",
                           "customer.subscription.deleted"):
        sub = (await session.execute(select(Subscription).where(
            Subscription.stripe_customer_id == obj["customer"]))).scalar_one_or_none()
        if sub:
            sub.status = ("canceled" if event["type"].endswith("deleted")
                          else obj["status"])  # active | past_due | ...
            period_end = obj.get("current_period_end")
            if period_end:
                sub.current_period_end = datetime.fromtimestamp(
                    period_end, tz=timezone.utc)

    return {"received": True}


# ---------------------------------------------------------------- gating
async def require_premium(subject: Subject = Depends(current_subject),
                          session: AsyncSession = Depends(db)) -> Subject:
    """Drop `premium_subject: Subject = Depends(require_premium)` into any
    endpoint to paywall it (e.g. council deep-dives, unlimited chat)."""
    from app.models import Subscription
    sub = (await session.execute(select(Subscription).where(
        Subscription.user_id == subject.user_id))).scalar_one_or_none()
    if not sub or sub.status != "active":
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED,
                            "upgrade required: POST /api/v1/billing/checkout")
    return subject
