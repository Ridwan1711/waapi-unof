import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import type { ApiKey, ApiKeyCreated } from "@/types";

const KEY = ["api-keys"] as const;

export function useApiKeys() {
  return useQuery({
    queryKey: KEY,
    queryFn: async () => (await api.get<ApiKey[]>("/api-keys/")).data,
  });
}

export function useCreateApiKey() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: { name: string }) =>
      (await api.post<ApiKeyCreated>("/api-keys/", input)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: KEY }),
  });
}

export function useRevokeApiKey() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => (await api.post(`/api-keys/${id}/revoke`)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: KEY }),
  });
}
