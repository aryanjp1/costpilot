import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { clearToken, getToken, setToken } from "@/lib/auth";
import type { User } from "@/types";

export function useCurrentUser() {
  return useQuery({
    queryKey: ["me"],
    queryFn: async () => (await api.get<User>("/api/auth/me")).data,
    enabled: Boolean(getToken()),
    retry: false,
  });
}

export function useLogin() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (payload: { email: string; password: string }) => {
      const { data } = await api.post<{ access_token: string }>(
        "/api/auth/login",
        payload,
      );
      setToken(data.access_token);
      return data;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["me"] }),
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: async (payload: {
      email: string;
      password: string;
      full_name?: string;
    }) => (await api.post<User>("/api/auth/register", payload)).data,
  });
}

export function logout() {
  clearToken();
  window.location.href = "/login";
}
