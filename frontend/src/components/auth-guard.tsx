"use client";

import { useRouter } from "next/navigation";
import * as React from "react";

import { getToken } from "@/lib/token";

/**
 * Redirects to /login when no access token is present. Rendered client-side
 * (the token lives in localStorage), so it runs after hydration.
 */
export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();

  React.useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
    }
  }, [router]);

  return <>{children}</>;
}
