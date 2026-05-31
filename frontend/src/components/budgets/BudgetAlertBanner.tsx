import { AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";
import { useMarkAlertRead } from "@/hooks/useAlerts";
import type { Alert } from "@/types";

export function BudgetAlertBanner({
  alerts,
  projectId,
}: {
  alerts: Alert[];
  projectId: string;
}) {
  const markRead = useMarkAlertRead(projectId);
  const unread = alerts.filter((a) => !a.is_read);
  if (unread.length === 0) return null;

  return (
    <div className="space-y-2">
      {unread.map((alert) => (
        <div
          key={alert.id}
          className={cn(
            "flex items-start justify-between gap-4 rounded-lg border p-3 text-sm",
            alert.alert_type === "exceeded"
              ? "border-red-200 bg-red-50 text-red-800"
              : "border-yellow-200 bg-yellow-50 text-yellow-800",
          )}
        >
          <div className="flex items-start gap-2">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
            <div>
              <p className="font-medium">{alert.title}</p>
              <p className="text-xs opacity-80">{alert.description}</p>
            </div>
          </div>
          <button
            className="text-xs font-medium underline"
            onClick={() => markRead.mutate(alert.id)}
          >
            Dismiss
          </button>
        </div>
      ))}
    </div>
  );
}
