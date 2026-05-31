import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import type { Member, Project } from "@/types";

export function useProjects() {
  return useQuery({
    queryKey: ["projects"],
    queryFn: async () => (await api.get<Project[]>("/api/projects")).data,
  });
}

export function useProject(projectId: string) {
  return useQuery({
    queryKey: ["project", projectId],
    queryFn: async () =>
      (await api.get<Project>(`/api/projects/${projectId}`)).data,
    enabled: Boolean(projectId),
  });
}

export function useCreateProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { name: string; description?: string }) =>
      (await api.post<Project>("/api/projects", payload)).data,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["projects"] }),
  });
}

export function useDeleteProject() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (projectId: string) =>
      api.delete(`/api/projects/${projectId}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["projects"] }),
  });
}

export function useMembers(projectId: string) {
  return useQuery({
    queryKey: ["members", projectId],
    queryFn: async () =>
      (await api.get<Member[]>(`/api/projects/${projectId}/members`)).data,
    enabled: Boolean(projectId),
  });
}

export function useInviteMember(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { email: string; role: string }) =>
      (
        await api.post<Member>(
          `/api/projects/${projectId}/members/invite`,
          payload,
        )
      ).data,
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ["members", projectId] }),
  });
}

export function useRemoveMember(projectId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (memberId: string) =>
      api.delete(`/api/projects/${projectId}/members/${memberId}`),
    onSuccess: () =>
      qc.invalidateQueries({ queryKey: ["members", projectId] }),
  });
}
