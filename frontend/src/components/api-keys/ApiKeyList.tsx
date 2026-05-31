import { Trash2 } from "lucide-react";
import { Badge, Button } from "@/components/ui";
import { formatDateTime } from "@/lib/utils";
import { useRevokeApiKey } from "@/hooks/useApiKeys";
import type { ApiKey } from "@/types";

export function ApiKeyList({
  keys,
  projectId,
}: {
  keys: ApiKey[];
  projectId: string;
}) {
  const revoke = useRevokeApiKey(projectId);

  if (keys.length === 0) {
    return <p className="text-sm text-slate-400">No API keys yet.</p>;
  }

  return (
    <div className="divide-y divide-slate-100">
      {keys.map((key) => (
        <div key={key.id} className="flex items-center justify-between py-3">
          <div>
            <div className="flex items-center gap-2">
              <span className="font-medium text-slate-800">{key.name}</span>
              {key.is_active ? (
                <Badge color="green">active</Badge>
              ) : (
                <Badge color="red">revoked</Badge>
              )}
            </div>
            <p className="mt-0.5 font-mono text-xs text-slate-500">
              {key.key_prefix}…
            </p>
            <p className="text-xs text-slate-400">
              Created {formatDateTime(key.created_at)}
              {key.last_used_at
                ? ` · last used ${formatDateTime(key.last_used_at)}`
                : " · never used"}
            </p>
          </div>
          {key.is_active && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => revoke.mutate(key.id)}
              disabled={revoke.isPending}
            >
              <Trash2 className="h-4 w-4 text-red-500" />
            </Button>
          )}
        </div>
      ))}
    </div>
  );
}
