"use client";

import * as React from "react";

import { MessageSquare } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { useDevices } from "@/features/devices/hooks";
import { useMessages } from "@/features/messages/hooks";

const SELECT_CLASS =
  "h-9 rounded-md border border-input bg-transparent px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";

export default function MessagesPage() {
  const [direction, setDirection] = React.useState("");
  const [status, setStatus] = React.useState("");
  const [device, setDevice] = React.useState("");

  const { data, isLoading } = useMessages({ direction, status, device });
  const devices = useDevices();
  const results = data?.results ?? [];

  return (
    <>
      <PageHeader
        title="Messages"
        description={`Logs${data ? ` · ${data.pagination.count} total` : ""}`}
      />

      <div className="flex flex-wrap gap-2">
        <select
          aria-label="Filter by device"
          className={SELECT_CLASS}
          value={device}
          onChange={(e) => setDevice(e.target.value)}
        >
          <option value="">All devices</option>
          {(devices.data ?? []).map((d) => (
            <option key={d.id} value={d.id}>
              {d.name}
            </option>
          ))}
        </select>
        <select
          aria-label="Filter by direction"
          className={SELECT_CLASS}
          value={direction}
          onChange={(e) => setDirection(e.target.value)}
        >
          <option value="">All directions</option>
          <option value="in">Inbound</option>
          <option value="out">Outbound</option>
        </select>
        <select
          aria-label="Filter by status"
          className={SELECT_CLASS}
          value={status}
          onChange={(e) => setStatus(e.target.value)}
        >
          <option value="">All statuses</option>
          <option value="sent">Sent</option>
          <option value="delivered">Delivered</option>
          <option value="read">Read</option>
          <option value="failed">Failed</option>
          <option value="received">Received</option>
          <option value="queued">Queued</option>
        </select>
      </div>

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : results.length === 0 ? (
        <EmptyState
          icon={MessageSquare}
          title="No messages"
          description="Messages you send or receive will appear here."
        />
      ) : (
        <Card>
          <div className="divide-y">
            {results.map((message) => (
              <div key={message.id} className="flex items-center justify-between gap-4 p-4">
                <div className="min-w-0">
                  <p className="truncate text-sm">
                    <span className="text-muted-foreground">{message.address || "—"}</span>{" "}
                    {message.body}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {new Date(message.created_at).toLocaleString()} · {message.message_type}
                  </p>
                </div>
                <div className="flex shrink-0 items-center gap-2">
                  <Badge variant={message.direction === "in" ? "secondary" : "default"}>
                    {message.direction === "in" ? "in" : "out"}
                  </Badge>
                  <Badge variant={message.status === "failed" ? "destructive" : "outline"}>
                    {message.status}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </>
  );
}
