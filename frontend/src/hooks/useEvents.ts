import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { EventPage } from "@/types";

export interface EventFilters {
  page: number;
  pageSize: number;
  model?: string;
  status?: string;
}

export function useEvents(projectId: string, filters: EventFilters) {
  return useQuery({
    queryKey: ["events", projectId, filters],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: String(filters.page),
        page_size: String(filters.pageSize),
      });
      if (filters.model) params.set("model", filters.model);
      if (filters.status) params.set("status", filters.status);
      return (
        await api.get<EventPage>(
          `/api/projects/${projectId}/events?${params.toString()}`,
        )
      ).data;
    },
    enabled: Boolean(projectId),
    placeholderData: keepPreviousData,
  });
}
