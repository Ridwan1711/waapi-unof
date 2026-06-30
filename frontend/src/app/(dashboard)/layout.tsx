import type { ReactNode } from "react";

import { AuthGuard } from "@/components/auth-guard";
import { Sidebar } from "@/components/dashboard/sidebar";
import { Topbar } from "@/components/dashboard/topbar";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <AuthGuard>
      <div className="flex min-h-screen">
        <Sidebar />
        <div className="flex flex-1 flex-col">
          <Topbar />
          <main className="flex-1 space-y-6 p-4 md:p-8">{children}</main>
        </div>
      </div>
    </AuthGuard>
  );
}
