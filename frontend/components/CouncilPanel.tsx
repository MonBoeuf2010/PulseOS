import React from "react";
import { GitBranch, Scale, Sparkles } from "lucide-react";
import type { CouncilReport } from "@/lib/types";
import { ConfidenceMeter } from "./ConfidenceMeter";

export function CouncilPanel({ report }: { report: CouncilReport }) {
  return (
    <div className="card p-5">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-accent-soft" />
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-300">
            Strategic Council
          </h3>
          <span className="chip">{report.tier} council</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] uppercase tracking-wide text-slate-500">Confidence</span>
          <ConfidenceMeter value={report.confidence} />
        </div>
      </div>

      {report.executive_summary && (
        <p className="mb-4 text-sm leading-relaxed text-slate-200">{report.executive_summary}</p>
      )}

      {report.consensus && (
        <div className="mb-4">
          <div className="mb-1 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-400">
            <Scale className="h-3.5 w-3.5" /> Consensus
          </div>
          <p className="text-sm leading-relaxed text-slate-400">{report.consensus}</p>
        </div>
      )}

      {report.recommended_actions.length > 0 && (
        <div className="mb-4">
          <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
            Recommended actions
          </div>
          <ul className="space-y-1.5">
            {report.recommended_actions.map((a, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-300">
                <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-accent" />
                {a}
              </li>
            ))}
          </ul>
        </div>
      )}

      {report.dissent.length > 0 && (
        <div className="rounded-xl border border-signal-red/20 bg-signal-red/5 p-3">
          <div className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-signal-red/90">
            <GitBranch className="h-3.5 w-3.5" /> Dissenting view
          </div>
          {report.dissent.map((d, i) => (
            <p key={i} className="text-sm text-slate-300">
              <span className="font-medium text-signal-red/90">{d.agent}:</span> {d.position}
            </p>
          ))}
        </div>
      )}

      <div className="mt-4 flex items-center gap-4 border-t border-ink-700/60 pt-3 text-[11px] text-slate-500">
        <span>cost ${report.cost_usd.toFixed(4)}</span>
        <span>·</span>
        <span>{report.latency_ms} ms</span>
        {report.estimated_impact !== null && (
          <>
            <span>·</span>
            <span>est. impact ${report.estimated_impact.toLocaleString()}</span>
          </>
        )}
      </div>
    </div>
  );
}
