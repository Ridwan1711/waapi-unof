"use client";

import { Power, Smartphone, Trash2 } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { AddDeviceDialog } from "@/features/devices/add-device-dialog";
import { useDeleteDevice, useDevices, useLogoutDevice } from "@/features/devices/hooks";
import type { DeviceStatus } from "@/types";

const STATUS_VARIANT: Record<DeviceStatus, "success" | "warning" | "secondary" | "destructive"> = {
  connected: "success",
  qr: "warning",
  initializing: "warning",
  pending: "secondary",
  disconnected: "secondary",
  logged_out: "secondary",
  failed: "destructive",
};

export default function DevicesPage() {
  const { data: devices = [], isLoading } = useDevices();
  const deleteDevice = useDeleteDevice();
  const logoutDevice = useLogoutDevice();

  return (
    <>
      <PageHeader
        title="Devices"
        description="Connect and manage your WhatsApp sessions."
        action={<AddDeviceDialog />}
      />

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : devices.length === 0 ? (
        <EmptyState
          icon={Smartphone}
          title="No devices yet"
          description="Add a device and scan the QR code to connect WhatsApp."
          action={<AddDeviceDialog />}
        />
      ) : (
        <div className="grid gap-3">
          {devices.map((device) => (
            <Card key={device.id}>
              <CardContent className="flex items-center justify-between gap-4 p-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-full bg-muted">
                    <Smartphone className="h-5 w-5 text-muted-foreground" />
                  </div>
                  <div>
                    <p className="font-medium">{device.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {device.phone_number || "Not linked"}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={STATUS_VARIANT[device.status] ?? "secondary"}>
                    {device.status}
                  </Badge>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label="Log out device"
                    disabled={logoutDevice.isPending}
                    onClick={() => logoutDevice.mutate(device.id)}
                  >
                    <Power />
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label="Delete device"
                    disabled={deleteDevice.isPending}
                    onClick={() => deleteDevice.mutate(device.id)}
                  >
                    <Trash2 />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </>
  );
}
