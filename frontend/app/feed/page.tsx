"use client";

import React, { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Send, Sparkles, TrendingUp, Users } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { categoryAccent } from "@/lib/category";
import { api, ApiError } from "@/lib/api";
import type { Post } from "@/lib/types";

const CATEGORIES = ["general", "markets", "career", "economy", "growth", "ai"];

function timeAgo(iso?: string): string {
  if (!iso) return "just now";
  const diff = Date.now() - new Date(iso).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return "just now";
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

export default function FeedPage() {
  const router = useRouter();
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [category, setCategory] = useState("markets");
  const [posting, setPosting] = useState(false);

  const load = useCallback(async () => {
    try {
      setPosts(await api.feed());
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) router.replace("/login");
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    load();
  }, [load]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim() || !body.trim()) return;
    setPosting(true);
    try {
      const created = await api.createPost(title.trim(), body.trim(), category);
      setPosts((prev) => [created, ...prev]);
      setTitle("");
      setBody("");
      setOpen(false);
    } finally {
      setPosting(false);
    }
  }

  async function react(id: string) {
    setPosts((prev) =>
      prev.map((p) =>
        p.id === id
          ? { ...p, reacted: !p.reacted, reaction_count: p.reaction_count + (p.reacted ? -1 : 1) }
          : p,
      ),
    );
    try {
      const updated = await api.reactToPost(id);
      setPosts((prev) => prev.map((p) => (p.id === id ? updated : p)));
    } catch {
      load();
    }
  }

  return (
    <AppShell>
      <header className="mb-lg flex flex-wrap items-end justify-between gap-md">
        <div>
          <div className="eyebrow mb-1">Operator community</div>
          <h1 className="text-[32px] font-semibold tracking-[-0.6px] text-ink">Community</h1>
          <p className="mt-1 text-[15px] text-body-mid">
            What sharp operators are acting on right now. Share your calls.
          </p>
        </div>
        <button onClick={() => setOpen((v) => !v)} className="btn-primary">
          <Sparkles className="h-4 w-4" /> {open ? "Close" : "Post a call"}
        </button>
      </header>

      {open && (
        <form onSubmit={submit} className="card mb-lg space-y-md p-lg shadow-lift">
          <div className="flex flex-col gap-md sm:flex-row">
            <input
              className="input flex-1"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Your call — e.g. Long applied-AI talent before the squeeze"
            />
            <select
              className="input sm:w-44"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
            >
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
          <textarea
            className="input min-h-[96px] resize-none"
            value={body}
            onChange={(e) => setBody(e.target.value)}
            placeholder="The thesis, the evidence, and what you'd do about it…"
          />
          <div className="flex justify-end">
            <button type="submit" disabled={posting} className="btn-primary">
              <Send className="h-4 w-4" /> {posting ? "Posting…" : "Publish"}
            </button>
          </div>
        </form>
      )}

      {loading ? (
        <div className="space-y-md">
          {[0, 1, 2].map((i) => (
            <div key={i} className="card h-28 animate-pulse" />
          ))}
        </div>
      ) : posts.length === 0 ? (
        <div className="card flex flex-col items-center px-lg py-16 text-center">
          <Users className="mb-md h-7 w-7 text-mute-soft" />
          <h3 className="text-[18px] font-medium text-ink">No posts yet</h3>
          <p className="mt-1 text-[14px] text-body-mid">Be the first to share a call with the community.</p>
        </div>
      ) : (
        <div className="space-y-md">
          {posts.map((p) => {
            const accent = categoryAccent(p.category);
            const initials = p.author_name.slice(0, 2).toUpperCase();
            return (
              <article key={p.id} className="card p-lg transition-shadow hover:shadow-lift">
                <div className="mb-md flex items-center gap-sm">
                  <div className={`grid h-9 w-9 place-items-center rounded-full ${accent.soft} ${accent.text} text-[13px] font-semibold`}>
                    {initials}
                  </div>
                  <div className="min-w-0">
                    <div className="text-[14px] font-medium text-ink">{p.author_name}</div>
                    <div className="text-[12px] text-mute">{timeAgo(p.created_at)}</div>
                  </div>
                  <span className={`chip ml-auto border-transparent ${accent.soft} ${accent.text}`}>
                    {p.category}
                  </span>
                </div>
                <h3 className="text-[18px] font-medium tracking-[-0.2px] text-ink">{p.title}</h3>
                <p className="mt-1.5 whitespace-pre-wrap text-[15px] leading-relaxed text-body">{p.body}</p>
                <div className="mt-md flex items-center gap-md border-t border-hairline-soft pt-md">
                  <button
                    onClick={() => react(p.id)}
                    className={`inline-flex items-center gap-1.5 rounded-sm px-md py-1.5 text-[13px] font-medium transition-colors ${
                      p.reacted
                        ? "bg-accent-green/10 text-signal-green"
                        : "text-body-mid hover:bg-canvas-soft"
                    }`}
                  >
                    <TrendingUp className="h-3.5 w-3.5" />
                    Insightful · {p.reaction_count}
                  </button>
                  {p.confidence !== null && (
                    <span className="text-[12px] text-mute">
                      author confidence {Math.round((p.confidence ?? 0) * 100)}%
                    </span>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      )}
    </AppShell>
  );
}
