import { Badge } from "@/components/ui";
import {
  formatCurrencyPrecise,
  formatDateTime,
  formatLatency,
  formatNumber,
} from "@/lib/utils";
import type { EventRow } from "@/types";

export function EventDetail({ event }: { event: EventRow }) {
  const fields = [
    ["Timestamp", formatDateTime(event.timestamp)],
    ["Model", event.model],
    ["Input tokens", formatNumber(event.input_tokens)],
    ["Output tokens", formatNumber(event.output_tokens)],
    ["Cost", formatCurrencyPrecise(event.cost_usd)],
    ["Latency", formatLatency(event.latency_ms)],
  ] as const;

  return (
    <div className="bg-slate-50 px-4 py-3 text-sm">
      <div className="grid grid-cols-2 gap-x-8 gap-y-2 sm:grid-cols-3">
        {fields.map(([label, value]) => (
          <div key={label}>
            <p className="text-xs text-slate-400">{label}</p>
            <p className="font-medium text-slate-700">{value}</p>
          </div>
        ))}
      </div>
      {event.error_message && (
        <p className="mt-3 rounded bg-red-50 p-2 text-xs text-red-700">
          {event.error_message}
        </p>
      )}
      {Object.keys(event.tags).length > 0 && (
        <div className="mt-3 flex flex-wrap gap-2">
          {Object.entries(event.tags).map(([key, value]) => (
            <Badge key={key}>
              {key}:{value}
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
}
