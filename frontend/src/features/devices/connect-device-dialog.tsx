"use client";

import * as React from "react";

import { QrCode } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

import { DeviceQrView } from "./device-qr-view";
import { useConnectDevice, useDeviceQr } from "./hooks";

/** "Show QR / Connect" for an existing device — (re)starts the session and polls its QR. */
export function ConnectDeviceDialog({ deviceId }: { deviceId: string }) {
  const [open, setOpen] = React.useState(false);
  const connectDevice = useConnectDevice();
  const qr = useDeviceQr(open ? deviceId : null);

  function handleOpenChange(next: boolean) {
    setOpen(next);
    if (next) {
      // Ensure the Node session is running (idempotent on the Node side).
      connectDevice.mutate(deviceId);
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button variant="ghost" size="icon" aria-label="Show QR / connect">
          <QrCode />
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Connect device</DialogTitle>
          <DialogDescription>Scan the QR with WhatsApp to link this device.</DialogDescription>
        </DialogHeader>
        <DeviceQrView
          status={qr.data?.status ?? null}
          qr={qr.data?.qr ?? null}
          phone={qr.data?.phone ?? null}
        />
      </DialogContent>
    </Dialog>
  );
}
