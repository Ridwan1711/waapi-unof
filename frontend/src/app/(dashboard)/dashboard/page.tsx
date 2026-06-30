"use client";

import { Bot, MessageSquare, Smartphone, Webhook } from "lucide-react";

import { PageHeader } from "@/components/page-header";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { useMe } from "@/features/account/hooks";
import { useAutoReplyRules } from "@/features/automation/hooks";
import { useDevices } from "@/features/devices/hooks";
import { useMessages } from "@/features/messages/hooks";
import { useWebhooks } from "@/features/webhooks/hooks";

const STEPS = [
  "Generate an API key from the API Keys page.",
  "Add a device and scan the QR code to connect WhatsApp.",
  "Send your first message via the REST API.",
];

export default function OverviewPage() {
  const me = useMe();
  const devices = useDevices();
  const webhooks = useWebhooks();
  const messages = useMessages();
  const rules = useAutoReplyRules();

  const deviceList = devices.data ?? [];
  const connected = deviceList.filter((d) => d.status === "connected").length;

  const stats = [
    { label: "Connected devices", value: `${connected}/${deviceList.length}`, icon: Smartphone },
    { label: "Messages", value: String(messages.data?.pagination.count ?? 0), icon: MessageSquare },
    {
      label: "Active webhooks",
      value: String((webhooks.data ?? []).filter((w) => w.is_active).length),
      icon: Webhook,
    },
    { label: "Auto-reply rules", value: String((rules.data ?? []).length), icon: Bot },
  ];

  const greeting = me.data ? `Welcome, ${me.data.user.full_name || me.data.user.email}` : "Overview";

  return (
    <>
      <PageHeader title={greeting} description="A snapshot of your workspace." />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.label}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.label}
                </CardTitle>
                <Icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Getting started</CardTitle>
          <CardDescription>Three steps to your first message.</CardDescription>
        </CardHeader>
        <CardContent>
          <ol className="space-y-3">
            {STEPS.map((step, index) => (
              <li key={step} className="flex items-start gap-3 text-sm">
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">
                  {index + 1}
                </span>
                <span className="pt-0.5 text-muted-foreground">{step}</span>
              </li>
            ))}
          </ol>
        </CardContent>
      </Card>
    </>
  );
}
