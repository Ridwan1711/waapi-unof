import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import type { ScheduledMessage } from "@/types";

const KEY = ["scheduled-messages"] as const;

export interface CreateScheduledInput {
  device: string;
  run_at: string;
  to: string;
  text: string;
}

export function useScheduledMessages() {
  return useQuery({
    queryKey: KEY,
    queryFn: async () => (await api.get<ScheduledMessage[]>("/scheduled-messages/")).data,
  });
}

export function useCreateScheduled() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: CreateScheduledInput) =>
      (await api.post<ScheduledMessage>("/scheduled-messages/", input)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: KEY }),
  });
}

export function useCancelScheduled() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) =>
      (await api.post<ScheduledMessage>(`/scheduled-messages/${id}/cancel`)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: KEY }),
  });
}
