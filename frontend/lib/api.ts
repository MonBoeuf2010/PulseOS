"use client";

import { clearSession, getSession, saveSession } from "./auth";
import type {
  Briefing,
  ChatReply,
  Conversation,
  ConversationDetail,
  CouncilReport,
  Dashboard,
  FeedbackVerdict,
  MemoryItem,
  Opportunity,
  Post,
  SearchHit,
  TokenPair,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

interface RequestOpts {
  method?: string;
  body?: unknown;
  auth?: boolean;
}

async function request<T>(path: string, opts: RequestOpts = {}): Promise<T> {
  const { method = "GET", body, auth = true } = opts;
  const headers: Record<string, string> = { "Content-Type": "application/json" };

  if (auth) {
    const session = getSession();
    if (!session) throw new ApiError(401, "not authenticated");
    headers["Authorization"] = `Bearer ${session.token}`;
    headers["X-Tenant-Id"] = session.tenantId;
  }

  const res = await fetch(`${BASE}/v1${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
    credentials: "include",
  });

  if (res.status === 401) {
    clearSession();
    throw new ApiError(401, "session expired");
  }
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const j = await res.json();
      detail = (j as { detail?: string }).detail ?? detail;
    } catch {
      /* ignore non-JSON error bodies */
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  // ---- auth ----
  async register(email: string, password: string, displayName?: string): Promise<TokenPair> {
    const tp = await request<TokenPair>("/auth/register", {
      method: "POST",
      auth: false,
      body: { email, password, display_name: displayName },
    });
    saveSession(tp);
    return tp;
  },

  async login(email: string, password: string): Promise<TokenPair> {
    const tp = await request<TokenPair>("/auth/login", {
      method: "POST",
      auth: false,
      body: { method: "password", email, password },
    });
    saveSession(tp);
    return tp;
  },

  // ---- dashboard / briefings ----
  dashboard: () => request<Dashboard>("/dashboard"),
  listBriefings: () => request<{ items: Briefing[]; next_cursor: string | null }>("/briefings"),
  getBriefing: (id: string) => request<Briefing>(`/briefings/${id}`),
  generateBriefing: () =>
    request<{ job_id: string; status: string }>("/briefings:generate", { method: "POST" }),
  feedback: (itemId: string, verdict: FeedbackVerdict, note?: string) =>
    request<void>(`/briefing-items/${itemId}/feedback`, {
      method: "POST",
      body: { verdict, note },
    }),

  // ---- opportunities ----
  listOpportunities: (status = "open") =>
    request<{ items: Opportunity[]; next_cursor: string | null }>(
      `/opportunities?status_filter=${encodeURIComponent(status)}`,
    ),
  actOnOpportunity: (id: string) =>
    request<void>(`/opportunities/${id}:act`, { method: "POST" }),

  // ---- memory ----
  listMemory: () => request<MemoryItem[]>("/memory"),
  addMemory: (kind: string, content: string) =>
    request<MemoryItem>("/memory", { method: "POST", body: { kind, content } }),
  deleteMemory: (id: string) => request<void>(`/memory/${id}`, { method: "DELETE" }),

  // ---- search / council ----
  search: (q: string) =>
    request<{ results: SearchHit[]; next_cursor: string | null; took_ms: number }>(
      `/search?q=${encodeURIComponent(q)}`,
    ),
  analyze: (subject: string, domain = "general", tier = "full") =>
    request<{ status: string; report: CouncilReport }>("/council/analyze", {
      method: "POST",
      body: { subject, domain, tier },
    }),
  getReport: (id: string) => request<CouncilReport>(`/council/reports/${id}`),

  // ---- chat ----
  chat: (message: string, conversationId?: string) =>
    request<ChatReply>("/chat", {
      method: "POST",
      body: { message, conversation_id: conversationId },
    }),
  listConversations: () => request<Conversation[]>("/chat/conversations"),
  getConversation: (id: string) => request<ConversationDetail>(`/chat/conversations/${id}`),

  // ---- community feed ----
  feed: () => request<Post[]>("/feed"),
  createPost: (title: string, body: string, category: string, confidence?: number) =>
    request<Post>("/feed", { method: "POST", body: { title, body, category, confidence } }),
  reactToPost: (id: string) => request<Post>(`/feed/${id}/react`, { method: "POST" }),
};
