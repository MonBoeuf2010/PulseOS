"use client";

import React, { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import { Activity, Brain, LayoutDashboard, LogOut, Radar, Search } from "lucide-react";
import { clearSession, getSession } from "@/lib/auth";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/opportunities", label: "Opportunities", icon: Radar },
  { href: "/memory", label: "Memory", icon: Brain },
  { href: "/search", label: "Search", icon: Search },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!getSession()) {
      router.replace("/login");
    } else {
      setReady(true);
    }
  }, [router]);

  function logout() {
    clearSession();
    router.replace("/login");
  }

  if (!ready) {
    return (
      <div className="grid min-h-screen place-items-center text-slate-500">
        <Activity className="h-5 w-5 animate-pulse" />
      </div>
    );
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-6xl gap-6 px-4 py-6 md:px-6">
      <aside className="sticky top-6 hidden h-[calc(100vh-3rem)] w-56 shrink-0 flex-col md:flex">
        <Link href="/dashboard" className="mb-8 flex items-center gap-2 px-2">
          <div className="grid h-8 w-8 place-items-center rounded-xl bg-accent shadow-glow">
            <Activity className="h-4 w-4 text-white" />
          </div>
          <span className="text-lg font-semibold tracking-tight text-slate-100">PulseOS</span>
        </Link>
        <nav className="flex flex-1 flex-col gap-1">
          {NAV.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium transition-colors ${
                  active
                    ? "bg-ink-800 text-slate-100 shadow-card"
                    : "text-slate-400 hover:bg-ink-800/50 hover:text-slate-200"
                }`}
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            );
          })}
        </nav>
        <button onClick={logout} className="flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium text-slate-500 hover:text-slate-300">
          <LogOut className="h-4 w-4" />
          Sign out
        </button>
      </aside>

      <main className="min-w-0 flex-1 pb-16">{children}</main>
    </div>
  );
}
