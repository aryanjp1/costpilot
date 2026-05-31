import { Card } from "@/components/ui";
import { formatCurrency } from "@/lib/utils";
import type { Budget } from "@/types";

function barColor(pct: number): string {
  if (pct >= 80) return "bg-red-500";
  if (pct >= 60) return "bg-yellow-500";
  return "bg-green-500";
}

export function BudgetProgress({
  budget,
  spend,
}: {
  budget: Budget;
  spend: number;
}) {
  const pct = budget.amount_usd > 0 ? (spend / budget.amount_usd) * 100 : 0;
  const clamped = Math.min(pct, 100);

  return (
    <Card>
      <div className="mb-2 flex items-center justify-between">
        <span className="text-sm font-semibold text-slate-700">
          {budget.name}
        </span>
        <span className="text-xs uppercase text-slate-400">
          {budget.period}
        </span>
      </div>
      <div className="h-3 rounded-full bg-slate-100">
        <div
          className={`h-3 rounded-full ${barColor(pct)}`}
          style={{ width: `${clamped}%` }}
        />
      </div>
      <p className="mt-2 text-sm text-slate-600">
        {formatCurrency(spend)} of {formatCurrency(budget.amount_usd)}{" "}
        <span className="text-slate-400">({pct.toFixed(0)}%)</span>
      </p>
    </Card>
  );
}
