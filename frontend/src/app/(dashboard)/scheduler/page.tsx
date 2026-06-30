"use client";

import * as React from "react";

import { CalendarClock, Plus } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
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
import { useDevices } from "@/features/devices/hooks";
import {
  useCancelScheduled,
  useCreateScheduled,
  useScheduledMessages,
} from "@/features/scheduler/hooks";

const SELECT_CLASS =
  "h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";

export default function SchedulerPage() {
  const { data: items = [], isLoading } = useScheduledMessages();
  const createScheduled = useCreateScheduled();
  const cancelScheduled = useCancelScheduled();
  const devices = useDevices();

  const [open, setOpen] = React.useState(false);
  const [deviceId, setDeviceId] = React.useState("");
  const [runAt, setRunAt] = React.useState("");
  const [to, setTo] = React.useState("");
  const [text, setText] = React.useState("");

  function reset() {
    setDeviceId("");
    setRunAt("");
    setTo("");
    setText("");
  }

  function handleOpenChange(next: boolean) {
    setOpen(next);
    if (!next) reset();
  }

  async function handleCreate(event: React.FormEvent) {
    event.preventDefault();
    await createScheduled.mutateAsync({
      device: deviceId,
      run_at: new Date(runAt).toISOString(),
      to,
      text,
    });
    handleOpenChange(false);
  }

  const dialog = (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button>
          <Plus /> Schedule message
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Schedule a message</DialogTitle>
          <DialogDescription>It will be sent automatically at the chosen time.</DialogDescription>
        </DialogHeader>
        <form onSubmit={handleCreate} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="sch-device">Device</Label>
            <select
              id="sch-device"
              required
              className={SELECT_CLASS}
              value={deviceId}
              onChange={(e) => setDeviceId(e.target.value)}
            >
              <option value="" disabled>
                Select a device
              </option>
              {(devices.data ?? []).map((d) => (
                <option key={d.id} value={d.id}>
                  {d.name}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="sch-when">Send at</Label>
            <Input
              id="sch-when"
              type="datetime-local"
              required
              value={runAt}
              onChange={(e) => setRunAt(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="sch-to">Recipient</Label>
            <Input
              id="sch-to"
              required
              value={to}
              onChange={(e) => setTo(e.target.value)}
              placeholder="15551234567"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="sch-text">Message</Label>
            <Input
              id="sch-text"
              required
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
          </div>
          <Button type="submit" className="w-full" disabled={createScheduled.isPending}>
            {createScheduled.isPending ? "Scheduling…" : "Schedule"}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );

  return (
    <>
      <PageHeader title="Scheduler" description="Schedule messages to send later." action={dialog} />

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : items.length === 0 ? (
        <EmptyState
          icon={CalendarClock}
          title="Nothing scheduled"
          description="Queue a message and it will be sent automatically."
        />
      ) : (
        <div className="grid gap-3">
          {items.map((item) => {
            const recipient = String(item.payload.to ?? "");
            const cancellable = item.status === "pending" || item.status === "queued";
            return (
              <Card key={item.id}>
                <CardContent className="flex items-center justify-between gap-4 p-4">
                  <div>
                    <p className="font-medium">{recipient || "—"}</p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(item.run_at).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant={item.status === "failed" ? "destructive" : "secondary"}>
                      {item.status}
                    </Badge>
                    {cancellable && (
                      <Button
                        variant="ghost"
                        size="sm"
                        disabled={cancelScheduled.isPending}
                        onClick={() => cancelScheduled.mutate(item.id)}
                      >
                        Cancel
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </>
  );
}
