"use client";

import type { TokenPair } from "./types";

const TOKEN_KEY = "pulse_access";
const TENANT_KEY = "pulse_tenant";
const USER_KEY = "pulse_user";

export interface Session {
  token: string;
  tenantId: string;
  userId: string;
}

export function saveSession(tp: TokenPair): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(TOKEN_KEY, tp.access_token);
  if (tp.tenant_id) localStorage.setItem(TENANT_KEY, tp.tenant_id);
  if (tp.user_id) localStorage.setItem(USER_KEY, tp.user_id);
}

export function getSession(): Session | null {
  if (typeof window === "undefined") return null;
  const token = localStorage.getItem(TOKEN_KEY);
  const tenantId = localStorage.getItem(TENANT_KEY);
  const userId = localStorage.getItem(USER_KEY);
  if (!token || !tenantId) return null;
  return { token, tenantId, userId: userId ?? "" };
}

export function clearSession(): void {
  if (typeof window === "undefined") return;
  [TOKEN_KEY, TENANT_KEY, USER_KEY].forEach((k) => localStorage.removeItem(k));
}
