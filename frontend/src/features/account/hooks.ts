import { useQuery } from "@tanstack/react-query";

import { api } from "@/lib/api";
import type { MeResponse } from "@/types";

export function useMe() {
  return useQuery({
    queryKey: ["me"],
    queryFn: async () => (await api.get<MeResponse>("/auth/me")).data,
  });
}
