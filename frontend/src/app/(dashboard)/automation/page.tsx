"use client";

import * as React from "react";

import { Bot, Plus, Trash2 } from "lucide-react";

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
import { Textarea } from "@/components/ui/textarea";
import {
  useAutoReplyRules,
  useCreateRule,
  useDeleteRule,
  useUpdateRule,
} from "@/features/automation/hooks";

const SELECT_CLASS =
  "h-9 w-full rounded-md border border-input bg-transparent px-3 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring";

export default function AutomationPage() {
  const { data: rules = [], isLoading } = useAutoReplyRules();
  const createRule = useCreateRule();
  const updateRule = useUpdateRule();
  const deleteRule = useDeleteRule();

  const [open, setOpen] = React.useState(false);
  const [name, setName] = React.useState("");
  const [matchType, setMatchType] = React.useState("contains");
  const [pattern, setPattern] = React.useState("");
  const [response, setResponse] = React.useState("");

  function reset() {
    setName("");
    setMatchType("contains");
    setPattern("");
    setResponse("");
  }

  function handleOpenChange(next: boolean) {
    setOpen(next);
    if (!next) reset();
  }

  async function handleCreate(event: React.FormEvent) {
    event.preventDefault();
    await createRule.mutateAsync({
      name,
      match_type: matchType,
      pattern,
      response_body: response,
    });
    handleOpenChange(false);
  }

  const dialog = (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button>
          <Plus /> New rule
        </Button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create auto-reply rule</DialogTitle>
          <DialogDescription>Automatically reply to matching inbound messages.</DialogDescription>
        </DialogHeader>
        <form onSubmit={handleCreate} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="rule-name">Name</Label>
            <Input
              id="rule-name"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="rule-match">Match type</Label>
            <select
              id="rule-match"
              className={SELECT_CLASS}
              value={matchType}
              onChange={(e) => setMatchType(e.target.value)}
            >
              <option value="exact">Exact</option>
              <option value="contains">Contains</option>
              <option value="starts_with">Starts with</option>
              <option value="regex">Regex</option>
            </select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="rule-pattern">Pattern</Label>
            <Input
              id="rule-pattern"
              required
              value={pattern}
              onChange={(e) => setPattern(e.target.value)}
              placeholder="hello"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="rule-response">Reply</Label>
            <Textarea
              id="rule-response"
              required
              value={response}
              onChange={(e) => setResponse(e.target.value)}
              placeholder="Thanks for your message! We'll reply soon."
            />
          </div>
          <Button type="submit" className="w-full" disabled={createRule.isPending}>
            {createRule.isPending ? "Creating…" : "Create rule"}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );

  return (
    <>
      <PageHeader
        title="Automation"
        description="Define auto-reply rules for inbound messages."
        action={dialog}
      />

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : rules.length === 0 ? (
        <EmptyState
          icon={Bot}
          title="No auto-reply rules"
          description="Create rules that automatically respond to incoming messages."
        />
      ) : (
        <div className="grid gap-3">
          {rules.map((rule) => (
            <Card key={rule.id}>
              <CardContent className="flex items-center justify-between gap-4 p-4">
                <div className="min-w-0">
                  <p className="font-medium">{rule.name}</p>
                  <p className="truncate text-sm text-muted-foreground">
                    {rule.match_type}: {rule.pattern}
                  </p>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant={rule.is_active ? "success" : "secondary"}>
                    {rule.is_active ? "active" : "off"}
                  </Badge>
                  <Button
                    variant="ghost"
                    size="sm"
                    disabled={updateRule.isPending}
                    onClick={() => updateRule.mutate({ id: rule.id, is_active: !rule.is_active })}
                  >
                    {rule.is_active ? "Disable" : "Enable"}
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    aria-label="Delete rule"
                    disabled={deleteRule.isPending}
                    onClick={() => deleteRule.mutate(rule.id)}
                  >
                    <Trash2 />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </>
  );
}
