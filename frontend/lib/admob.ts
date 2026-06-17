"use client";

import { useEffect } from "react";
import { Capacitor } from "@capacitor/core";

/**
 * AdMob banner ads for the iOS app — shown ONLY to ad-supported tiers
 * (free / $5 Basic). Premium ($15 / yearly / Apple IAP) users see no ads.
 *
 * Design goals:
 *  - FAIL-SAFE: every AdMob call is wrapped; any error → simply no ad, never a
 *    crash. Ads are revenue, not core functionality, so they must never break
 *    the app.
 *  - WEB is untouched: native-only. The web build keeps using <AdSlot/> (AdSense).
 *  - NO ACCOUNT NEEDED to build/run: defaults to Google's official TEST ad unit.
 *    Set NEXT_PUBLIC_ADMOB_IOS_BANNER to your real ad-unit id for live revenue.
 */

// Google's official test banner unit (safe to ship; shows "Test Ad").
const TEST_BANNER = "ca-app-pub-3940256099942544/2934735716";
const BANNER_AD_ID = process.env.NEXT_PUBLIC_ADMOB_IOS_BANNER || TEST_BANNER;
const IS_TEST = !process.env.NEXT_PUBLIC_ADMOB_IOS_BANNER;

function isNative(): boolean {
  try {
    return Capacitor.isNativePlatform();
  } catch {
    return false;
  }
}

let initialized = false;

async function ensureInit(): Promise<void> {
  if (initialized) return;
  const { AdMob } = await import("@capacitor-community/admob");
  await AdMob.initialize({ initializeForTesting: IS_TEST });
  initialized = true;
}

async function showBanner(): Promise<void> {
  try {
    const { AdMob, BannerAdSize, BannerAdPosition } = await import(
      "@capacitor-community/admob"
    );
    await ensureInit();
    await AdMob.showBanner({
      adId: BANNER_AD_ID,
      adSize: BannerAdSize.ADAPTIVE_BANNER,
      position: BannerAdPosition.BOTTOM_CENTER,
      margin: 0,
      isTesting: IS_TEST,
    });
  } catch (e) {
    console.warn("[admob] banner not shown:", e);
  }
}

async function removeBanner(): Promise<void> {
  try {
    const { AdMob } = await import("@capacitor-community/admob");
    await AdMob.removeBanner();
  } catch {
    /* nothing to remove / not ready — ignore */
  }
}

/**
 * Drives a native bottom banner from the viewer's entitlements.
 * Call once high in the tree (AppShell). No-op on web and for Premium users.
 */
export function useAdmobBanner(showAds: boolean): void {
  useEffect(() => {
    if (!isNative()) return;
    if (showAds) void showBanner();
    else void removeBanner();
    return () => {
      void removeBanner();
    };
  }, [showAds]);
}
