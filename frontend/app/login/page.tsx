"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { Activity, ArrowRight } from "lucide-react";
import { api, ApiError } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("demo@pulseos.com");
  const [password, setPassword] = useState("pulsedemo123");
  const [displayName, setDisplayName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      if (mode === "login") {
        await api.login(email, password);
      } else {
        await api.register(email, password, displayName || undefined);
      }
      router.replace("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="grid min-h-screen place-items-center px-4">
      <div className="w-full max-w-sm">
        <div className="mb-8 flex flex-col items-center text-center">
          <div className="mb-4 grid h-12 w-12 place-items-center rounded-2xl bg-accent shadow-glow">
            <Activity className="h-6 w-6 text-white" />
          </div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-100">PulseOS</h1>
          <p className="mt-1 text-sm text-slate-500">
            The highest-value action you should take right now.
          </p>
        </div>

        <form onSubmit={submit} className="card space-y-4 p-6">
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
            <p className="rounded-lg border border-signal-red/30 bg-signal-red/10 px-3 py-2 text-xs text-signal-red">
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
          className="mt-4 w-full text-center text-xs text-slate-500 hover:text-slate-300"
        >
          {mode === "login"
            ? "No account? Create one"
            : "Already have an account? Sign in"}
        </button>
      </div>
    </div>
  );
}
