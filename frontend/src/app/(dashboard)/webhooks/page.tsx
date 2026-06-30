import type { Metadata } from "next";

import { Webhook } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";

export const metadata: Metadata = { title: "Webhooks" };

export default function WebhooksPage() {
  return (
    <>
      <PageHeader title="Webhooks" description="Receive real-time events at your own endpoints." />
      <EmptyState
        icon={Webhook}
        title="No webhooks configured"
        description="Register an endpoint to receive HMAC-signed events such as incoming messages."
      />
    </>
  );
}
