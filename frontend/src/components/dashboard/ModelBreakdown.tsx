import { BreakdownBars } from "./BreakdownBars";
import type { ModelStat } from "@/types";

export function ModelBreakdown({ data }: { data: ModelStat[] }) {
  return (
    <BreakdownBars
      title="Cost by model"
      rows={data.map((m) => ({
        label: m.model,
        cost: m.cost,
        requests: m.requests,
      }))}
    />
  );
}
