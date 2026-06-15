"use client";

/**
 * RevenueCat native In-App Purchase integration (iOS).
 *
 * Apple REQUIRES digital subscriptions bought inside the iOS app to go through
 * Apple IAP (StoreKit), not Stripe/Safari — using web checkout in the app is an
 * automatic rejection (App Store guideline 3.1.1). On native we therefore use
 * RevenueCat; on the web build these helpers no-op and the app keeps using Stripe.
 *
 * THE ONE RULE (the DreamDecode UUID lesson): the RevenueCat "App User ID" MUST
 * equal YOUR backend user UUID. The same id flows: login → here → RevenueCat →
 * the iap webhook (backend/app/api/v1/iap.py) → the Subscription row. One id
 * everywhere, or premium detection silently breaks.
 *
 * Setup: paste your RevenueCat *public* iOS key (appl_...) into
 * NEXT_PUBLIC_REVENUECAT_IOS_KEY (see .env.example). The entitlement you attach
 * the product to in the RevenueCat dashboard must be named "premium".
 */

import { Capacitor } from "@capacitor/core";

const ENTITLEMENT_ID = "premium";
const IOS_API_KEY = process.env.NEXT_PUBLIC_REVENUECAT_IOS_KEY ?? "";

let configuredFor: string | null = null;

/** True only inside the native iOS/Android shell — false in any browser. */
export function isNativePlatform(): boolean {
  return Capacitor.isNativePlatform();
}

/** True when native AND a RevenueCat key is configured — i.e. IAP can run. */
export function iapAvailable(): boolean {
  return isNativePlatform() && IOS_API_KEY.length > 0;
}

/**
 * Configure RevenueCat once and bind it to the signed-in user. Safe to call on
 * every app load / login; it only reconfigures when the user changes. No-op on web.
 */
export async function initRevenueCat(userId: string): Promise<void> {
  if (!iapAvailable() || !userId) return;
  if (configuredFor === userId) return;
  const { Purchases, LOG_LEVEL } = await import("@revenuecat/purchases-capacitor");
  try {
    if (configuredFor === null) {
      await Purchases.setLogLevel({ level: LOG_LEVEL.WARN });
      await Purchases.configure({ apiKey: IOS_API_KEY, appUserID: userId });
    } else {
      // A different user signed in on the same device — switch the RC identity.
      await Purchases.logIn({ appUserID: userId });
    }
    configuredFor = userId;
  } catch (err) {
    console.error("RevenueCat init failed", err);
  }
}

/**
 * Localized App Store price string for the premium subscription (e.g. "$5.99"),
 * read from the current RevenueCat Offering. Returns null if unavailable.
 */
export async function getPremiumPriceString(): Promise<string | null> {
  if (!iapAvailable()) return null;
  const { Purchases } = await import("@revenuecat/purchases-capacitor");
  try {
    const offerings = await Purchases.getOfferings();
    return offerings.current?.availablePackages?.[0]?.product?.priceString ?? null;
  } catch {
    return null;
  }
}

/** Ask Apple (via RevenueCat) whether this user currently has the premium entitlement. */
export async function hasPremiumEntitlement(): Promise<boolean> {
  if (!iapAvailable()) return false;
  const { Purchases } = await import("@revenuecat/purchases-capacitor");
  try {
    const { customerInfo } = await Purchases.getCustomerInfo();
    return Boolean(customerInfo.entitlements.active[ENTITLEMENT_ID]);
  } catch (err) {
    console.error("RevenueCat getCustomerInfo failed", err);
    return false;
  }
}

/**
 * Launch the native Apple purchase sheet (Face ID / one tap) for the premium
 * subscription. Returns true if the user ends up with the premium entitlement.
 * The actual source of truth still flips server-side via the RevenueCat webhook;
 * this return value is just for instant UI feedback.
 */
export async function purchasePremium(): Promise<{ ok: boolean; error?: string; cancelled?: boolean }> {
  if (!iapAvailable()) return { ok: false, error: "In-app purchases aren't available here." };
  const { Purchases } = await import("@revenuecat/purchases-capacitor");
  try {
    const offerings = await Purchases.getOfferings();
    const pkg = offerings.current?.availablePackages?.[0];
    if (!pkg) {
      return {
        ok: false,
        error:
          "No subscription found. Check that the product is attached to an Offering in RevenueCat and is Ready to Submit in App Store Connect.",
      };
    }
    const { customerInfo } = await Purchases.purchasePackage({ aPackage: pkg });
    return { ok: Boolean(customerInfo.entitlements.active[ENTITLEMENT_ID]) };
  } catch (err) {
    // RevenueCat throws with userCancelled when the user dismisses the sheet.
    const e = err as { code?: string; userCancelled?: boolean; message?: string };
    if (e?.userCancelled) return { ok: false, cancelled: true };
    return { ok: false, error: e?.message ?? "Purchase failed. Please try again." };
  }
}

/** Apple REQUIRES a visible "Restore Purchases" control. Re-applies a prior subscription. */
export async function restorePurchases(): Promise<{ ok: boolean; error?: string }> {
  if (!iapAvailable()) return { ok: false, error: "Restore is only available in the app." };
  const { Purchases } = await import("@revenuecat/purchases-capacitor");
  try {
    const { customerInfo } = await Purchases.restorePurchases();
    return { ok: Boolean(customerInfo.entitlements.active[ENTITLEMENT_ID]) };
  } catch (err) {
    return { ok: false, error: (err as { message?: string })?.message ?? "Restore failed." };
  }
}
