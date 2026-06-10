"use client";

import React, { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { Activity, ArrowUp, Sparkles } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { api, ApiError } from "@/lib/api";
import type { ChatMessage } from "@/lib/types";

const SUGGESTIONS = [
  "What's the single highest-value thing I should do today?",
  "Pressure-test my plan to pilot an open-weight model.",
  "What signal should I be watching that I'm probably ignoring?",
  "Given my goals, where am I most exposed right now?",
];

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [convoId, setConvoId] = useState<string | undefined>(undefined);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, sending]);

  async function send(text: string) {
    const message = text.trim();
    if (!message || sending) return;
    setInput("");
    const optimistic: ChatMessage = { id: `tmp-${Date.now()}`, role: "user", content: message };
    setMessages((prev) => [...prev, optimistic]);
    setSending(true);
    try {
      const res = await api.chat(message, convoId);
      setConvoId(res.conversation_id);
      setMessages((prev) => [...prev, res.reply]);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        router.replace("/login");
        return;
      }
      setMessages((prev) => [
        ...prev,
        { id: `err-${Date.now()}`, role: "assistant", content: "I couldn't reach the analyst just now. Try again in a moment." },
      ]);
    } finally {
      setSending(false);
    }
  }

  const empty = messages.length === 0;

  return (
    <AppShell>
      <div className="flex h-[calc(100vh-3rem)] flex-col">
        <header className="mb-md">
          <div className="eyebrow mb-1">Always on</div>
          <h1 className="text-[32px] font-semibold tracking-[-0.6px] text-ink">AI Analyst</h1>
          <p className="mt-1 text-[15px] text-body-mid">
            An analyst that knows your goals and signals. Ask anything.
          </p>
        </header>

        <div ref={scrollRef} className="flex-1 space-y-md overflow-y-auto pr-1">
          {empty ? (
            <div className="flex h-full flex-col items-center justify-center text-center">
              <div className="mb-md grid h-12 w-12 place-items-center rounded-md bg-canvas-soft">
                <Sparkles className="h-6 w-6 text-ink" />
              </div>
              <h3 className="text-[18px] font-medium text-ink">How can I help you act today?</h3>
              <p className="mt-1 max-w-sm text-[14px] text-body-mid">
                I ground every answer in your memory and latest briefing.
              </p>
              <div className="mt-lg grid w-full max-w-xl grid-cols-1 gap-sm sm:grid-cols-2">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    onClick={() => send(s)}
                    className="card-flat px-md py-md text-left text-[14px] text-body hover:bg-canvas-soft"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((m) => (
              <div key={m.id} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                {m.role === "assistant" && (
                  <div className="mr-sm mt-1 grid h-7 w-7 shrink-0 place-items-center rounded-md bg-primary">
                    <Activity className="h-3.5 w-3.5 text-on-primary" />
                  </div>
                )}
                <div
                  className={`max-w-[78%] whitespace-pre-wrap rounded-md px-lg py-md text-[15px] leading-relaxed ${
                    m.role === "user"
                      ? "bg-primary text-on-primary"
                      : "card-flat text-ink-strong"
                  }`}
                >
                  {m.content}
                </div>
              </div>
            ))
          )}
          {sending && (
            <div className="flex items-center gap-sm text-mute">
              <div className="grid h-7 w-7 place-items-center rounded-md bg-primary">
                <Activity className="h-3.5 w-3.5 animate-pulse text-on-primary" />
              </div>
              <span className="text-[13px]">Analyst is thinking…</span>
            </div>
          )}
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            send(input);
          }}
          className="mt-md flex items-end gap-sm"
        >
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                send(input);
              }
            }}
            rows={1}
            placeholder="Ask your analyst…  (Enter to send, Shift+Enter for newline)"
            className="input max-h-40 flex-1 resize-none"
          />
          <button type="submit" disabled={sending || !input.trim()} className="btn-primary h-[46px] px-lg">
            <ArrowUp className="h-4 w-4" />
          </button>
        </form>
      </div>
    </AppShell>
  );
}
