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
      <header className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight text-slate-100">Universal Search</h1>
        <p className="mt-1 text-sm text-slate-500">
          Search your signals and memory — or pressure-test a question with the Strategic Council.
        </p>
      </header>

      <form onSubmit={runSearch} className="mb-6 flex gap-2">
        <div className="relative flex-1">
          <SearchIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <input
            className="input pl-9"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search signals, memory, or ask a strategic question…"
          />
        </div>
        <button type="submit" disabled={searching} className="btn-ghost">
          Search
        </button>
        <button
          type="button"
          onClick={analyze}
          disabled={analyzing || !q.trim()}
          className="btn-primary"
        >
          <Sparkles className="h-4 w-4" />
          {analyzing ? "Convening…" : "Ask the Council"}
        </button>
      </form>

      {report && (
        <div className="mb-6">
          <CouncilPanel report={report} />
        </div>
      )}

      {hits !== null && (
        <div>
          <div className="mb-2 text-xs uppercase tracking-wide text-slate-500">
            {hits.length} result{hits.length === 1 ? "" : "s"} · {tookMs} ms
          </div>
          {hits.length === 0 ? (
            <div className="card px-6 py-10 text-center text-sm text-slate-500">
              No matches. Try the Strategic Council instead.
            </div>
          ) : (
            <ul className="space-y-2">
              {hits.map((h) => (
                <li key={`${h.type}-${h.id}`} className="card px-4 py-3">
                  <div className="flex items-center gap-2">
                    <span className="chip">{h.type}</span>
                    {h.domain && <span className="text-xs text-slate-500">{h.domain}</span>}
                    {h.source && <span className="text-xs text-slate-600">· {h.source}</span>}
                  </div>
                  <p className="mt-1.5 text-sm font-medium text-slate-200">{h.title}</p>
                  {h.snippet && <p className="mt-0.5 text-sm text-slate-500">{h.snippet}</p>}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </AppShell>
  );
}
