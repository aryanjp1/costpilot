import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card } from "@/components/ui";
import { formatChartTime, formatNumber } from "@/lib/utils";
import type { Period, TimelinePoint } from "@/types";

export function RequestsChart({
  data,
  period,
}: {
  data: TimelinePoint[];
  period: Period;
}) {
  const chartData = data.map((p) => ({
    ...p,
    label: formatChartTime(p.timestamp, period),
  }));

  return (
    <Card>
      <h3 className="mb-4 text-sm font-semibold text-slate-700">Requests</h3>
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis dataKey="label" tick={{ fontSize: 12 }} stroke="#94a3b8" />
          <YAxis tick={{ fontSize: 12 }} stroke="#94a3b8" />
          <Tooltip formatter={(v: number) => [formatNumber(v), "Requests"]} />
          <Bar dataKey="requests" fill="#818cf8" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </Card>
  );
}
