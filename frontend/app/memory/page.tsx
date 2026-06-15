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
      <header className="mb-lg">
        <div className="eyebrow mb-1">Transparent by design</div>
        <h1 className="text-[32px] font-semibold tracking-[-0.6px] text-ink">AI Memory</h1>
        <p className="mt-1 text-[15px] text-body-mid">
          Everything LifeIQ remembers about you — fully visible and editable.
        </p>
      </header>

      <form onSubmit={add} className="card mb-lg flex flex-col gap-md p-lg sm:flex-row sm:items-end">
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
          <Plus className="h-4 w-4" /> Add
        </button>
      </form>

      {loading ? (
        <div className="card h-40 animate-pulse" />
      ) : items.length === 0 ? (
        <div className="card flex flex-col items-center px-lg py-16 text-center">
          <Brain className="mb-md h-7 w-7 text-mute-soft" />
          <h3 className="text-[18px] font-medium text-ink">No memories yet</h3>
          <p className="mt-1 text-[14px] text-body-mid">Add goals and interests so briefings get sharper.</p>
        </div>
      ) : (
        <ul className="space-y-sm">
          {items.map((m) => (
            <li key={m.id} className="card flex items-center justify-between gap-lg px-lg py-md">
              <div className="min-w-0">
                <span className="chip mb-1">{m.kind}</span>
                <p className="truncate text-[15px] text-ink-strong">{m.content}</p>
              </div>
              <button
                onClick={() => remove(m.id)}
                className="btn-secondary btn-sm px-md text-mute hover:text-signal-red"
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
