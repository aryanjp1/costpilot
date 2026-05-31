import { useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import { Button, Card, Input, Label } from "@/components/ui";
import { PageHeader } from "@/components/common";
import { apiError } from "@/lib/api";
import { useCreateProject } from "@/hooks/useProjects";

export function NewProjectPage() {
  const navigate = useNavigate();
  const createProject = useCreateProject();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const project = await createProject.mutateAsync({
      name,
      description: description || undefined,
    });
    navigate({ to: "/projects/$projectId", params: { projectId: project.id } });
  };

  return (
    <div className="mx-auto max-w-lg">
      <PageHeader title="New project" />
      <Card>
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <Label>Name</Label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="My LLM App"
              required
            />
          </div>
          <div>
            <Label>Description</Label>
            <Input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional"
            />
          </div>
          {createProject.isError && (
            <p className="text-sm text-red-600">
              {apiError(createProject.error)}
            </p>
          )}
          <div className="flex justify-end gap-2">
            <Button
              type="button"
              variant="secondary"
              onClick={() => navigate({ to: "/projects" })}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={createProject.isPending}>
              Create project
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
