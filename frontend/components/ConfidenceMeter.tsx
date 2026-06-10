import React from "react";

export function confidenceColor(c: number): string {
  if (c >= 0.75) return "text-signal-green";
  if (c >= 0.55) return "text-signal-amber";
  return "text-signal-red";
}

function barColor(c: number): string {
  if (c >= 0.75) return "bg-signal-green";
  if (c >= 0.55) return "bg-signal-amber";
  return "bg-signal-red";
}

export function ConfidenceMeter({ value, label = true }: { value: number; label?: boolean }) {
  const pct = Math.round(value * 100);
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 w-24 overflow-hidden rounded-full bg-ink-700">
        <div className={`h-full rounded-full ${barColor(value)}`} style={{ width: `${pct}%` }} />
      </div>
      {label && (
        <span className={`font-mono text-xs font-semibold ${confidenceColor(value)}`}>{pct}%</span>
      )}
    </div>
  );
}
