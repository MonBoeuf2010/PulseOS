import React from "react";
import { Clock, DollarSign, Target } from "lucide-react";
import type { Analytics } from "@/lib/types";

function Tile({
  icon,
  label,
  value,
  accent,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  accent: string;
}) {
  return (
    <div className="card flex items-center gap-md px-lg py-md">
      <div className={`grid h-10 w-10 place-items-center rounded-md ${accent}`}>{icon}</div>
      <div>
        <div className="font-mono text-[24px] font-medium leading-none text-ink">{value}</div>
        <div className="eyebrow mt-1">{label}</div>
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
    <div className="grid grid-cols-1 gap-md sm:grid-cols-3">
      <Tile
        icon={<Clock className="h-4 w-4 text-accent-blue-deep" />}
        label="Time saved"
        value={`${hrs} h`}
        accent="bg-accent-blue/10"
      />
      <Tile
        icon={<DollarSign className="h-4 w-4 text-signal-green" />}
        label="Value realized"
        value={money}
        accent="bg-accent-green/10"
      />
      <Tile
        icon={<Target className="h-4 w-4 text-accent-purple" />}
        label="Actions taken"
        value={`${analytics.acted}`}
        accent="bg-accent-purple/10"
      />
    </div>
  );
}
