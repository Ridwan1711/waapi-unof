"use client";

import * as React from "react";

import { Plus, Trash2, Webhook as WebhookIcon } from "lucide-react";

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
import { useCreateWebhook, useDeleteWebhook, useWebhooks } from "@/features/webhooks/hooks";

export default function WebhooksPage() {
  const { data: webhooks = [], isLoading } = useWebhooks();
  const createWebhook = useCreateWebhook();
  const deleteWebhook = useDeleteWebhook();

  const [open, setOpen] = React.useState(false);
  const [url, setUrl] = React.useState("");
  const [events, setEvents] = React.useState("message.received");
  const [secret, setSecret] = React.useState<string | null>(null);

  function handleOpenChange(next: boolean) {
    setOpen(next);
    if (!next) {
      setUrl("");
      setEvents("message.received");
      setSecret(null);
    }
  }

  async function handleCreate(event: React.FormEvent) {
    event.preventDefault();
    const created = await createWebhook.mutateAsync({
      url,
      events: events
        .split(",")
        .map((value) => value.trim())
        .filter(Boolean),
    });
    setSecret(created.secret);
  }

  const dialog = (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button>
          <Plus /> New webhook
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create webhook</DialogTitle>
          <DialogDescription>Receive HMAC-signed events at your endpoint.</DialogDescription>
        </DialogHeader>
        {secret ? (
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground">
              Your signing secret (used to verify the X-Signature header):
            </p>
            <code className="block break-all rounded-md border bg-muted p-3 text-xs">{secret}</code>
            <Button className="w-full" onClick={() => handleOpenChange(false)}>
              Done
            </Button>
          </div>
        ) : (
          <form onSubmit={handleCreate} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="hook-url">Endpoint URL</Label>
              <Input
                id="hook-url"
                type="url"
                required
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="https://example.com/webhooks/wa"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="hook-events">Events (comma-separated)</Label>
              <Input
                id="hook-events"
                value={events}
                onChange={(e) => setEvents(e.target.value)}
                placeholder="message.received"
              />
            </div>
            <Button type="submit" className="w-full" disabled={createWebhook.isPending}>
              {createWebhook.isPending ? "Creating…" : "Create webhook"}
            </Button>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );

  return (
    <>
      <PageHeader
        title="Webhooks"
        description="Receive real-time events at your own endpoints."
        action={dialog}
      />

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : webhooks.length === 0 ? (
        <EmptyState
          icon={WebhookIcon}
          title="No webhooks configured"
          description="Register an endpoint to receive HMAC-signed events such as incoming messages."
        />
      ) : (
        <div className="grid gap-3">
          {webhooks.map((webhook) => (
            <Card key={webhook.id}>
              <CardContent className="flex items-center justify-between gap-4 p-4">
                <div className="min-w-0">
                  <p className="truncate font-medium">{webhook.url}</p>
                  <p className="text-sm text-muted-foreground">
                    {webhook.events.length ? webhook.events.join(", ") : "all events"}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={webhook.is_active ? "success" : "secondary"}>
                    {webhook.is_active ? "active" : "inactive"}
                  </Badge>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label="Delete webhook"
                    disabled={deleteWebhook.isPending}
                    onClick={() => deleteWebhook.mutate(webhook.id)}
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
