"use client";

import * as React from "react";

import { Plus } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

import { useCreateDevice } from "./hooks";
import { useDeviceEvents } from "./use-device-events";

export function AddDeviceDialog() {
  const [open, setOpen] = React.useState(false);
  const [name, setName] = React.useState("");
  const [deviceId, setDeviceId] = React.useState<string | null>(null);
  const createDevice = useCreateDevice();
  const events = useDeviceEvents(open ? deviceId : null);

  function handleOpenChange(next: boolean) {
    setOpen(next);
    if (!next) {
      setDeviceId(null);
      setName("");
    }
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const device = await createDevice.mutateAsync({ name });
    setDeviceId(device.id);
  }

  React.useEffect(() => {
    if (events.status === "connected") {
      const timer = setTimeout(() => {
        setOpen(false);
        setDeviceId(null);
        setName("");
      }, 1500);
      return () => clearTimeout(timer);
    }
  }, [events.status]);

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button>
          <Plus /> Add device
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Add a device</DialogTitle>
          <DialogDescription>Connect a WhatsApp account by scanning a QR code.</DialogDescription>
        </DialogHeader>

        {deviceId === null ? (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="device-name">Device name</Label>
              <Input
                id="device-name"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Support line"
              />
            </div>
            <Button type="submit" className="w-full" disabled={createDevice.isPending}>
              {createDevice.isPending ? "Creating…" : "Generate QR"}
            </Button>
          </form>
        ) : (
          <div className="flex flex-col items-center gap-3 py-2 text-center">
            {events.status === "connected" ? (
              <p className="text-sm font-medium text-emerald-600">
                Connected{events.phone ? ` · ${events.phone}` : ""}
              </p>
            ) : events.qr ? (
              <>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={events.qr}
                  alt="WhatsApp QR code"
                  className="h-56 w-56 rounded-md border"
                />
                <p className="text-sm text-muted-foreground">
                  WhatsApp → Linked devices → Link a device, then scan.
                </p>
              </>
            ) : (
              <p className="text-sm text-muted-foreground">Starting session…</p>
            )}
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
