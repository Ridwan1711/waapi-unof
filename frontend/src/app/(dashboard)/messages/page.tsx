import type { Metadata } from "next";

import { MessageSquare } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";

export const metadata: Metadata = { title: "Messages" };

export default function MessagesPage() {
  return (
    <>
      <PageHeader title="Messages" description="Browse inbound and outbound message logs." />
      <EmptyState
        icon={MessageSquare}
        title="No messages yet"
        description="Once you connect a device and start sending or receiving, your messages appear here."
      />
    </>
  );
}
