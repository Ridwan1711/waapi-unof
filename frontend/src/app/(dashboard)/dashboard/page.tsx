import type { Metadata } from "next";

import { BarChart3, MessageSquare, Smartphone, Webhook } from "lucide-react";

import { PageHeader } from "@/components/page-header";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export const metadata: Metadata = { title: "Overview" };

const STATS = [
  { label: "Connected devices", value: "0", icon: Smartphone },
  { label: "Messages (30d)", value: "0", icon: MessageSquare },
  { label: "Active webhooks", value: "0", icon: Webhook },
  { label: "Delivery rate", value: "—", icon: BarChart3 },
] as const;

const STEPS = [
  "Generate an API key from the API Keys page.",
  "Add a device and scan the QR code to connect WhatsApp.",
  "Send your first message via the REST API.",
];

export default function OverviewPage() {
  return (
    <>
      <PageHeader title="Overview" description="A snapshot of your workspace." />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {STATS.map((stat) => {
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
