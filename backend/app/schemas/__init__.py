"""Pydantic v2 request/response DTOs (API contract, Phase 2.6).

These are the stable wire contract; ORM models stay internal. `from_attributes`
lets us build responses directly from SQLAlchemy rows.
"""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- Auth ----------
class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=200)
    display_name: str | None = None
    tenant_name: str | None = None


class LoginIn(BaseModel):
    method: str = "password"
    email: EmailStr | None = None
    password: str | None = None
    provider: str | None = None
    code: str | None = None


class RefreshIn(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"
    expires_in: int = 900
    mfa_required: bool = False
    tenant_id: UUID | None = None
    user_id: UUID | None = None


# ---------- Briefings ----------
class BriefingItemOut(ORMModel):
    id: UUID
    category: str
    title: str
    rationale: str
    confidence: float
    expected_value: float | None = None
    cost_of_inaction: str | None = None
    evidence_refs: list[UUID] = []
    council_report_id: UUID | None = None
    rank: int = 0


class BriefingOut(ORMModel):
    id: UUID
    generated_at: datetime
    period: str = "daily"
    summary: str | None = None
    items: list[BriefingItemOut] = []


class BriefingListOut(BaseModel):
    items: list[BriefingOut] = []
    next_cursor: str | None = None


class AnalyticsOut(BaseModel):
    time_saved_min: int = 0
    money_saved_usd: float = 0
    acted: int = 0


class DashboardOut(BaseModel):
    briefing: BriefingOut | None = None
    streams: list[dict] = []
    analytics: AnalyticsOut = AnalyticsOut()


class FeedbackIn(BaseModel):
    verdict: str  # useful | not_useful | wrong | acted_on
    note: str | None = None


# ---------- Memory ----------
class MemoryIn(BaseModel):
    kind: str  # interest | goal | profession | preference | episodic
    content: str = Field(min_length=1, max_length=4000)


class MemoryOut(ORMModel):
    id: UUID
    kind: str
    content: str
    confidence: float = 0.7


# ---------- Opportunities ----------
class OpportunityOut(ORMModel):
    id: UUID
    domain: str
    title: str
    rationale: str | None = None
    status: str
    confidence: float
    expected_value: float | None = None
    council_report_id: UUID | None = None


class OpportunityListOut(BaseModel):
    items: list[OpportunityOut] = []
    next_cursor: str | None = None


# ---------- Council ----------
class AnalyzeIn(BaseModel):
    subject: str = Field(min_length=3, max_length=2000)
    domain: str = "general"
    tier: str = "full"


class CouncilReportOut(ORMModel):
    id: UUID | None = None
    tier: str
    executive_summary: str | None = None
    consensus: str | None = None
    confidence: float
    dissent: list[dict] = []
    recommended_actions: list[str] = []
    estimated_impact: float | None = None
    cost_of_inaction: str | None = None
    evidence: list[dict] = []
    agent_traces: list[dict] = []
    cost_usd: float = 0
    latency_ms: int = 0


# ---------- Chat ----------
class ChatIn(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: UUID | None = None


class ChatMessageOut(ORMModel):
    id: UUID
    role: str
    content: str
    created_at: datetime | None = None


class ConversationOut(ORMModel):
    id: UUID
    title: str
    updated_at: datetime | None = None


class ConversationDetailOut(ORMModel):
    id: UUID
    title: str
    messages: list[ChatMessageOut] = []


# ---------- Community feed ----------
class PostIn(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    body: str = Field(min_length=1, max_length=6000)
    category: str = "general"
    confidence: float | None = None


class PostOut(ORMModel):
    id: UUID
    author_name: str
    category: str
    title: str
    body: str
    confidence: float | None = None
    reaction_count: int = 0
    reacted: bool = False
    created_at: datetime | None = None
