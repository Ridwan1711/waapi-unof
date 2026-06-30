import type { Metadata } from "next";

import { KeyRound } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";

export const metadata: Metadata = { title: "API Keys" };

export default function ApiKeysPage() {
  return (
    <>
      <PageHeader title="API Keys" description="Create and manage keys for programmatic access." />
      <EmptyState
        icon={KeyRound}
        title="No API keys"
        description="Generate a scoped API key to authenticate your requests to the REST API."
      />
    </>
  );
}
