import { BreakdownBars } from "./BreakdownBars";
import type { TagStat } from "@/types";

export function MemberBreakdown({ data }: { data: TagStat[] }) {
  return (
    <BreakdownBars
      title="Cost by team member"
      emptyHint="Tag your calls with user:<name> to see this breakdown."
      rows={data.map((t) => ({
        label: t.tag_value,
        cost: t.cost,
        requests: t.requests,
      }))}
    />
  );
}
