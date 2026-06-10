"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { Activity } from "lucide-react";
import { getSession } from "@/lib/auth";

export default function Home() {
  const router = useRouter();
  useEffect(() => {
    router.replace(getSession() ? "/dashboard" : "/login");
  }, [router]);

  return (
    <div className="grid min-h-screen place-items-center text-slate-500">
      <Activity className="h-6 w-6 animate-pulse text-accent" />
    </div>
  );
}
