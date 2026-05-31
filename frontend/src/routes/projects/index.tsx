import { Link } from "@tanstack/react-router";
import { Plus } from "lucide-react";
import { Button, Card } from "@/components/ui";
import { EmptyState, Loading, PageHeader } from "@/components/common";
import { formatDateTime } from "@/lib/utils";
import { useProjects } from "@/hooks/useProjects";

export function ProjectsPage() {
  const { data: projects, isLoading } = useProjects();

  if (isLoading) return <Loading />;

  return (
    <div>
      <PageHeader title="Projects">
        <Link to="/projects/new">
          <Button>
            <Plus className="h-4 w-4" /> New project
          </Button>
        </Link>
      </PageHeader>

      {!projects || projects.length === 0 ? (
        <EmptyState
          title="No projects yet"
          description="Create a project to start tracking your LLM spending."
          action={
            <Link to="/projects/new">
              <Button>Create your first project</Button>
            </Link>
          }
        />
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
            <Link
              key={project.id}
              to="/projects/$projectId"
              params={{ projectId: project.id }}
            >
              <Card className="transition-shadow hover:shadow-md">
                <h3 className="font-semibold text-slate-800">{project.name}</h3>
                {project.description && (
                  <p className="mt-1 text-sm text-slate-500">
                    {project.description}
                  </p>
                )}
                <p className="mt-3 text-xs text-slate-400">
                  Created {formatDateTime(project.created_at)}
                </p>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
