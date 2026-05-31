import { useState } from "react";
import { Check, Copy } from "lucide-react";
import { Button, Dialog, Input, Label } from "@/components/ui";
import { apiError } from "@/lib/api";
import { useCreateApiKey } from "@/hooks/useApiKeys";

export function CreateKeyDialog({
  projectId,
  open,
  onClose,
}: {
  projectId: string;
  open: boolean;
  onClose: () => void;
}) {
  const [name, setName] = useState("");
  const [createdKey, setCreatedKey] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const createKey = useCreateApiKey(projectId);

  const handleCreate = async () => {
    const result = await createKey.mutateAsync(name || "Default");
    setCreatedKey(result.key);
  };

  const handleClose = () => {
    setName("");
    setCreatedKey(null);
    setCopied(false);
    onClose();
  };

  const copy = async () => {
    if (createdKey) {
      await navigator.clipboard.writeText(createdKey);
      setCopied(true);
    }
  };

  return (
    <Dialog open={open} onClose={handleClose} title="Create API key">
      {createdKey ? (
        <div className="space-y-4">
          <p className="rounded-md bg-yellow-50 p-3 text-sm text-yellow-800">
            Copy this key now. For security, it will not be shown again.
          </p>
          <div className="flex items-center gap-2">
            <code className="flex-1 truncate rounded-md bg-slate-100 px-3 py-2 font-mono text-sm">
              {createdKey}
            </code>
            <Button variant="secondary" size="sm" onClick={copy}>
              {copied ? (
                <Check className="h-4 w-4 text-green-600" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
            </Button>
          </div>
          <div className="flex justify-end">
            <Button onClick={handleClose}>Done</Button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div>
            <Label>Key name</Label>
            <Input
              placeholder="Production"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          {createKey.isError && (
            <p className="text-sm text-red-600">{apiError(createKey.error)}</p>
          )}
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={handleClose}>
              Cancel
            </Button>
            <Button onClick={handleCreate} disabled={createKey.isPending}>
              Create key
            </Button>
          </div>
        </div>
      )}
    </Dialog>
  );
}
