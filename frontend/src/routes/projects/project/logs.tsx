import { useState } from "react";
import { useProjectId } from "@/hooks/useProjectId";
import { Button, Card, Select } from "@/components/ui";
import { Loading, PageHeader } from "@/components/common";
import { EventTable } from "@/components/logs/EventTable";
import { useEvents } from "@/hooks/useEvents";

const PAGE_SIZE = 25;

export function LogsPage() {
  const projectId = useProjectId();
  const [page, setPage] = useState(1);
  const [model, setModel] = useState("");
  const [status, setStatus] = useState("");

  const { data, isLoading } = useEvents(projectId, {
    page,
    pageSize: PAGE_SIZE,
    model: model || undefined,
    status: status || undefined,
  });

  const totalPages = data ? Math.ceil(data.total / PAGE_SIZE) : 1;

  return (
    <div className="space-y-4">
      <PageHeader title="Event logs" />

      <div className="flex flex-wrap gap-3">
        <Select
          value={status}
          onChange={(e) => {
            setStatus(e.target.value);
            setPage(1);
          }}
          className="w-40"
        >
          <option value="">All statuses</option>
          <option value="success">Success</option>
          <option value="error">Error</option>
        </Select>
        <input
          className="w-48 rounded-md border border-slate-300 px-3 py-2 text-sm"
          placeholder="Filter by model"
          value={model}
          onChange={(e) => {
            setModel(e.target.value);
            setPage(1);
          }}
        />
      </div>

      <Card className="overflow-x-auto p-0">
        {isLoading || !data ? (
          <Loading />
        ) : (
          <EventTable events={data.items} />
        )}
      </Card>

      {data && data.total > 0 && (
        <div className="flex items-center justify-between text-sm text-slate-500">
          <span>
            {data.total} events · page {page} of {totalPages}
          </span>
          <div className="flex gap-2">
            <Button
              variant="secondary"
              size="sm"
              disabled={page <= 1}
              onClick={() => setPage((p) => p - 1)}
            >
              Previous
            </Button>
            <Button
              variant="secondary"
              size="sm"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
