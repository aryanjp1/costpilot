import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Recommendation } from "@/types";

export function useRecommendations(projectId: string) {
  return useQuery({
    queryKey: ["recommendations", projectId],
    queryFn: async () =>
      (
        await api.get<Recommendation[]>(
          `/api/projects/${projectId}/recommendations`,
        )
      ).data,
    enabled: Boolean(projectId),
  });
}
