import type { Metadata } from "next";

import { Smartphone } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";

export const metadata: Metadata = { title: "Devices" };

export default function DevicesPage() {
  return (
    <>
      <PageHeader title="Devices" description="Connect and manage your WhatsApp sessions." />
      <EmptyState
        icon={Smartphone}
        title="No devices yet"
        description="Connect a WhatsApp account by scanning a QR code to start sending messages."
      />
    </>
  );
}
