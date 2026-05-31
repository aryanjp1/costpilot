import {
  CartesianGrid,
  Line,
  LineChart,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card } from "@/components/ui";
import { formatChartTime, formatLatency } from "@/lib/utils";
import type { LatencyPoint, Period } from "@/types";

export function LatencyChart({
  data,
  period,
}: {
  data: LatencyPoint[];
  period: Period;
}) {
  const chartData = data.map((p) => ({
    ...p,
    label: formatChartTime(p.timestamp, period),
  }));

  return (
    <Card>
      <h3 className="mb-4 text-sm font-semibold text-slate-700">
        Latency (P50 / P95 / P99)
      </h3>
      <ResponsiveContainer width="100%" height={240}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis dataKey="label" tick={{ fontSize: 12 }} stroke="#94a3b8" />
          <YAxis
            tick={{ fontSize: 12 }}
            stroke="#94a3b8"
            tickFormatter={(v) => `${v}ms`}
          />
          <Tooltip formatter={(v: number) => formatLatency(v)} />
          <Legend />
          <Line type="monotone" dataKey="p50" name="P50" stroke="#22c55e" dot={false} />
          <Line type="monotone" dataKey="p95" name="P95" stroke="#f59e0b" dot={false} />
          <Line type="monotone" dataKey="p99" name="P99" stroke="#ef4444" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
}
