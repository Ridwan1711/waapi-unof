"use client";

import { useRouter } from "next/navigation";

import { LogOut } from "lucide-react";

import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import { logout } from "@/lib/auth";

export function Topbar() {
  const router = useRouter();

  function handleLogout() {
    logout();
    router.push("/login");
  }

  return (
    <header className="flex h-14 items-center justify-between gap-4 border-b px-4 md:px-6">
      <div className="text-sm font-medium text-muted-foreground">Dashboard</div>
      <div className="flex items-center gap-1">
        <ThemeToggle />
        <Button variant="ghost" size="icon" aria-label="Log out" onClick={handleLogout}>
          <LogOut />
        </Button>
      </div>
    </header>
  );
}
