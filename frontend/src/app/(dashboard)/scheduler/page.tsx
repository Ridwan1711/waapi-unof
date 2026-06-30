import type { Metadata } from "next";

import { CalendarClock } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";

export const metadata: Metadata = { title: "Scheduler" };

export default function SchedulerPage() {
  return (
    <>
      <PageHeader title="Scheduler" description="Schedule messages to send later." />
      <EmptyState
        icon={CalendarClock}
        title="Nothing scheduled"
        description="Queue one-off or recurring messages and they will be sent automatically."
      />
    </>
  );
}
