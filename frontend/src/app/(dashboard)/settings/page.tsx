import type { Metadata } from "next";

import { Settings } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";

export const metadata: Metadata = { title: "Settings" };

export default function SettingsPage() {
  return (
    <>
      <PageHeader title="Settings" description="Manage your account and workspace." />
      <EmptyState
        icon={Settings}
        title="Settings coming together"
        description="Profile, workspace, and team management will be available here."
      />
    </>
  );
}
