import { Trash2 } from "lucide-react";
import { Badge, Button, Card } from "@/components/ui";
import { formatCurrency } from "@/lib/utils";
import { useDeleteBudget } from "@/hooks/useBudgets";
import type { Budget } from "@/types";

export function BudgetCard({
  budget,
  projectId,
}: {
  budget: Budget;
  projectId: string;
}) {
  const deleteBudget = useDeleteBudget(projectId);

  return (
    <Card>
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-slate-800">{budget.name}</h3>
            {budget.is_active ? (
              <Badge color="green">Active</Badge>
            ) : (
              <Badge>Paused</Badge>
            )}
          </div>
          <p className="mt-1 text-sm text-slate-500">
            {formatCurrency(budget.amount_usd)} / {budget.period} · alert at{" "}
            {budget.alert_threshold_pct}%
          </p>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => deleteBudget.mutate(budget.id)}
          disabled={deleteBudget.isPending}
        >
          <Trash2 className="h-4 w-4 text-red-500" />
        </Button>
      </div>
    </Card>
  );
}
