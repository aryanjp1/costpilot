import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Alert } from "@/types";

export function useAlerts(projectId: string, unreadOnly = false) {
  return useQuery({
    queryKey: ["alerts", projectId, unreadOnly],
    queryFn: async () =>
      (
        await api.get<Alert[]>(
          `/api/projects/${projectId}/alerts?unread_only=${unreadOnly}`,
        )
      ).data,
    enabled: Boolean(projectId),
  });
}

export function useMarkAlertRead(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (alertId: string) =>
      (await api.put<Alert>(`/api/alerts/${alertId}/read`)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["alerts", projectId] }),
  });
}
