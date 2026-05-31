import { useState } from "react";
import { useProjectId } from "@/hooks/useProjectId";
import { Card } from "@/components/ui";
import { Loading, PageHeader } from "@/components/common";
import { PeriodSelector } from "@/components/dashboard/PeriodSelector";
import { ModelBreakdown } from "@/components/dashboard/ModelBreakdown";
import {
  formatCurrencyPrecise,
  formatLatency,
  formatNumber,
  formatTokens,
} from "@/lib/utils";
import { useModelBreakdown } from "@/hooks/useAnalytics";
import type { Period } from "@/types";

export function ModelsPage() {
  const projectId = useProjectId();
  const [period, setPeriod] = useState<Period>("7d");
  const { data, isLoading } = useModelBreakdown(projectId, period);

  return (
    <div className="space-y-6">
      <PageHeader title="Models">
        <PeriodSelector value={period} onChange={setPeriod} />
      </PageHeader>

      {isLoading || !data ? (
        <Loading />
      ) : (
        <>
          <ModelBreakdown data={data} />
          <Card>
            <table className="w-full text-sm">
              <thead className="border-b border-slate-200 text-left text-xs uppercase text-slate-400">
                <tr>
                  <th className="px-3 py-2">Model</th>
                  <th className="px-3 py-2">Cost</th>
                  <th className="px-3 py-2">Requests</th>
                  <th className="px-3 py-2">Avg latency</th>
                  <th className="px-3 py-2">Input</th>
                  <th className="px-3 py-2">Output</th>
                </tr>
              </thead>
              <tbody>
                {data.map((m) => (
                  <tr key={m.model} className="border-b border-slate-100">
                    <td className="px-3 py-2 font-medium">{m.model}</td>
                    <td className="px-3 py-2">
                      {formatCurrencyPrecise(m.cost)}
                    </td>
                    <td className="px-3 py-2">{formatNumber(m.requests)}</td>
                    <td className="px-3 py-2">{formatLatency(m.avg_latency)}</td>
                    <td className="px-3 py-2">{formatTokens(m.input_tokens)}</td>
                    <td className="px-3 py-2">
                      {formatTokens(m.output_tokens)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </>
      )}
    </div>
  );
}
