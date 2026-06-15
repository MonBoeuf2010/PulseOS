"use client";

import React, { useEffect, useState } from "react";
import { Check, ArrowRight, Loader2, RotateCcw } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { api, ApiError } from "@/lib/api";
import { useEntitlements } from "@/lib/useEntitlements";
import {
  getPremiumPriceString,
  iapAvailable,
  purchasePremium,
  restorePurchases,
} from "@/lib/revenuecat";
import type { CheckoutPlan } from "@/lib/types";

const BASIC_FEATURES = [
  "Daily briefing (3 actions)",
  "AI analyst (basic)",
  "Community feed",
  "Ad-supported",
];
const PRO_FEATURES = [
  "Unlimited briefings + full Strategic Council",
  "AI analyst with live reasoning",
  "Opportunity Engine + value tracking",
  "No ads — ever",
];

export default function PricingPage() {
  const { status } = useEntitlements();
  const [busy, setBusy] = useState<CheckoutPlan | "portal" | "iap" | "restore" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);

  // On iOS we MUST sell via Apple In-App Purchase, not Stripe (App Store rule 3.1.1).
  const [native, setNative] = useState(false);
  const [iapPrice, setIapPrice] = useState<string | null>(null);

  useEffect(() => {
    if (!iapAvailable()) return;
    setNative(true);
    void getPremiumPriceString().then(setIapPrice);
  }, []);

  async function checkout(plan: CheckoutPlan) {
    setBusy(plan);
    setError(null);
    try {
      const { checkout_url } = await api.createCheckout(plan);
      window.location.href = checkout_url;
    } catch (err) {
      setError(
        err instanceof ApiError && err.status === 503
          ? "Payments aren’t switched on yet — add your Stripe keys to enable checkout."
          : "Could not start checkout. Please try again.",
      );
      setBusy(null);
    }
  }

  async function buyNative() {
    setBusy("iap");
    setError(null);
    setNotice(null);
    const res = await purchasePremium();
    setBusy(null);
    if (res.cancelled) return;
    if (res.ok) {
      setNotice("You’re Premium 🎉 It may take a moment to unlock everywhere.");
    } else {
      setError(res.error ?? "Purchase failed. Please try again.");
    }
  }

  async function restore() {
    setBusy("restore");
    setError(null);
    setNotice(null);
    const res = await restorePurchases();
    setBusy(null);
    if (res.ok) setNotice("Your subscription has been restored.");
    else setError(res.error ?? "No previous purchase found to restore.");
  }

  async function manage() {
    setBusy("portal");
    setError(null);
    try {
      const { portal_url } = await api.billingPortal();
      window.location.href = portal_url;
    } catch {
      setError("Could not open the billing portal.");
      setBusy(null);
    }
  }

  return (
    <AppShell>
      <header className="mb-lg">
        <div className="eyebrow mb-1">Plans</div>
        <h1 className="text-[32px] font-semibold tracking-[-0.6px] text-ink">
          Upgrade your intelligence
        </h1>
        <p className="mt-1 text-[15px] text-body-mid">
          {status.pro
            ? "You’re on Premium — ad-free, with the full Strategic Council."
            : status.plan === "basic"
              ? "You’re on Basic. Go Premium to remove ads and unlock the full council."
              : "Unlock unlimited AI council analyses, the full analyst chat, and an ad-free feed."}
        </p>
      </header>

      {error && (
        <p className="mb-md rounded-sm border border-accent-red/30 bg-accent-red/5 px-lg py-md text-[14px] text-signal-red">
          {error}
        </p>
      )}
      {notice && (
        <p className="mb-md rounded-sm border border-signal-green/30 bg-signal-green/5 px-lg py-md text-[14px] text-signal-green">
          {notice}
        </p>
      )}

      <div className={`grid grid-cols-1 gap-md ${native ? "" : "lg:grid-cols-2"}`}>
        {/* Basic — web only (Stripe). Apple doesn't allow web payment for digital goods in-app. */}
        {!native && (
          <div className="card p-3xl">
            <div className="eyebrow">Basic</div>
            <div className="mt-sm flex items-end gap-1">
              <span className="text-[40px] font-semibold tracking-[-1px] text-ink">$5</span>
              <span className="mb-2 text-[14px] text-mute">/ month</span>
            </div>
            <ul className="mt-lg space-y-sm text-[14px] text-body">
              {BASIC_FEATURES.map((f) => (
                <li key={f} className="flex items-center gap-sm">
                  <Check className="h-4 w-4 text-signal-green" /> {f}
                </li>
              ))}
            </ul>
            <button
              onClick={() => checkout("basic")}
              disabled={busy !== null || status.plan === "basic" || status.pro}
              className="btn-secondary mt-lg w-full"
            >
              {busy === "basic" ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
              {status.plan === "basic" ? "Current plan" : "Choose Basic"}
            </button>
          </div>
        )}

        {/* Premium */}
        <div className="card-dark relative p-3xl shadow-lift">
          <span className="absolute right-lg top-lg rounded-sm bg-accent-green px-sm py-xxs text-[12px] font-medium text-primary">
            Most popular
          </span>
          <div className="text-[12px] font-medium uppercase tracking-[0.6px] text-on-primary/70">
            Premium
          </div>
          <div className="mt-sm flex items-end gap-1">
            <span className="text-[40px] font-semibold tracking-[-1px] text-on-primary">
              {native ? (iapPrice ?? "$5.99") : "$15"}
            </span>
            <span className="mb-2 text-[14px] text-on-primary/60">/ month</span>
          </div>
          <div className="mt-xs text-[13px] font-medium text-accent-green">
            Cancel anytime — no ads
          </div>
          <ul className="mt-lg space-y-sm text-[14px] text-on-primary/90">
            {PRO_FEATURES.map((f) => (
              <li key={f} className="flex items-center gap-sm">
                <Check className="h-4 w-4 text-accent-green" /> {f}
              </li>
            ))}
          </ul>

          {status.pro ? (
            !native && (
              <button
                onClick={manage}
                disabled={busy !== null}
                className="btn mt-lg w-full bg-on-primary text-ink hover:bg-hairline-soft"
              >
                {busy === "portal" ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
                Manage billing
              </button>
            )
          ) : native ? (
            <button
              onClick={buyNative}
              disabled={busy !== null}
              className="btn mt-lg w-full bg-on-primary text-ink hover:bg-hairline-soft"
            >
              {busy === "iap" ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <>
                  Subscribe <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          ) : (
            <button
              onClick={() => checkout("monthly")}
              disabled={busy !== null}
              className="btn mt-lg w-full bg-on-primary text-ink hover:bg-hairline-soft"
            >
              {busy === "monthly" ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <>
                  Go Premium <ArrowRight className="h-4 w-4" />
                </>
              )}
            </button>
          )}

          {/* Yearly upsell — web/Stripe only. */}
          {!native && !status.pro && (
            <button
              onClick={() => checkout("yearly")}
              disabled={busy !== null}
              className="mt-sm w-full text-[13px] text-on-primary/70 underline underline-offset-2 hover:text-on-primary"
            >
              {busy === "yearly" ? "…" : "Or save with yearly billing"}
            </button>
          )}

          {/* Apple requires a visible Restore Purchases control inside the app. */}
          {native && (
            <button
              onClick={restore}
              disabled={busy !== null}
              className="mt-md flex w-full items-center justify-center gap-xs text-[13px] text-on-primary/70 hover:text-on-primary"
            >
              {busy === "restore" ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <RotateCcw className="h-3.5 w-3.5" />
              )}
              Restore purchases
            </button>
          )}
        </div>
      </div>

      {native && (
        <p className="mt-lg text-center text-[12px] leading-relaxed text-mute">
          Payment is charged to your Apple ID. Subscriptions renew automatically unless cancelled at
          least 24 hours before the period ends. Manage or cancel anytime in your iPhone Settings →
          Apple ID → Subscriptions.
        </p>
      )}
    </AppShell>
  );
}
