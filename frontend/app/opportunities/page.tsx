"use client";

import React, { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Check, Radar, Zap } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { ConfidenceMeter } from "@/components/ConfidenceMeter";
import { categoryAccent } from "@/lib/category";
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
      <header className="mb-lg">
        <div className="eyebrow mb-1">Opportunity Engine</div>
        <h1 className="text-[32px] font-semibold tracking-[-0.6px] text-ink">Opportunities</h1>
        <p className="mt-1 text-[15px] text-body-mid">
          Time-sensitive, asymmetric upside surfaced for you to act on.
        </p>
      </header>

      {loading ? (
        <div className="space-y-md">
          {[0, 1].map((i) => (
            <div key={i} className="card h-28 animate-pulse" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <div className="card flex flex-col items-center px-lg py-16 text-center">
          <Radar className="mb-md h-7 w-7 text-mute-soft" />
          <h3 className="text-[18px] font-medium text-ink">No open opportunities</h3>
          <p className="mt-1 text-[14px] text-body-mid">New opportunities appear as signals arrive.</p>
        </div>
      ) : (
        <div className="space-y-md">
          {items.map((o) => {
            const ev = currency(o.expected_value);
            const accent = categoryAccent(o.domain);
            return (
              <article key={o.id} className="card p-3xl transition-shadow hover:shadow-lift">
                <div className="mb-md flex items-start justify-between gap-lg">
                  <div>
                    <span className={`chip mb-md border-transparent ${accent.soft} ${accent.text}`}>
                      {o.domain}
                    </span>
                    <h3 className="text-[20px] font-medium tracking-[-0.2px] text-ink">{o.title}</h3>
                  </div>
                  {ev && (
                    <div className="text-right">
                      <div className="eyebrow">Est. value</div>
                      <div className="font-mono text-[24px] font-medium text-signal-green">{ev}</div>
                    </div>
                  )}
                </div>
                {o.rationale && (
                  <p className="mb-lg text-[16px] leading-relaxed text-body">{o.rationale}</p>
                )}
                <div className="flex items-center justify-between border-t border-hairline-soft pt-md">
                  <div className="flex items-center gap-sm">
                    <span className="eyebrow">Confidence</span>
                    <ConfidenceMeter value={o.confidence} />
                  </div>
                  <button onClick={() => act(o.id)} disabled={acting === o.id} className="btn-primary btn-sm">
                    {acting === o.id ? <Check className="h-3.5 w-3.5" /> : <Zap className="h-3.5 w-3.5" />}
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
