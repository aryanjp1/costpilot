import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import { Card } from "@/components/ui";
import {
  formatCurrency,
  formatCurrencyPrecise,
  formatLatency,
  formatNumber,
} from "@/lib/utils";
import type { OverviewStats } from "@/types";

export function StatsCards({ stats }: { stats: OverviewStats }) {
  const up = stats.cost_change_pct > 0;
  const items = [
    {
      label: "Total Cost",
      value: formatCurrency(stats.total_cost),
      change: stats.prev_total_cost > 0 ? stats.cost_change_pct : null,
    },
    { label: "Requests", value: formatNumber(stats.total_requests) },
    {
      label: "Avg Cost / Req",
      value: formatCurrencyPrecise(stats.avg_cost_per_request),
    },
    { label: "Avg Latency", value: formatLatency(stats.avg_latency) },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {items.map((item) => (
        <Card key={item.label}>
          <p className="text-sm text-slate-500">{item.label}</p>
          <p className="mt-1 text-2xl font-bold">{item.value}</p>
          {item.change != null && (
            <p
              className={`mt-1 flex items-center gap-1 text-xs font-medium ${
                up ? "text-red-600" : "text-green-600"
              }`}
            >
              {up ? (
                <ArrowUpRight className="h-3 w-3" />
              ) : (
                <ArrowDownRight className="h-3 w-3" />
              )}
              {Math.abs(item.change)}% vs previous
            </p>
          )}
        </Card>
      ))}
    </div>
  );
}
