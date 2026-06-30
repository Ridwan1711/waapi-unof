"use client";

import * as React from "react";

import { env } from "@/lib/env";
import { getToken } from "@/lib/token";

interface DeviceEventsState {
  status: string | null;
  qr: string | null;
  phone: string | null;
}

/**
 * Subscribes to a device's SSE stream and exposes the latest QR + status.
 * Pass `null` to disconnect (e.g. when a dialog is closed).
 */
export function useDeviceEvents(deviceId: string | null): DeviceEventsState {
  const [state, setState] = React.useState<DeviceEventsState>({
    status: null,
    qr: null,
    phone: null,
  });

  React.useEffect(() => {
    if (!deviceId) return;

    const token = getToken();
    const url = `${env.apiBaseUrl}/v1/devices/${deviceId}/events?token=${encodeURIComponent(token ?? "")}`;
    const source = new EventSource(url);

    source.addEventListener("status", (event) => {
      try {
        const data = JSON.parse((event as MessageEvent).data);
        setState((prev) => ({
          status: data.status ?? prev.status,
          phone: data.phone ?? prev.phone,
          qr: data.status === "qr" ? prev.qr : null,
        }));
      } catch {
        /* ignore malformed frame */
      }
    });

    source.onmessage = (event) => {
      try {
        const evt = JSON.parse(event.data);
        if (evt.type === "qr" && evt.data?.qr) {
          setState((prev) => ({ ...prev, status: "qr", qr: evt.data.qr }));
        } else if (evt.type === "ready") {
          setState((prev) => ({
            ...prev,
            status: "connected",
            qr: null,
            phone: evt.data?.phone ?? prev.phone,
          }));
        } else if (evt.type === "disconnected") {
          setState((prev) => ({ ...prev, status: "disconnected" }));
        }
      } catch {
        /* ignore malformed frame */
      }
    };

    return () => source.close();
  }, [deviceId]);

  return state;
}
