import type { Metadata } from "next";

import { BarChart3 } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";

export const metadata: Metadata = { title: "Analytics" };

export default function AnalyticsPage() {
  return (
    <>
      <PageHeader title="Analytics" description="Track message volume, delivery, and errors." />
      <EmptyState
        icon={BarChart3}
        title="No data yet"
        description="Analytics populate as you send and receive messages across your devices."
      />
    </>
  );
}
