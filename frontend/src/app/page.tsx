import Link from "next/link";

import { ArrowRight, ExternalLink } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { env } from "@/lib/env";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="flex h-14 items-center justify-between border-b px-4 md:px-8">
        <div className="flex items-center gap-2">
          <span className="flex h-6 w-6 items-center justify-center rounded bg-primary text-xs font-bold text-primary-foreground">
            W
          </span>
          <span className="font-semibold">{env.appName}</span>
        </div>
        <nav className="flex items-center gap-2">
          <Button variant="ghost" asChild>
            <Link href="/login">Sign in</Link>
          </Button>
          <Button asChild>
            <Link href="/register">Get started</Link>
          </Button>
        </nav>
      </header>

      <main className="flex flex-1 flex-col items-center justify-center px-4 py-20 text-center">
        <Badge variant="secondary" className="mb-6">
          Unofficial · self-hostable
        </Badge>
        <h1 className="max-w-3xl text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
          The WhatsApp API platform for builders
        </h1>
        <p className="mt-6 max-w-xl text-balance text-lg text-muted-foreground">
          Connect a WhatsApp account, then automate messaging through a clean REST API, webhooks,
          and a modern dashboard.
        </p>
        <div className="mt-8 flex flex-col gap-3 sm:flex-row">
          <Button size="lg" asChild>
            <Link href="/register">
              Start building <ArrowRight />
            </Link>
          </Button>
          <Button size="lg" variant="outline" asChild>
            <a href="https://github.com/your-org/waapi-unof" target="_blank" rel="noreferrer">
              <ExternalLink /> View on GitHub
            </a>
          </Button>
        </div>
      </main>

      <footer className="border-t px-4 py-6 text-center text-sm text-muted-foreground">
        Use responsibly. Automating WhatsApp may violate its Terms of Service.
      </footer>
    </div>
  );
}
