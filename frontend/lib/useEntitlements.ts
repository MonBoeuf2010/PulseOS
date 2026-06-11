"use client";

import { useEffect, useState } from "react";
import { api, ApiError } from "./api";
import type { BillingStatus } from "./types";

const DEFAULT: BillingStatus = {
  premium: false,
  plan: "free",
  status: "inactive",
  pro: false,
  ads: true,
};

/**
 * Reads the viewer's subscription entitlements from the backend.
 * Drives both the upgrade CTAs and whether ads render (Pro = ad-free).
 * Fails open to the free/ad-supported default so UI never blocks on billing.
 */
export function useEntitlements(): { status: BillingStatus; loading: boolean } {
  const [status, setStatus] = useState<BillingStatus>(DEFAULT);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    api
      .billingStatus()
      .then((s) => {
        if (alive) setStatus(s);
      })
      .catch((err) => {
        // 401 is handled globally by the api layer; anything else → stay on free default.
        if (!(err instanceof ApiError)) console.error(err);
      })
      .finally(() => {
        if (alive) setLoading(false);
      });
    return () => {
      alive = false;
    };
  }, []);

  return { status, loading };
}
