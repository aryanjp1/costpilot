import { useProjectId } from "@/hooks/useProjectId";
import { Badge, Button, Card } from "@/components/ui";
import { EmptyState, Loading, PageHeader } from "@/components/common";
import { formatCurrency, formatDateTime } from "@/lib/utils";
import { useAlerts, useMarkAlertRead } from "@/hooks/useAlerts";

export function AlertsPage() {
  const projectId = useProjectId();
  const { data, isLoading } = useAlerts(projectId);
  const markRead = useMarkAlertRead(projectId);

  if (isLoading) return <Loading />;

  return (
    <div className="space-y-4">
      <PageHeader title="Alerts" />

      {!data || data.length === 0 ? (
        <EmptyState
          title="No alerts"
          description="Alerts appear here when your spending approaches or exceeds a budget."
        />
      ) : (
        data.map((alert) => (
          <Card key={alert.id}>
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="flex items-center gap-2">
                  <Badge
                    color={alert.alert_type === "exceeded" ? "red" : "yellow"}
                  >
                    {alert.alert_type}
                  </Badge>
                  {!alert.is_read && <Badge color="indigo">new</Badge>}
                </div>
                <h3 className="mt-2 font-semibold text-slate-800">
                  {alert.title}
                </h3>
                <p className="mt-1 text-sm text-slate-600">
                  {alert.description}
                </p>
                <p className="mt-2 text-xs text-slate-400">
                  {formatCurrency(alert.current_spend)} of{" "}
                  {formatCurrency(alert.budget_amount)} ·{" "}
                  {formatDateTime(alert.created_at)}
                </p>
              </div>
              {!alert.is_read && (
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => markRead.mutate(alert.id)}
                >
                  Mark read
                </Button>
              )}
            </div>
          </Card>
        ))
      )}
    </div>
  );
}
