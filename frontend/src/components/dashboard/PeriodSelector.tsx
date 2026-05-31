import { cn } from "@/lib/utils";
import type { Period } from "@/types";

const PERIODS: Period[] = ["24h", "7d", "30d", "90d"];

export function PeriodSelector({
  value,
  onChange,
}: {
  value: Period;
  onChange: (period: Period) => void;
}) {
  return (
    <div className="inline-flex rounded-lg border border-slate-200 bg-white p-1">
      {PERIODS.map((period) => (
        <button
          key={period}
          onClick={() => onChange(period)}
          className={cn(
            "rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
            value === period
              ? "bg-indigo-600 text-white"
              : "text-slate-600 hover:bg-slate-100",
          )}
        >
          {period}
        </button>
      ))}
    </div>
  );
}
