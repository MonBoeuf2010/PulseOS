"use client";

import React, { useState } from "react";
import { AlertTriangle, Check, ThumbsDown, ThumbsUp, Zap } from "lucide-react";
import { api } from "@/lib/api";
import { categoryAccent } from "@/lib/category";
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
  const accent = categoryAccent(item.category);

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
    <article className="card p-3xl transition-shadow hover:shadow-lift">
      <div className="mb-md flex items-start justify-between gap-lg">
        <div>
          <span className={`chip mb-md border-transparent ${accent.soft} ${accent.text}`}>
            {item.category}
          </span>
          <h3 className="text-[20px] font-medium leading-tight tracking-[-0.2px] text-ink">
            {item.title}
          </h3>
        </div>
        {ev && (
          <div className="shrink-0 text-right">
            <div className="eyebrow">Est. value</div>
            <div className="font-mono text-[24px] font-medium text-signal-green">{ev}</div>
          </div>
        )}
      </div>

      <p className="mb-lg text-[16px] leading-relaxed text-body">{item.rationale}</p>

      {item.cost_of_inaction && (
        <div className="mb-lg flex items-start gap-sm rounded-sm border border-accent-yellow/40 bg-accent-yellow/10 p-md text-[14px] text-ink-strong">
          <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-accent-orange" />
          <span>
            <span className="font-medium">Cost of inaction:</span> {item.cost_of_inaction}
          </span>
        </div>
      )}

      <div className="flex items-center justify-between gap-lg border-t border-hairline-soft pt-md">
        <div className="flex items-center gap-sm">
          <span className="eyebrow">Confidence</span>
          <ConfidenceMeter value={item.confidence} />
        </div>

        {verdict ? (
          <span className="inline-flex items-center gap-1.5 text-[14px] font-medium text-signal-green">
            <Check className="h-3.5 w-3.5" />
            {verdict === "acted_on" ? "Marked as acted on" : "Thanks for the feedback"}
          </span>
        ) : (
          <div className="flex items-center gap-sm">
            <button
              className="btn-secondary btn-sm px-md"
              disabled={pending !== null}
              onClick={() => send("useful")}
              aria-label="Useful"
            >
              <ThumbsUp className="h-3.5 w-3.5" />
            </button>
            <button
              className="btn-secondary btn-sm px-md"
              disabled={pending !== null}
              onClick={() => send("not_useful")}
              aria-label="Not useful"
            >
              <ThumbsDown className="h-3.5 w-3.5" />
            </button>
            <button
              className="btn-primary btn-sm"
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
