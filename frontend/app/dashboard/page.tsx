"use client";

import React, { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { MessagesSquare, RefreshCw, Sparkles } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { AnalyticsTiles } from "@/components/AnalyticsTiles";
import { BriefingCard } from "@/components/BriefingCard";
import { AdSlot } from "@/components/AdSlot";
import { api, ApiError } from "@/lib/api";
import { useEntitlements } from "@/lib/useEntitlements";
import type { Dashboard } from "@/lib/types";

export default function DashboardPage() {
  const router = useRouter();
  const { status } = useEntitlements();
  const [data, setData] = useState<Dashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [justUpgraded, setJustUpgraded] = useState(false);

  useEffect(() => {
    if (typeof window !== "undefined" && new URLSearchParams(window.location.search).has("upgraded")) {
      setJustUpgraded(true);
      window.history.replaceState({}, "", "/dashboard");
    }
  }, []);

  const load = useCallback(async () => {
    try {
      setData(await api.dashboard());
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) router.replace("/login");
      else setError("Could not load your dashboard.");
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    load();
  }, [load]);

  async function generate() {
    setGenerating(true);
    setError(null);
    try {
      await api.generateBriefing();
      await new Promise((r) => setTimeout(r, 800));
      await load();
    } catch {
      setError("Could not generate a briefing.");
    } finally {
      setGenerating(false);
    }
  }

  const briefing = data?.briefing ?? null;
  const items = briefing?.items ?? [];

  return (
    <AppShell>
      <header className="mb-lg flex flex-wrap items-end justify-between gap-md">
        <div>
          <div className="eyebrow mb-1">Today</div>
          <h1 className="text-[32px] font-semibold tracking-[-0.6px] text-ink">
            Intelligence Dashboard
          </h1>
          <p className="mt-1 text-[15px] text-body-mid">
            {briefing?.summary ?? "Your ranked, highest-value actions — from the Strategic Council."}
          </p>
        </div>
        <div className="flex items-center gap-sm">
          <Link href="/chat" className="btn-secondary">
            <MessagesSquare className="h-4 w-4" /> Ask analyst
          </Link>
          <button onClick={generate} disabled={generating} className="btn-primary">
            {generating ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
            {generating ? "Generating…" : "Generate briefing"}
          </button>
        </div>
      </header>

      {justUpgraded && (
        <p className="mb-md rounded-sm border border-accent-green/30 bg-accent-green/5 px-lg py-md text-[14px] text-signal-green">
          You’re upgraded — welcome to Pro. Ads are off and the full Strategic Council is unlocked.
        </p>
      )}

      {!status.pro && (
        <div className="card-dark mb-lg flex flex-wrap items-center justify-between gap-md p-lg shadow-lift">
          <div>
            <div className="text-[15px] font-medium text-on-primary">
              {status.plan === "basic" ? "Go ad-free with Pro" : "Unlock the full Strategic Council"}
            </div>
            <p className="mt-0.5 text-[13px] text-on-primary/70">
              Unlimited briefings, live AI reasoning, and no ads. Try Pro free for 2 weeks.
            </p>
          </div>
          <Link href="/pricing" className="btn bg-on-primary text-ink hover:bg-hairline-soft">
            <Sparkles className="h-4 w-4" /> Upgrade
          </Link>
        </div>
      )}

      {data && (
        <div className="mb-lg">
          <AnalyticsTiles analytics={data.analytics} />
        </div>
      )}

      <AdSlot className="mb-lg" />

      {error && (
        <p className="mb-md rounded-sm border border-accent-red/30 bg-accent-red/5 px-lg py-md text-[14px] text-signal-red">
          {error}
        </p>
      )}

      {loading ? (
        <div className="space-y-md">
          {[0, 1, 2].map((i) => (
            <div key={i} className="card h-32 animate-pulse" />
          ))}
        </div>
      ) : items.length > 0 ? (
        <div className="space-y-md">
          {items.map((it) => (
            <BriefingCard key={it.id} item={it} />
          ))}
        </div>
      ) : (
        <div className="card flex flex-col items-center justify-center px-lg py-16 text-center">
          <div className="mb-md grid h-12 w-12 place-items-center rounded-md bg-canvas-soft">
            <Sparkles className="h-6 w-6 text-ink" />
          </div>
          <h3 className="text-[18px] font-medium text-ink">No briefing yet</h3>
          <p className="mt-1 max-w-sm text-[14px] text-body-mid">
            Generate your first briefing and the Strategic Council will surface the highest-value
            actions from the latest signals.
          </p>
          <button onClick={generate} disabled={generating} className="btn-primary mt-lg">
            <Sparkles className="h-4 w-4" /> Generate my first briefing
          </button>
        </div>
      )}
    </AppShell>
  );
}
