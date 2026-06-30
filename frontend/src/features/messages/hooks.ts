import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";
import type { Message, Paginated } from "@/types";

export interface MessageFilters {
  device?: string;
  direction?: string;
  status?: string;
}

export function useMessages(filters: MessageFilters = {}) {
  return useQuery({
    queryKey: ["messages", filters],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.device) params.set("device", filters.device);
      if (filters.direction) params.set("direction", filters.direction);
      if (filters.status) params.set("status", filters.status);
      const qs = params.toString();
      return (await api.get<Paginated<Message>>(`/messages/${qs ? `?${qs}` : ""}`)).data;
    },
  });
}
