import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { ApiKey, CreatedApiKey } from "@/types";

export function useApiKeys(projectId: string) {
  return useQuery({
    queryKey: ["api-keys", projectId],
    queryFn: async () =>
      (await api.get<ApiKey[]>(`/api/projects/${projectId}/api-keys`)).data,
    enabled: Boolean(projectId),
  });
}

export function useCreateApiKey(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (name: string) =>
      (
        await api.post<CreatedApiKey>(
          `/api/projects/${projectId}/api-keys`,
          { name },
        )
      ).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["api-keys", projectId] }),
  });
}

export function useRevokeApiKey(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (keyId: string) => api.delete(`/api/api-keys/${keyId}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["api-keys", projectId] }),
  });
}
