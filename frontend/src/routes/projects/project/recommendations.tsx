import { useProjectId } from "@/hooks/useProjectId";
import { EmptyState, Loading, PageHeader } from "@/components/common";
import { RecommendationCard } from "@/components/recommendations/RecommendationCard";
import { useRecommendations } from "@/hooks/useRecommendations";

export function RecommendationsPage() {
  const projectId = useProjectId();
  const { data, isLoading } = useRecommendations(projectId);

  if (isLoading) return <Loading />;

  return (
    <div className="space-y-4">
      <PageHeader title="Recommendations" />

      {!data || data.length === 0 ? (
        <EmptyState
          title="No recommendations yet"
          description="As more usage data comes in, CostPilot will surface ways to cut your spend."
        />
      ) : (
        data.map((rec, i) => <RecommendationCard key={i} rec={rec} />)
      )}
    </div>
  );
}
