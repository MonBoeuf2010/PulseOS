import React from "react";
import { GitBranch, Scale, Sparkles } from "lucide-react";
import type { CouncilReport } from "@/lib/types";
import { ConfidenceMeter } from "./ConfidenceMeter";

export function CouncilPanel({ report }: { report: CouncilReport }) {
  return (
    <div className="card p-3xl">
      <div className="mb-lg flex items-center justify-between">
        <div className="flex items-center gap-sm">
          <Sparkles className="h-4 w-4 text-accent-purple" />
          <h3 className="text-[16px] font-medium text-ink">Strategic Council</h3>
          <span className="chip">{report.tier} council</span>
        </div>
        <div className="flex items-center gap-sm">
          <span className="eyebrow">Confidence</span>
          <ConfidenceMeter value={report.confidence} />
        </div>
      </div>

      {report.executive_summary && (
        <p className="mb-lg text-[16px] leading-relaxed text-body">{report.executive_summary}</p>
      )}

      {report.consensus && (
        <div className="mb-lg">
          <div className="mb-xs flex items-center gap-1.5 eyebrow">
            <Scale className="h-3.5 w-3.5" /> Consensus
          </div>
          <p className="text-[14px] leading-relaxed text-body-mid">{report.consensus}</p>
        </div>
      )}

      {report.recommended_actions.length > 0 && (
        <div className="mb-lg">
          <div className="mb-sm eyebrow">Recommended actions</div>
          <ul className="space-y-sm">
            {report.recommended_actions.map((a, i) => (
              <li key={i} className="flex items-start gap-sm text-[14px] text-ink-strong">
                <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-accent-purple" />
                {a}
              </li>
            ))}
          </ul>
        </div>
      )}

      {report.dissent.length > 0 && (
        <div className="rounded-sm border border-accent-red/30 bg-accent-red/5 p-md">
          <div className="mb-1.5 flex items-center gap-1.5 text-[12px] font-medium uppercase tracking-[0.6px] text-signal-red">
            <GitBranch className="h-3.5 w-3.5" /> Dissenting view
          </div>
          {report.dissent.map((d, i) => (
            <p key={i} className="text-[14px] text-ink-strong">
              <span className="font-medium text-signal-red">{d.agent}:</span> {d.position}
            </p>
          ))}
        </div>
      )}

      <div className="mt-lg flex items-center gap-md border-t border-hairline-soft pt-md text-[12px] text-mute">
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
