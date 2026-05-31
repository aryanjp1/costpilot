import { Lightbulb } from "lucide-react";
import { Badge, Card } from "@/components/ui";
import { SavingsEstimate } from "./SavingsEstimate";
import type { Recommendation } from "@/types";

export function RecommendationCard({ rec }: { rec: Recommendation }) {
  return (
    <Card>
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="rounded-lg bg-indigo-50 p-2">
            <Lightbulb className="h-5 w-5 text-indigo-600" />
          </div>
          <div>
            <h3 className="font-semibold text-slate-800">{rec.title}</h3>
            <p className="mt-1 text-sm text-slate-600">{rec.description}</p>
            <div className="mt-2 flex flex-wrap items-center gap-2">
              {rec.model_from && rec.model_to && (
                <Badge color="indigo">
                  {rec.model_from} → {rec.model_to}
                </Badge>
              )}
              {rec.affected_tags.map((tag) => (
                <Badge key={tag}>{tag}</Badge>
              ))}
            </div>
          </div>
        </div>
        <SavingsEstimate amount={rec.estimated_savings_usd} />
      </div>
    </Card>
  );
}
