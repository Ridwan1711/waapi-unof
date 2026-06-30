"use client";

import * as React from "react";

import { KeyRound, Plus } from "lucide-react";

import { EmptyState } from "@/components/empty-state";
import { PageHeader } from "@/components/page-header";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useApiKeys, useCreateApiKey, useRevokeApiKey } from "@/features/api-keys/hooks";

export default function ApiKeysPage() {
  const { data: keys = [], isLoading } = useApiKeys();
  const createKey = useCreateApiKey();
  const revokeKey = useRevokeApiKey();

  const [open, setOpen] = React.useState(false);
  const [name, setName] = React.useState("");
  const [createdKey, setCreatedKey] = React.useState<string | null>(null);

  function handleOpenChange(next: boolean) {
    setOpen(next);
    if (!next) {
      setName("");
      setCreatedKey(null);
    }
  }

  async function handleCreate(event: React.FormEvent) {
    event.preventDefault();
    const created = await createKey.mutateAsync({ name });
    setCreatedKey(created.key);
  }

  const dialog = (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button>
          <Plus /> New key
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create API key</DialogTitle>
          <DialogDescription>Use this key to authenticate REST API requests.</DialogDescription>
        </DialogHeader>
        {createdKey ? (
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground">
              Copy your key now — it won&apos;t be shown again.
            </p>
            <code className="block break-all rounded-md border bg-muted p-3 text-xs">
              {createdKey}
            </code>
            <Button className="w-full" onClick={() => handleOpenChange(false)}>
              Done
            </Button>
          </div>
        ) : (
          <form onSubmit={handleCreate} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="key-name">Name</Label>
              <Input
                id="key-name"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Production"
              />
            </div>
            <Button type="submit" className="w-full" disabled={createKey.isPending}>
              {createKey.isPending ? "Creating…" : "Create key"}
            </Button>
          </form>
        )}
      </DialogContent>
    </Dialog>
  );

  return (
    <>
      <PageHeader
        title="API Keys"
        description="Create and manage keys for programmatic access."
        action={dialog}
      />

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : keys.length === 0 ? (
        <EmptyState
          icon={KeyRound}
          title="No API keys"
          description="Generate a scoped key to authenticate your API requests."
        />
      ) : (
        <div className="grid gap-3">
          {keys.map((key) => (
            <Card key={key.id}>
              <CardContent className="flex items-center justify-between gap-4 p-4">
                <div>
                  <p className="font-medium">{key.name}</p>
                  <p className="font-mono text-sm text-muted-foreground">{key.prefix}…</p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={key.is_active ? "success" : "secondary"}>
                    {key.is_active ? "active" : "revoked"}
                  </Badge>
                  {key.is_active && (
                    <Button
                      variant="ghost"
                      size="sm"
                      disabled={revokeKey.isPending}
                      onClick={() => revokeKey.mutate(key.id)}
                    >
                      Revoke
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </>
  );
}
