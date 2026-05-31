import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Budget } from "@/types";

export interface BudgetInput {
  name: string;
  period: string;
  amount_usd: number;
  alert_threshold_pct: number;
}

export function useBudgets(projectId: string) {
  return useQuery({
    queryKey: ["budgets", projectId],
    queryFn: async () =>
      (await api.get<Budget[]>(`/api/projects/${projectId}/budgets`)).data,
    enabled: Boolean(projectId),
  });
}

export function useCreateBudget(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: BudgetInput) =>
      (await api.post<Budget>(`/api/projects/${projectId}/budgets`, payload))
        .data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["budgets", projectId] }),
  });
}

export function useUpdateBudget(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async ({
      id,
      ...payload
    }: Partial<BudgetInput> & { id: string; is_active?: boolean }) =>
      (await api.put<Budget>(`/api/budgets/${id}`, payload)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["budgets", projectId] }),
  });
}

export function useDeleteBudget(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => api.delete(`/api/budgets/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["budgets", projectId] }),
  });
}
