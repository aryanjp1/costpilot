import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card } from "@/components/ui";
import { formatChartTime, formatTokens } from "@/lib/utils";
import type { Period, TokenPoint } from "@/types";

export function TokenUsageChart({
  data,
  period,
}: {
  data: TokenPoint[];
  period: Period;
}) {
  const chartData = data.map((p) => ({
    ...p,
    label: formatChartTime(p.timestamp, period),
  }));

  return (
    <Card>
      <h3 className="mb-4 text-sm font-semibold text-slate-700">Token usage</h3>
      <ResponsiveContainer width="100%" height={240}>
        <AreaChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
          <XAxis dataKey="label" tick={{ fontSize: 12 }} stroke="#94a3b8" />
          <YAxis
            tick={{ fontSize: 12 }}
            stroke="#94a3b8"
            tickFormatter={formatTokens}
          />
          <Tooltip formatter={(v: number) => formatTokens(v)} />
          <Legend />
          <Area
            type="monotone"
            dataKey="input_tokens"
            name="Input"
            stackId="1"
            stroke="#6366f1"
            fill="#c7d2fe"
          />
          <Area
            type="monotone"
            dataKey="output_tokens"
            name="Output"
            stackId="1"
            stroke="#0ea5e9"
            fill="#bae6fd"
          />
        </AreaChart>
      </ResponsiveContainer>
    </Card>
  );
}
