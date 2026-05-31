import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card } from "@/components/ui";
import { formatChartTime, formatCurrencyPrecise } from "@/lib/utils";
import type { Period, TimelinePoint } from "@/types";

export function CostTimeline({
  data,
  period,
}: {
  data: TimelinePoint[];
  period: Period;
}) {
  const chartData = data.map((point) => ({
    ...point,
    label: formatChartTime(point.timestamp, period),
  }));

  return (
    <Card>
      <h3 className="mb-4 text-sm font-semibold text-slate-700">
        Cost over time
      </h3>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis dataKey="label" tick={{ fontSize: 12 }} stroke="#94a3b8" />
          <YAxis
            tick={{ fontSize: 12 }}
            stroke="#94a3b8"
            tickFormatter={(v) => `$${v}`}
          />
          <Tooltip
            formatter={(value: number, name: string) =>
              name === "cost"
                ? [formatCurrencyPrecise(value), "Cost"]
                : [value, "Requests"]
            }
          />
          <Line
            type="monotone"
            dataKey="cost"
            stroke="#4f46e5"
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}
