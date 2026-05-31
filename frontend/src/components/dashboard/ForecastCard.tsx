import { Minus, TrendingDown, TrendingUp } from "lucide-react";
import { Card } from "@/components/ui";
import { formatCurrency } from "@/lib/utils";
import type { Forecast } from "@/types";

const TREND = {
  increasing: { icon: TrendingUp, color: "text-red-600", label: "trending up" },
  decreasing: {
    icon: TrendingDown,
    color: "text-green-600",
    label: "trending down",
  },
  stable: { icon: Minus, color: "text-slate-500", label: "stable" },
  insufficient_data: {
    icon: Minus,
    color: "text-slate-400",
    label: "not enough data yet",
  },
};

export function ForecastCard({ forecast }: { forecast: Forecast }) {
  const trend = TREND[forecast.trend];
  const Icon = trend.icon;

  return (
    <Card>
      <h3 className="mb-2 text-sm font-semibold text-slate-700">Forecast</h3>
      <div className="flex items-baseline gap-2">
        <span className="text-3xl font-bold">
          {formatCurrency(forecast.projected_monthly)}
        </span>
        <span className="text-sm text-slate-500">/ month projected</span>
      </div>
      <div className={`mt-2 flex items-center gap-1.5 text-sm ${trend.color}`}>
        <Icon className="h-4 w-4" /> {trend.label}
      </div>
      <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
        <div>
          <p className="text-slate-500">Daily average</p>
          <p className="font-medium">
            {formatCurrency(forecast.current_daily_avg)}
          </p>
        </div>
        <div>
          <p className="text-slate-500">Projected weekly</p>
          <p className="font-medium">
            {formatCurrency(forecast.projected_weekly)}
          </p>
        </div>
      </div>
    </Card>
  );
}
