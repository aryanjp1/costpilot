import { useNavigate, useParams } from "@tanstack/react-router";
import { useProjects } from "@/hooks/useProjects";
import { Select } from "@/components/ui";

export function ProjectSwitcher() {
  const navigate = useNavigate();
  const params = useParams({ strict: false }) as { projectId?: string };
  const { data: projects } = useProjects();

  if (!projects || projects.length === 0) {
    return <div className="text-sm font-medium text-slate-500">Dashboard</div>;
  }

  return (
    <Select
      value={params.projectId ?? ""}
      onChange={(e) =>
        navigate({
          to: "/projects/$projectId",
          params: { projectId: e.target.value },
        })
      }
      className="w-56"
    >
      <option value="" disabled>
        Select a project
      </option>
      {projects.map((p) => (
        <option key={p.id} value={p.id}>
          {p.name}
        </option>
      ))}
    </Select>
  );
}
