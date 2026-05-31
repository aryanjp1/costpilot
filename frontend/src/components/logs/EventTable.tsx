import { Fragment, useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import { Badge } from "@/components/ui";
import {
  formatCurrencyPrecise,
  formatDateTime,
  formatLatency,
} from "@/lib/utils";
import type { EventRow } from "@/types";
import { EventDetail } from "./EventDetail";

export function EventTable({ events }: { events: EventRow[] }) {
  const [expanded, setExpanded] = useState<string | null>(null);

  if (events.length === 0) {
    return (
      <p className="px-4 py-8 text-center text-sm text-slate-400">
        No events match these filters.
      </p>
    );
  }

  return (
    <table className="w-full text-sm">
      <thead className="border-b border-slate-200 text-left text-xs uppercase text-slate-400">
        <tr>
          <th className="w-6" />
          <th className="px-3 py-2">Time</th>
          <th className="px-3 py-2">Model</th>
          <th className="px-3 py-2">Tokens</th>
          <th className="px-3 py-2">Cost</th>
          <th className="px-3 py-2">Latency</th>
          <th className="px-3 py-2">Status</th>
        </tr>
      </thead>
      <tbody>
        {events.map((event) => {
          const isOpen = expanded === event.id;
          return (
            <Fragment key={event.id}>
              <tr
                className="cursor-pointer border-b border-slate-100 hover:bg-slate-50"
                onClick={() => setExpanded(isOpen ? null : event.id)}
              >
                <td className="pl-3 text-slate-400">
                  {isOpen ? (
                    <ChevronDown className="h-4 w-4" />
                  ) : (
                    <ChevronRight className="h-4 w-4" />
                  )}
                </td>
                <td className="px-3 py-2 text-slate-600">
                  {formatDateTime(event.timestamp)}
                </td>
                <td className="px-3 py-2 font-medium">{event.model}</td>
                <td className="px-3 py-2 text-slate-600">
                  {event.input_tokens} / {event.output_tokens}
                </td>
                <td className="px-3 py-2">
                  {formatCurrencyPrecise(event.cost_usd)}
                </td>
                <td className="px-3 py-2 text-slate-600">
                  {formatLatency(event.latency_ms)}
                </td>
                <td className="px-3 py-2">
                  {event.status === "success" ? (
                    <Badge color="green">success</Badge>
                  ) : (
                    <Badge color="red">error</Badge>
                  )}
                </td>
              </tr>
              {isOpen && (
                <tr>
                  <td colSpan={7}>
                    <EventDetail event={event} />
                  </td>
                </tr>
              )}
            </Fragment>
          );
        })}
      </tbody>
    </table>
  );
}
