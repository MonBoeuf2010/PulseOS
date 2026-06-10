import React from "react";

export function confidenceColor(c: number): string {
  if (c >= 0.75) return "text-signal-green";
  if (c >= 0.55) return "text-signal-amber";
  return "text-signal-red";
}

function barColor(c: number): string {
  if (c >= 0.75) return "bg-accent-green";
  if (c >= 0.55) return "bg-accent-yellow";
  return "bg-accent-red";
}

export function ConfidenceMeter({ value, label = true }: { value: number; label?: boolean }) {
  const pct = Math.round(value * 100);
  return (
    <div className="flex items-center gap-sm">
      <div className="h-1.5 w-24 overflow-hidden rounded-full bg-hairline-soft">
        <div className={`h-full rounded-full ${barColor(value)}`} style={{ width: `${pct}%` }} />
      </div>
      {label && (
        <span className={`font-mono text-[12px] font-medium ${confidenceColor(value)}`}>{pct}%</span>
      )}
    </div>
  );
}
