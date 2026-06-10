"use client";

import React, { useState } from "react";
import { AlertTriangle, Check, ThumbsDown, ThumbsUp, Zap } from "lucide-react";
import { api } from "@/lib/api";
import type { BriefingItem, FeedbackVerdict } from "@/lib/types";
import { ConfidenceMeter } from "./ConfidenceMeter";

function currency(n: number | null): string | null {
  if (n === null || n === undefined) return null;
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(n);
}

export function BriefingCard({ item }: { item: BriefingItem }) {
  const [verdict, setVerdict] = useState<FeedbackVerdict | null>(null);
  const [pending, setPending] = useState<FeedbackVerdict | null>(null);
  const ev = currency(item.expected_value);

  async function send(v: FeedbackVerdict) {
    setPending(v);
    try {
      await api.feedback(item.id, v);
      setVerdict(v);
    } catch {
      /* surfaced globally; keep card usable */
    } finally {
      setPending(null);
    }
  }

  return (
    <article className="card p-5">
      <div className="mb-3 flex items-start justify-between gap-4">
        <div>
          <span className="chip mb-2">{item.category}</span>
          <h3 className="text-base font-semibold leading-snug text-slate-100">{item.title}</h3>
        </div>
        {ev && (
          <div className="shrink-0 text-right">
            <div className="text-[11px] uppercase tracking-wide text-slate-500">Est. value</div>
            <div className="font-mono text-lg font-semibold text-signal-green">{ev}</div>
          </div>
        )}
      </div>

      <p className="mb-4 text-sm leading-relaxed text-slate-400">{item.rationale}</p>

      {item.cost_of_inaction && (
        <div className="mb-4 flex items-start gap-2 rounded-xl border border-signal-amber/20 bg-signal-amber/5 p-3 text-xs text-signal-amber/90">
          <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
          <span>
            <span className="font-semibold">Cost of inaction:</span> {item.cost_of_inaction}
          </span>
        </div>
      )}

      <div className="flex items-center justify-between gap-4 border-t border-ink-700/60 pt-3">
        <div className="flex items-center gap-2">
          <span className="text-[11px] uppercase tracking-wide text-slate-500">Confidence</span>
          <ConfidenceMeter value={item.confidence} />
        </div>

        {verdict ? (
          <span className="inline-flex items-center gap-1.5 text-xs font-medium text-signal-green">
            <Check className="h-3.5 w-3.5" />
            {verdict === "acted_on" ? "Marked as acted on" : "Thanks for the feedback"}
          </span>
        ) : (
          <div className="flex items-center gap-2">
            <button
              className="btn-ghost px-2.5 py-1.5"
              disabled={pending !== null}
              onClick={() => send("useful")}
              aria-label="Useful"
            >
              <ThumbsUp className="h-3.5 w-3.5" />
            </button>
            <button
              className="btn-ghost px-2.5 py-1.5"
              disabled={pending !== null}
              onClick={() => send("not_useful")}
              aria-label="Not useful"
            >
              <ThumbsDown className="h-3.5 w-3.5" />
            </button>
            <button
              className="btn-primary px-3 py-1.5"
              disabled={pending !== null}
              onClick={() => send("acted_on")}
            >
              <Zap className="h-3.5 w-3.5" />
              Acted on
            </button>
          </div>
        )}
      </div>
    </article>
  );
}
