"use client";

import { useEffect, useRef } from "react";
import Link from "next/link";
import { useEntitlements } from "@/lib/useEntitlements";

const ADSENSE_CLIENT = process.env.NEXT_PUBLIC_ADSENSE_CLIENT ?? "";

declare global {
  interface Window {
    adsbygoogle?: unknown[];
  }
}

/**
 * Revenue unit shown to free + Basic (ad-supported) tiers; hidden for Pro.
 *
 * - When NEXT_PUBLIC_ADSENSE_CLIENT + a slot id are set, renders a real Google
 *   AdSense unit (the script is injected once in app/layout.tsx).
 * - Otherwise renders a house "Upgrade to remove ads" placeholder, which keeps
 *   the layout honest in dev and doubles as an upsell before AdSense approval.
 */
export function AdSlot({ slot, className = "" }: { slot?: string; className?: string }) {
  const { status, loading } = useEntitlements();
  const pushed = useRef(false);

  const live = Boolean(ADSENSE_CLIENT && slot);

  useEffect(() => {
    if (!live || pushed.current || loading || !status.ads) return;
    try {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
      pushed.current = true;
    } catch {
      /* AdSense not ready yet — ignore */
    }
  }, [live, loading, status.ads]);

  // Pro users (and while we don't yet know) see nothing.
  if (loading || !status.ads) return null;

  if (live) {
    return (
      <ins
        className={`adsbygoogle block ${className}`}
        style={{ display: "block" }}
        data-ad-client={ADSENSE_CLIENT}
        data-ad-slot={slot}
        data-ad-format="auto"
        data-full-width-responsive="true"
      />
    );
  }

  // House placeholder / upsell (no AdSense configured yet).
  return (
    <div
      className={`card flex items-center justify-between gap-md border-dashed px-lg py-md text-[13px] text-body-mid ${className}`}
    >
      <span>Sponsored — Basic is ad-supported.</span>
      <Link href="/pricing" className="font-medium text-ink underline underline-offset-2">
        Go ad-free with Pro →
      </Link>
    </div>
  );
}
