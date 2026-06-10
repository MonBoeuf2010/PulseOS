"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Search as SearchIcon, Sparkles } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { CouncilPanel } from "@/components/CouncilPanel";
import { api, ApiError } from "@/lib/api";
import type { CouncilReport, SearchHit } from "@/lib/types";

export default function SearchPage() {
  const router = useRouter();
  const [q, setQ] = useState("");
  const [hits, setHits] = useState<SearchHit[] | null>(null);
  const [tookMs, setTookMs] = useState(0);
  const [searching, setSearching] = useState(false);
  const [report, setReport] = useState<CouncilReport | null>(null);
  const [analyzing, setAnalyzing] = useState(false);

  function handle401(err: unknown) {
    if (err instanceof ApiError && err.status === 401) router.replace("/login");
  }

  async function runSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!q.trim()) return;
    setSearching(true);
    setReport(null);
    try {
      const res = await api.search(q.trim());
      setHits(res.results);
      setTookMs(res.took_ms);
    } catch (err) {
      handle401(err);
    } finally {
      setSearching(false);
    }
  }

  async function analyze() {
    setAnalyzing(true);
    try {
      const res = await api.analyze(q.trim(), "general", "full");
      setReport(res.report);
    } catch (err) {
      handle401(err);
    } finally {
      setAnalyzing(false);
    }
  }

  return (
    <AppShell>
      <header className="mb-lg">
        <div className="eyebrow mb-1">Universal search</div>
        <h1 className="text-[32px] font-semibold tracking-[-0.6px] text-ink">Search</h1>
        <p className="mt-1 text-[15px] text-body-mid">
          Search your signals and memory — or pressure-test a question with the Strategic Council.
        </p>
      </header>

      <form onSubmit={runSearch} className="mb-lg flex gap-sm">
        <div className="relative flex-1">
          <SearchIcon className="pointer-events-none absolute left-md top-1/2 h-4 w-4 -translate-y-1/2 text-mute" />
          <input
            className="input pl-9"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search signals, memory, or ask a strategic question…"
          />
        </div>
        <button type="submit" disabled={searching} className="btn-secondary">
          Search
        </button>
        <button type="button" onClick={analyze} disabled={analyzing || !q.trim()} className="btn-primary">
          <Sparkles className="h-4 w-4" />
          {analyzing ? "Convening…" : "Ask the Council"}
        </button>
      </form>

      {report && (
        <div className="mb-lg">
          <CouncilPanel report={report} />
        </div>
      )}

      {hits !== null && (
        <div>
          <div className="eyebrow mb-sm">
            {hits.length} result{hits.length === 1 ? "" : "s"} · {tookMs} ms
          </div>
          {hits.length === 0 ? (
            <div className="card px-lg py-10 text-center text-[14px] text-body-mid">
              No matches. Try the Strategic Council instead.
            </div>
          ) : (
            <ul className="space-y-sm">
              {hits.map((h) => (
                <li key={`${h.type}-${h.id}`} className="card px-lg py-md">
                  <div className="flex items-center gap-sm">
                    <span className="chip">{h.type}</span>
                    {h.domain && <span className="text-[13px] text-mute">{h.domain}</span>}
                    {h.source && <span className="text-[13px] text-mute-soft">· {h.source}</span>}
                  </div>
                  <p className="mt-1.5 text-[15px] font-medium text-ink">{h.title}</p>
                  {h.snippet && <p className="mt-0.5 text-[14px] text-body-mid">{h.snippet}</p>}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </AppShell>
  );
}
