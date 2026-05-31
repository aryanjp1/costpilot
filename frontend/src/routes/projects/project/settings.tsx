import { useState } from "react";
import { useProjectId } from "@/hooks/useProjectId";
import { useNavigate } from "@tanstack/react-router";
import { Plus } from "lucide-react";
import { Button, Card } from "@/components/ui";
import { Loading, PageHeader } from "@/components/common";
import { ApiKeyList } from "@/components/api-keys/ApiKeyList";
import { CreateKeyDialog } from "@/components/api-keys/CreateKeyDialog";
import { useApiKeys } from "@/hooks/useApiKeys";
import { useDeleteProject, useProject } from "@/hooks/useProjects";

export function SettingsPage() {
  const projectId = useProjectId();
  const navigate = useNavigate();
  const project = useProject(projectId);
  const keys = useApiKeys(projectId);
  const deleteProject = useDeleteProject();
  const [dialogOpen, setDialogOpen] = useState(false);

  const onDelete = async () => {
    if (!confirm("Delete this project? This cannot be undone.")) return;
    await deleteProject.mutateAsync(projectId);
    navigate({ to: "/projects" });
  };

  return (
    <div className="space-y-6">
      <PageHeader title="Settings" />

      <Card>
        <h3 className="text-sm font-semibold text-slate-700">Project</h3>
        {project.data ? (
          <div className="mt-2 text-sm text-slate-600">
            <p>
              <span className="text-slate-400">Name:</span> {project.data.name}
            </p>
            <p>
              <span className="text-slate-400">Slug:</span> {project.data.slug}
            </p>
            {project.data.description && (
              <p>
                <span className="text-slate-400">Description:</span>{" "}
                {project.data.description}
              </p>
            )}
          </div>
        ) : (
          <Loading />
        )}
      </Card>

      <Card>
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-700">API keys</h3>
          <Button size="sm" onClick={() => setDialogOpen(true)}>
            <Plus className="h-4 w-4" /> Create key
          </Button>
        </div>
        {keys.isLoading || !keys.data ? (
          <Loading />
        ) : (
          <ApiKeyList keys={keys.data} projectId={projectId} />
        )}
      </Card>

      <Card className="border-red-200">
        <h3 className="text-sm font-semibold text-red-700">Danger zone</h3>
        <p className="mt-1 text-sm text-slate-500">
          Deleting a project removes all of its events, budgets, and keys.
        </p>
        <Button variant="danger" className="mt-3" onClick={onDelete}>
          Delete project
        </Button>
      </Card>

      <CreateKeyDialog
        projectId={projectId}
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
      />
    </div>
  );
}
