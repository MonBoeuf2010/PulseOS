"""RevenueCat webhook — Apple/Google in-app-purchase subscriptions.

Mirror of the Stripe webhook for mobile. Apple requires digital subscriptions
bought *inside* the iOS app to use Apple IAP (StoreKit), not Stripe. RevenueCat
normalizes Apple/Google receipts and calls this webhook, so the SAME Subscription
row flips to active — `require_premium` and the ad gate then behave identically
for web (Stripe) and iOS (IAP).

Setup — RevenueCat Dashboard → Project → Integrations → Webhooks:
  URL: https://<your-api-domain>/v1/iap/webhook   (this app mounts under /v1)
  Authorization header value → set the SAME string as REVENUECAT_WEBHOOK_AUTH in .env
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Request, status
from sqlalchemy import select

from app.core.config import get_settings
from app.core.db import tenant_session

router = APIRouter()
settings = get_settings()

PREMIUM_EVENTS = {"INITIAL_PURCHASE", "RENEWAL", "UNCANCELLATION", "PRODUCT_CHANGE"}
CANCEL_EVENTS = {"EXPIRATION", "CANCELLATION", "BILLING_ISSUE"}


@router.post("/webhook")
async def revenuecat_webhook(request: Request, authorization: str = Header(None)):
    """Source of truth for mobile subscriptions. Verifies the shared secret,
    then upserts the user's Subscription. Runs without a user JWT (RevenueCat
    calls server-to-server), so it opens its own session rather than using the
    auth-bound `db` dependency."""
    if not settings.revenuecat_webhook_auth or authorization != settings.revenuecat_webhook_auth:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "bad auth")

    event = (await request.json()).get("event", {})
    etype = event.get("type")
    # CRITICAL: in the iOS app set the RevenueCat App User ID to YOUR user UUID
    # (Purchases.logIn(user.id)) — one id everywhere, no guessing (the
    # DreamDecode UUID-mismatch lesson).
    try:
        user_id = UUID(event.get("app_user_id"))
    except (TypeError, ValueError):
        # Unknown/anonymous id — ack so RevenueCat doesn't retry forever.
        return {"received": True, "ignored": "no app_user_id"}

    from app.models import Subscription
    async with tenant_session(None) as session:
        sub = (await session.execute(select(Subscription).where(
            Subscription.user_id == user_id))).scalar_one_or_none()
        if sub is None:
            sub = Subscription(user_id=user_id)
            session.add(sub)
        # plan "ios_iap" is part of PRO_PLANS in billing.py → ad-free + premium.
        if etype in PREMIUM_EVENTS:
            sub.status, sub.plan = "active", "ios_iap"
        elif etype in CANCEL_EVENTS:
            sub.status = "canceled"
    return {"received": True}
