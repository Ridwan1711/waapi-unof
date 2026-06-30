import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/lib/api";
import type { Device } from "@/types";

const DEVICES_KEY = ["devices"] as const;

export function useDevices() {
  return useQuery({
    queryKey: DEVICES_KEY,
    queryFn: async () => (await api.get<Device[]>("/devices/")).data,
  });
}

export function useCreateDevice() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: { name: string }) =>
      (await api.post<Device>("/devices/", input)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: DEVICES_KEY }),
  });
}

export function useDeleteDevice() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => {
      await api.delete(`/devices/${id}`);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: DEVICES_KEY }),
  });
}

export function useLogoutDevice() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => (await api.post<Device>(`/devices/${id}/logout`)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: DEVICES_KEY }),
  });
}

export function useConnectDevice() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (id: string) => (await api.post<Device>(`/devices/${id}/connect`)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: DEVICES_KEY }),
  });
}

export interface DeviceQrResult {
  status: string;
  qr: string | null;
  phone: string;
}

/** Polls the device's current status + QR (robust alternative to SSE behind proxies). */
export function useDeviceQr(deviceId: string | null) {
  return useQuery({
    queryKey: ["device-qr", deviceId],
    enabled: Boolean(deviceId),
    refetchInterval: (query) => (query.state.data?.status === "connected" ? false : 2000),
    queryFn: async () => (await api.get<DeviceQrResult>(`/devices/${deviceId}/qr`)).data,
  });
}
