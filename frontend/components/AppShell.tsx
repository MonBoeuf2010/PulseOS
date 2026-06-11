"use client";

import React, { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";
import {
  Activity,
  Brain,
  LayoutDashboard,
  LogOut,
  MessagesSquare,
  Radar,
  Search,
  Sparkles,
  Users,
} from "lucide-react";
import { clearSession, getSession } from "@/lib/auth";

const NAV = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/chat", label: "AI Analyst", icon: MessagesSquare },
  { href: "/feed", label: "Community", icon: Users },
  { href: "/opportunities", label: "Opportunities", icon: Radar },
  { href: "/memory", label: "Memory", icon: Brain },
  { href: "/search", label: "Search", icon: Search },
  { href: "/pricing", label: "Upgrade", icon: Sparkles },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!getSession()) router.replace("/login");
    else setReady(true);
  }, [router]);

  function logout() {
    clearSession();
    router.replace("/login");
  }

  if (!ready) {
    return (
      <div className="grid min-h-screen place-items-center text-mute">
        <Activity className="h-5 w-5 animate-pulse" />
      </div>
    );
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-[1180px] gap-3xl px-lg py-2xl md:px-2xl">
      <aside className="sticky top-2xl hidden h-[calc(100vh-3rem)] w-56 shrink-0 flex-col md:flex">
        <Link href="/dashboard" className="mb-3xl flex items-center gap-sm px-sm">
          <div className="grid h-8 w-8 place-items-center rounded-md bg-primary">
            <Activity className="h-4 w-4 text-on-primary" />
          </div>
          <span className="text-[20px] font-semibold tracking-[-0.4px] text-ink">PulseOS</span>
        </Link>
        <nav className="flex flex-1 flex-col gap-xxs">
          {NAV.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-md rounded-sm px-md py-sm text-[14px] font-medium transition-colors ${
                  active
                    ? "bg-canvas-soft text-ink shadow-[inset_2px_0_0_0_#080808]"
                    : "text-body-mid hover:bg-canvas-soft hover:text-ink"
                }`}
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            );
          })}
        </nav>
        <button
          onClick={logout}
          className="flex items-center gap-md rounded-sm px-md py-sm text-[14px] font-medium text-mute hover:text-ink"
        >
          <LogOut className="h-4 w-4" />
          Sign out
        </button>
      </aside>

      <main className="min-w-0 flex-1 pb-16">{children}</main>
    </div>
  );
}
