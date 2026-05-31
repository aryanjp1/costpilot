import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { granularityForPeriod } from "@/lib/utils";
import type {
  ErrorPoint,
  Forecast,
  LatencyPoint,
  ModelStat,
  OverviewStats,
  Period,
  TagStat,
  TimelinePoint,
  TokenPoint,
} from "@/types";

function base(projectId: string) {
  return `/api/projects/${projectId}/analytics`;
}

export function useOverview(projectId: string, period: Period) {
  return useQuery({
    queryKey: ["overview", projectId, period],
    queryFn: async () =>
      (
        await api.get<OverviewStats>(
          `${base(projectId)}/overview?period=${period}`,
        )
      ).data,
    enabled: Boolean(projectId),
  });
}

export function useCostTimeline(projectId: string, period: Period) {
  const granularity = granularityForPeriod(period);
  return useQuery({
    queryKey: ["cost-timeline", projectId, period],
    queryFn: async () =>
      (
        await api.get<TimelinePoint[]>(
          `${base(projectId)}/cost-timeline?period=${period}&granularity=${granularity}`,
        )
      ).data,
    enabled: Boolean(projectId),
  });
}

export function useModelBreakdown(projectId: string, period: Period) {
  return useQuery({
    queryKey: ["models", projectId, period],
    queryFn: async () =>
      (await api.get<ModelStat[]>(`${base(projectId)}/models?period=${period}`))
        .data,
    enabled: Boolean(projectId),
  });
}

export function useTagBreakdown(
  projectId: string,
  period: Period,
  tagKey: string,
) {
  return useQuery({
    queryKey: ["tags", projectId, period, tagKey],
    queryFn: async () =>
      (
        await api.get<TagStat[]>(
          `${base(projectId)}/tags?period=${period}&tag_key=${tagKey}`,
        )
      ).data,
    enabled: Boolean(projectId),
  });
}

export function useMemberBreakdown(projectId: string, period: Period) {
  return useQuery({
    queryKey: ["member-breakdown", projectId, period],
    queryFn: async () =>
      (await api.get<TagStat[]>(`${base(projectId)}/members?period=${period}`))
        .data,
    enabled: Boolean(projectId),
  });
}

export function useTokenTimeline(projectId: string, period: Period) {
  const granularity = granularityForPeriod(period);
  return useQuery({
    queryKey: ["tokens", projectId, period],
    queryFn: async () =>
      (
        await api.get<TokenPoint[]>(
          `${base(projectId)}/tokens?period=${period}&granularity=${granularity}`,
        )
      ).data,
    enabled: Boolean(projectId),
  });
}

export function useLatencyTimeline(projectId: string, period: Period) {
  const granularity = granularityForPeriod(period);
  return useQuery({
    queryKey: ["latency", projectId, period],
    queryFn: async () =>
      (
        await api.get<LatencyPoint[]>(
          `${base(projectId)}/latency?period=${period}&granularity=${granularity}`,
        )
      ).data,
    enabled: Boolean(projectId),
  });
}

export function useErrorTimeline(projectId: string, period: Period) {
  const granularity = granularityForPeriod(period);
  return useQuery({
    queryKey: ["errors", projectId, period],
    queryFn: async () =>
      (
        await api.get<ErrorPoint[]>(
          `${base(projectId)}/errors?period=${period}&granularity=${granularity}`,
        )
      ).data,
    enabled: Boolean(projectId),
  });
}

export function useForecast(projectId: string) {
  return useQuery({
    queryKey: ["forecast", projectId],
    queryFn: async () =>
      (await api.get<Forecast>(`/api/projects/${projectId}/forecast`)).data,
    enabled: Boolean(projectId),
  });
}
