import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button, Input, Label, Select } from "@/components/ui";
import { apiError } from "@/lib/api";
import { useCreateBudget } from "@/hooks/useBudgets";

const schema = z.object({
  name: z.string().min(1, "Name is required"),
  period: z.enum(["daily", "weekly", "monthly"]),
  amount_usd: z.coerce.number().positive("Must be greater than 0"),
  alert_threshold_pct: z.coerce.number().min(1).max(100),
});

type FormValues = z.infer<typeof schema>;

export function BudgetForm({
  projectId,
  onDone,
}: {
  projectId: string;
  onDone: () => void;
}) {
  const createBudget = useCreateBudget(projectId);
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { period: "monthly", alert_threshold_pct: 80 },
  });

  const onSubmit = handleSubmit(async (values) => {
    await createBudget.mutateAsync(values);
    onDone();
  });

  return (
    <form onSubmit={onSubmit} className="space-y-4">
      <div>
        <Label>Name</Label>
        <Input placeholder="Monthly cap" {...register("name")} />
        {errors.name && (
          <p className="mt-1 text-xs text-red-600">{errors.name.message}</p>
        )}
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>Period</Label>
          <Select {...register("period")}>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </Select>
        </div>
        <div>
          <Label>Amount (USD)</Label>
          <Input type="number" step="0.01" {...register("amount_usd")} />
          {errors.amount_usd && (
            <p className="mt-1 text-xs text-red-600">
              {errors.amount_usd.message}
            </p>
          )}
        </div>
      </div>
      <div>
        <Label>Alert threshold (%)</Label>
        <Input type="number" {...register("alert_threshold_pct")} />
      </div>
      {createBudget.isError && (
        <p className="text-sm text-red-600">{apiError(createBudget.error)}</p>
      )}
      <div className="flex justify-end gap-2">
        <Button type="button" variant="secondary" onClick={onDone}>
          Cancel
        </Button>
        <Button type="submit" disabled={createBudget.isPending}>
          Create budget
        </Button>
      </div>
    </form>
  );
}
