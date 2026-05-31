import { useParams } from "@tanstack/react-router";

export function useProjectId(): string {
  const params = useParams({ strict: false }) as { projectId?: string };
  return params.projectId ?? "";
}
