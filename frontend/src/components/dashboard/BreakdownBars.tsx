import { Card } from "@/components/ui";
import { formatCurrencyPrecise, formatNumber } from "@/lib/utils";

interface Row {
  label: string;
  cost: number;
  requests: number;
}

export function BreakdownBars({
  title,
  rows,
  emptyHint,
}: {
  title: string;
  rows: Row[];
  emptyHint?: string;
}) {
  const max = Math.max(...rows.map((r) => r.cost), 0.0001);

  return (
    <Card>
      <h3 className="mb-4 text-sm font-semibold text-slate-700">{title}</h3>
      {rows.length === 0 ? (
        <p className="text-sm text-slate-400">
          {emptyHint ?? "No data for this period."}
        </p>
      ) : (
        <ul className="space-y-3">
          {rows.map((row) => (
            <li key={row.label}>
              <div className="mb-1 flex items-center justify-between text-sm">
                <span className="truncate font-medium text-slate-700">
                  {row.label}
                </span>
                <span className="text-slate-500">
                  {formatCurrencyPrecise(row.cost)}
                  <span className="ml-2 text-xs text-slate-400">
                    {formatNumber(row.requests)} req
                  </span>
                </span>
              </div>
              <div className="h-2 rounded-full bg-slate-100">
                <div
                  className="h-2 rounded-full bg-indigo-500"
                  style={{ width: `${(row.cost / max) * 100}%` }}
                />
              </div>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
