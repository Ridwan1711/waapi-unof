import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import type { AutoReplyRule } from "@/types";

const KEY = ["auto-reply-rules"] as const;

export interface CreateRuleInput {
  name: string;
  match_type: string;
  pattern: string;
  response_body: string;
  priority?: number;
  case_sensitive?: boolean;
}

export function useAutoReplyRules() {
  return useQuery({
    queryKey: KEY,
    queryFn: async () => (await api.get<AutoReplyRule[]>("/auto-reply-rules/")).data,
  });
}

export function useCreateRule() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: CreateRuleInput) =>
      (await api.post<AutoReplyRule>("/auto-reply-rules/", input)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: KEY }),
  });
}

export function useUpdateRule() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ id, ...patch }: { id: string } & Partial<AutoReplyRule>) =>
      (await api.patch<AutoReplyRule>(`/auto-reply-rules/${id}`, patch)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: KEY }),
  });
}

export function useDeleteRule() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/auto-reply-rules/${id}`);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: KEY }),
  });
}
