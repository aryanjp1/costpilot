import { useState } from "react";
import { useProjectId } from "@/hooks/useProjectId";
import { Loading } from "@/components/common";
import { PeriodSelector } from "@/components/dashboard/PeriodSelector";
import { StatsCards } from "@/components/dashboard/StatsCards";
import { CostTimeline } from "@/components/dashboard/CostTimeline";
import { ModelBreakdown } from "@/components/dashboard/ModelBreakdown";
import { FeatureBreakdown } from "@/components/dashboard/FeatureBreakdown";
import { ForecastCard } from "@/components/dashboard/ForecastCard";
import { RequestsChart } from "@/components/dashboard/RequestsChart";
import { BudgetAlertBanner } from "@/components/budgets/BudgetAlertBanner";
import { RecommendationCard } from "@/components/recommendations/RecommendationCard";
import {
  useCostTimeline,
  useForecast,
  useModelBreakdown,
  useOverview,
  useTagBreakdown,
} from "@/hooks/useAnalytics";
import { useAlerts } from "@/hooks/useAlerts";
import { useRecommendations } from "@/hooks/useRecommendations";
import type { Period } from "@/types";

export function ProjectDashboard() {
  const projectId = useProjectId();
  const [period, setPeriod] = useState<Period>("7d");

  const overview = useOverview(projectId, period);
  const timeline = useCostTimeline(projectId, period);
  const models = useModelBreakdown(projectId, period);
  const features = useTagBreakdown(projectId, period, "feature");
  const forecast = useForecast(projectId);
  const alerts = useAlerts(projectId);
  const recommendations = useRecommendations(projectId);

  if (overview.isLoading || !overview.data) return <Loading />;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Overview</h1>
        <PeriodSelector value={period} onChange={setPeriod} />
      </div>

      {alerts.data && (
        <BudgetAlertBanner alerts={alerts.data} projectId={projectId} />
      )}

      <StatsCards stats={overview.data} />

      {timeline.data && (
        <CostTimeline data={timeline.data} period={period} />
      )}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {models.data && <ModelBreakdown data={models.data} />}
        {features.data && <FeatureBreakdown data={features.data} />}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {forecast.data && <ForecastCard forecast={forecast.data} />}
        {timeline.data && <RequestsChart data={timeline.data} period={period} />}
      </div>

      {recommendations.data && recommendations.data.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold">Recommendations</h2>
          {recommendations.data.slice(0, 3).map((rec, i) => (
            <RecommendationCard key={i} rec={rec} />
          ))}
        </div>
      )}
    </div>
  );
}
