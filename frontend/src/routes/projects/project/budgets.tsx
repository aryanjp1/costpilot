import { useState } from "react";
import { useProjectId } from "@/hooks/useProjectId";
import { Plus } from "lucide-react";
import { Button, Dialog } from "@/components/ui";
import { EmptyState, Loading, PageHeader } from "@/components/common";
import { BudgetForm } from "@/components/budgets/BudgetForm";
import { BudgetCard } from "@/components/budgets/BudgetCard";
import { useBudgets } from "@/hooks/useBudgets";

export function BudgetsPage() {
  const projectId = useProjectId();
  const { data, isLoading } = useBudgets(projectId);
  const [open, setOpen] = useState(false);

  return (
    <div className="space-y-6">
      <PageHeader title="Budgets">
        <Button onClick={() => setOpen(true)}>
          <Plus className="h-4 w-4" /> New budget
        </Button>
      </PageHeader>

      {isLoading ? (
        <Loading />
      ) : !data || data.length === 0 ? (
        <EmptyState
          title="No budgets configured"
          description="Set a daily, weekly, or monthly budget to get alerted before costs run away."
          action={<Button onClick={() => setOpen(true)}>Create a budget</Button>}
        />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          {data.map((budget) => (
            <BudgetCard key={budget.id} budget={budget} projectId={projectId} />
          ))}
        </div>
      )}

      <Dialog open={open} onClose={() => setOpen(false)} title="New budget">
        <BudgetForm projectId={projectId} onDone={() => setOpen(false)} />
      </Dialog>
    </div>
  );
}
