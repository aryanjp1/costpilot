import { useState } from "react";
import { useProjectId } from "@/hooks/useProjectId";
import { Loading, PageHeader } from "@/components/common";
import { PeriodSelector } from "@/components/dashboard/PeriodSelector";
import { FeatureBreakdown } from "@/components/dashboard/FeatureBreakdown";
import { TokenUsageChart } from "@/components/dashboard/TokenUsageChart";
import { useTagBreakdown, useTokenTimeline } from "@/hooks/useAnalytics";
import type { Period } from "@/types";

export function FeaturesPage() {
  const projectId = useProjectId();
  const [period, setPeriod] = useState<Period>("7d");
  const features = useTagBreakdown(projectId, period, "feature");
  const tokens = useTokenTimeline(projectId, period);

  return (
    <div className="space-y-6">
      <PageHeader title="Features">
        <PeriodSelector value={period} onChange={setPeriod} />
      </PageHeader>

      {features.isLoading || !features.data ? (
        <Loading />
      ) : (
        <>
          <FeatureBreakdown data={features.data} />
          {tokens.data && (
            <TokenUsageChart data={tokens.data} period={period} />
          )}
        </>
      )}
    </div>
  );
}
