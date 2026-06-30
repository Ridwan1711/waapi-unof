import type { Metadata } from "next";

import { Bot } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";

export const metadata: Metadata = { title: "Automation" };

export default function AutomationPage() {
  return (
    <>
      <PageHeader title="Automation" description="Define auto-reply rules for inbound messages." />
      <EmptyState
        icon={Bot}
        title="No auto-reply rules"
        description="Create rules that automatically respond to incoming messages based on their content."
      />
    </>
  );
}
