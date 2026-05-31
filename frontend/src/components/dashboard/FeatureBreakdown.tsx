import { BreakdownBars } from "./BreakdownBars";
import type { TagStat } from "@/types";

export function FeatureBreakdown({ data }: { data: TagStat[] }) {
  return (
    <BreakdownBars
      title="Cost by feature"
      emptyHint="Tag your calls with feature:<name> to see this breakdown."
      rows={data.map((t) => ({
        label: t.tag_value,
        cost: t.cost,
        requests: t.requests,
      }))}
    />
  );
}
