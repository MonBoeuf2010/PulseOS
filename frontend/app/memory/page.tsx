"use client";

import React, { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Brain, Plus, Trash2 } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { api, ApiError } from "@/lib/api";
import type { MemoryItem } from "@/lib/types";

const KINDS = ["interest", "goal", "profession", "preference", "episodic"];

export default function MemoryPage() {
  const router = useRouter();
  const [items, setItems] = useState<MemoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [kind, setKind] = useState(KINDS[1]);
  const [content, setContent] = useState("");
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    try {
      setItems(await api.listMemory());
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) router.replace("/login");
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    load();
  }, [load]);

  async function add(e: React.FormEvent) {
    e.preventDefault();
    if (!content.trim()) return;
    setBusy(true);
    try {
      const created = await api.addMemory(kind, content.trim());
      setItems((prev) => [created, ...prev]);
      setContent("");
    } finally {
      setBusy(false);
    }
  }

  async function remove(id: string) {
    setItems((prev) => prev.filter((m) => m.id !== id));
    try {
      await api.deleteMemory(id);
    } catch {
      load();
    }
  }

  return (
    <AppShell>
      <header className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight text-slate-100">AI Memory</h1>
        <p className="mt-1 text-sm text-slate-500">
          Everything PulseOS remembers about you — fully transparent and editable.
        </p>
      </header>

      <form onSubmit={add} className="card mb-6 flex flex-col gap-3 p-4 sm:flex-row sm:items-end">
        <div className="sm:w-40">
          <label className="label">Kind</label>
          <select className="input" value={kind} onChange={(e) => setKind(e.target.value)}>
            {KINDS.map((k) => (
              <option key={k} value={k}>
                {k}
              </option>
            ))}
          </select>
        </div>
        <div className="flex-1">
          <label className="label">What should we remember?</label>
          <input
            className="input"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="e.g. Goal: raise a seed round by Q4"
          />
        </div>
        <button type="submit" disabled={busy} className="btn-primary">
          <Plus className="h-4 w-4" />
          Add
        </button>
      </form>

      {loading ? (
        <div className="card h-40 animate-pulse" />
      ) : items.length === 0 ? (
        <div className="card flex flex-col items-center px-6 py-16 text-center">
          <Brain className="mb-3 h-7 w-7 text-slate-600" />
          <h3 className="text-base font-semibold text-slate-200">No memories yet</h3>
          <p className="mt-1 text-sm text-slate-500">
            Add goals and interests so briefings get sharper.
          </p>
        </div>
      ) : (
        <ul className="space-y-2">
          {items.map((m) => (
            <li key={m.id} className="card flex items-center justify-between gap-4 px-4 py-3">
              <div className="min-w-0">
                <span className="chip mb-1">{m.kind}</span>
                <p className="truncate text-sm text-slate-200">{m.content}</p>
              </div>
              <button
                onClick={() => remove(m.id)}
                className="btn-ghost px-2.5 py-1.5 text-slate-500 hover:text-signal-red"
                aria-label="Delete memory"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </li>
          ))}
        </ul>
      )}
    </AppShell>
  );
}
