export interface BriefingItem {
  id: string;
  category: string;
  title: string;
  rationale: string;
  confidence: number; // 0..1
  expected_value: number | null;
  cost_of_inaction: string | null;
  evidence_refs: string[];
  council_report_id?: string | null;
  rank: number;
}

export interface Briefing {
  id: string;
  generated_at: string;
  period: string;
  summary: string | null;
  items: BriefingItem[];
}

export interface Analytics {
  time_saved_min: number;
  money_saved_usd: number;
  acted: number;
}

export interface Dashboard {
  briefing: Briefing | null;
  streams: unknown[];
  analytics: Analytics;
}

export interface Opportunity {
  id: string;
  domain: string;
  title: string;
  rationale: string | null;
  status: string;
  confidence: number;
  expected_value: number | null;
  council_report_id?: string | null;
}

export interface MemoryItem {
  id: string;
  kind: string;
  content: string;
  confidence: number;
}

export interface Dissent {
  agent: string;
  position: string;
  rationale?: string;
}

export interface CouncilReport {
  id?: string;
  tier: string;
  executive_summary: string | null;
  consensus: string | null;
  confidence: number;
  dissent: Dissent[];
  recommended_actions: string[];
  estimated_impact: number | null;
  cost_of_inaction: string | null;
  evidence: unknown[];
  agent_traces: Record<string, unknown>[];
  cost_usd: number;
  latency_ms: number;
}

export interface SearchHit {
  type: string;
  id: string;
  title: string;
  snippet?: string | null;
  domain?: string;
  source?: string;
  score: number;
}

export interface TokenPair {
  access_token: string;
  refresh_token?: string | null;
  token_type: string;
  expires_in: number;
  mfa_required: boolean;
  tenant_id: string | null;
  user_id: string | null;
}

export type FeedbackVerdict = "useful" | "not_useful" | "wrong" | "acted_on";
