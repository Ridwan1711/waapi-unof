"use client";

import { PageHeader } from "@/components/page-header";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useMe } from "@/features/account/hooks";

export default function SettingsPage() {
  const { data } = useMe();

  return (
    <>
      <PageHeader title="Settings" description="Your account and workspaces." />

      <Card>
        <CardHeader>
          <CardTitle>Account</CardTitle>
        </CardHeader>
        <CardContent className="space-y-1 text-sm">
          <p>
            <span className="text-muted-foreground">Email: </span>
            {data?.user.email ?? "—"}
          </p>
          <p>
            <span className="text-muted-foreground">Name: </span>
            {data?.user.full_name || "—"}
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Workspaces</CardTitle>
        </CardHeader>
        <CardContent className="space-y-1 text-sm">
          {(data?.workspaces ?? []).map((workspace) => (
            <p key={workspace.id}>
              {workspace.name}{" "}
              <span className="text-muted-foreground">({workspace.slug})</span>
            </p>
          ))}
        </CardContent>
      </Card>
    </>
  );
}
