"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Activity, ArrowRight } from "lucide-react";
import { api, ApiError } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("demo@lifeiq.com");
  const [password, setPassword] = useState("pulsedemo123");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      if (mode === "login") await api.login(email, password);
      else await api.register(email, password, displayName || undefined);
      router.replace("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid min-h-screen place-items-center px-lg">
      <div className="w-full max-w-sm">
        <Link href="/" className="mb-2xl flex flex-col items-center text-center">
          <div className="mb-md grid h-12 w-12 place-items-center rounded-md bg-primary">
            <Activity className="h-6 w-6 text-on-primary" />
          </div>
          <h1 className="text-[24px] font-semibold tracking-[-0.5px] text-ink">LifeIQ</h1>
          <p className="mt-1 text-[14px] text-body-mid">
            {mode === "login" ? "Welcome back." : "Create your intelligence workspace."}
          </p>
        </Link>

        <form onSubmit={submit} className="card space-y-lg p-2xl shadow-lift">
          {mode === "register" && (
            <div>
              <label className="label">Name</label>
              <input
                className="input"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="Ada Lovelace"
              />
            </div>
          )}
          <div>
            <label className="label">Email</label>
            <input
              className="input"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
            />
          </div>
          <div>
            <label className="label">Password</label>
            <input
              className="input"
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </div>

          {error && (
            <p className="rounded-sm border border-accent-red/30 bg-accent-red/5 px-md py-sm text-[13px] text-signal-red">
              {error}
            </p>
          )}

          <button type="submit" disabled={busy} className="btn-primary w-full">
            {busy ? "…" : mode === "login" ? "Sign in" : "Create account"}
            {!busy && <ArrowRight className="h-4 w-4" />}
          </button>
        </form>

        <button
          onClick={() => {
            setMode(mode === "login" ? "register" : "login");
            setError(null);
          }}
          className="mt-lg w-full text-center text-[13px] text-mute hover:text-ink"
        >
          {mode === "login" ? "No account? Create one" : "Already have an account? Sign in"}
        </button>
      </div>
    </div>
  );
}
