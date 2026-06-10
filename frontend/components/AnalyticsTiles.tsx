import React from "react";
import { Clock, DollarSign, Target } from "lucide-react";
import type { Analytics } from "@/lib/types";

function Tile({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="card flex items-center gap-3 px-4 py-3">
      <div className="grid h-9 w-9 place-items-center rounded-xl bg-accent/10 text-accent-soft">
        {icon}
      </div>
      <div>
        <div className="font-mono text-lg font-semibold text-slate-100">{value}</div>
        <div className="text-[11px] uppercase tracking-wide text-slate-500">{label}</div>
      </div>
    </div>
  );
}

export function AnalyticsTiles({ analytics }: { analytics: Analytics }) {
  const money = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(analytics.money_saved_usd);
  const hrs = (analytics.time_saved_min / 60).toFixed(1);
  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
      <Tile icon={<Clock className="h-4 w-4" />} label="Time saved" value={`${hrs} h`} />
      <Tile icon={<DollarSign className="h-4 w-4" />} label="Value realized" value={money} />
      <Tile icon={<Target className="h-4 w-4" />} label="Actions taken" value={`${analytics.acted}`} />
    </div>
  );
}
