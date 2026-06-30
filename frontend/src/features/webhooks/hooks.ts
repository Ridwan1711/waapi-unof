import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import type { Paginated, Webhook, WebhookDelivery } from "@/types";

const KEY = ["webhooks"] as const;

export function useWebhooks() {
  return useQuery({
    queryKey: KEY,
    queryFn: async () => (await api.get<Webhook[]>("/webhooks/")).data,
  });
}

export function useCreateWebhook() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: { url: string; events: string[]; description?: string }) =>
      (await api.post<Webhook>("/webhooks/", input)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: KEY }),
  });
}

export function useDeleteWebhook() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/webhooks/${id}`);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: KEY }),
  });
}

export function useWebhookDeliveries(id: string | null) {
  return useQuery({
    queryKey: ["webhook-deliveries", id],
    enabled: Boolean(id),
    queryFn: async () =>
      (await api.get<Paginated<WebhookDelivery>>(`/webhooks/${id}/deliveries`)).data,
  });
}
