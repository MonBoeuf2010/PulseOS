"use client";

import React, { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Check, Radar, Zap } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { ConfidenceMeter } from "@/components/ConfidenceMeter";
import { api, ApiError } from "@/lib/api";
import type { Opportunity } from "@/lib/types";

function currency(n: number | null): string | null {
  if (n === null || n === undefined) return null;
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(n);
}

export default function OpportunitiesPage() {
  const router = useRouter();
  const [items, setItems] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [acting, setActing] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const res = await api.listOpportunities("open");
      setItems(res.items);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) router.replace("/login");
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    load();
  }, [load]);

  async function act(id: string) {
    setActing(id);
    try {
      await api.actOnOpportunity(id);
      setItems((prev) => prev.filter((o) => o.id !== id));
    } finally {
      setActing(null);
    }
  }

  return (
    <AppShell>
      <header className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight text-slate-100">Opportunities</h1>
        <p className="mt-1 text-sm text-slate-500">
          Time-sensitive, asymmetric upside surfaced for you to act on.
        </p>
      </header>

      {loading ? (
        <div className="space-y-3">
          {[0, 1].map((i) => (
            <div key={i} className="card h-28 animate-pulse" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <div className="card flex flex-col items-center px-6 py-16 text-center">
          <Radar className="mb-3 h-7 w-7 text-slate-600" />
          <h3 className="text-base font-semibold text-slate-200">No open opportunities</h3>
          <p className="mt-1 text-sm text-slate-500">New opportunities appear as signals arrive.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {items.map((o) => {
            const ev = currency(o.expected_value);
            return (
              <article key={o.id} className="card p-5">
                <div className="mb-3 flex items-start justify-between gap-4">
                  <div>
                    <span className="chip mb-2">{o.domain}</span>
                    <h3 className="text-base font-semibold text-slate-100">{o.title}</h3>
                  </div>
                  {ev && (
                    <div className="text-right">
                      <div className="text-[11px] uppercase tracking-wide text-slate-500">
                        Est. value
                      </div>
                      <div className="font-mono text-lg font-semibold text-signal-green">{ev}</div>
                    </div>
                  )}
                </div>
                {o.rationale && (
                  <p className="mb-4 text-sm leading-relaxed text-slate-400">{o.rationale}</p>
                )}
                <div className="flex items-center justify-between border-t border-ink-700/60 pt-3">
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] uppercase tracking-wide text-slate-500">
                      Confidence
                    </span>
                    <ConfidenceMeter value={o.confidence} />
                  </div>
                  <button
                    onClick={() => act(o.id)}
                    disabled={acting === o.id}
                    className="btn-primary px-3 py-1.5"
                  >
                    {acting === o.id ? (
                      <Check className="h-3.5 w-3.5" />
                    ) : (
                      <Zap className="h-3.5 w-3.5" />
                    )}
                    Act on this
                  </button>
                </div>
              </article>
            );
          })}
        </div>
      )}
    </AppShell>
  );
}
