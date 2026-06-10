# 05 — Feature Map

Full inventory of the PulseOS surface, prioritized with **MoSCoW** (Must / Should / Could / Won't-yet) and mapped to release phase. "Won't-yet" ≠ never; it means *not before this gate*.

Legend — Phase: **M**=MVP, **2/3/4**=R2/R3/R4. Priority: **Mu/Sh/Co/Wo**.

---

## Ecosystem 1 — Intelligence Dashboard (Page 1)

| Feature | Phase | Pri | Notes / dependency |
|---|---|---|---|
| Daily Intelligence Briefing | M | Mu | Core wedge surface |
| Sections: Immediate Actions / Opportunities / Risks / Time / Money / Events / Forecasts | M | Mu | Some sections may be empty early — handle gracefully |
| Per-item: confidence, evidence, EV, cost-of-inaction | M | Mu | Trust contract |
| 1-tap feedback (useful/wrong/acted-on) | M | Mu | Trains ranking + memory |
| Ranking by EV × confidence × relevance, precision-first | M | Mu | Depends on Council + memory |
| Configurable schedule + event-driven briefings | M | Sh | Notification quality SLO |
| Public + personal data fusion | M | Mu | Connectors, consent |
| Forecasts module | 2 | Sh | Needs time-series + eval discipline |

## Ecosystem 2 — Corporate Live Rooms (Page 2)

| Feature | Phase | Pri | Notes |
|---|---|---|---|
| Verified company accounts | 4 | Mu | Verification/KYC process |
| Live feed: text/voice/video/docs | 4 | Mu | Media pipeline, CDN |
| Real-time distribution to followers | 4 | Mu | Fan-out infra |
| **Meeting Intelligence** (record→transcribe→summarize→decisions/risks/actions→report) | 4 | Mu | High-stakes accuracy + security |
| Semantic search over meetings, "forever" | 4 | Mu | pgvector/OpenSearch, retention policy |
| Follow system (companies/teams/govs/unis/startups) | 2 | Sh | Pull forward partially in R2 for streams |

## Ecosystem 3 — Community Intelligence Network (Page 3)

| Feature | Phase | Pri | Notes |
|---|---|---|---|
| User report submission | 2 | Mu | UGC supply |
| AI Verification Score (source/cross-source/history/confirmations) | 2 | Mu | Misinformation defense — core |
| Confidence + verification display | 2 | Mu | Humility by default |
| Community confirmations/disputes | 2 | Sh | Anti-brigading needed |

## Ecosystem 4 — AI Communities (Page 4)

| Feature | Phase | Pri | Notes |
|---|---|---|---|
| Create/join communities | 3 | Sh | Cold-start risk; seed carefully |
| Posts/comments/debates/reports/live rooms | 3 | Sh | |
| **AI Community Moderator** (spam/abuse/misinfo/brigading/manipulation) | 3 | Mu | With explanations + **human appeal** |
| Moderation transparency + appeals | 3 | Mu | Trust + legal |

## Ecosystem 5 — Opportunity Engine (Page 5)

| Feature | Phase | Pri | Notes |
|---|---|---|---|
| Single-domain engine (founding vertical) | M | Mu | Wedge value driver |
| Outputs: Score / EV / Confidence / Risk / Action | M | Mu | |
| Regulated-advice guardrail | M | Mu | Liability bright line |
| Multi-domain expansion | 3 | Sh | After single-domain proven |
| Cross-ecosystem scanning (uses community + corporate signals) | 3 | Sh | Network amplifies it |

## Cross-cutting platform

| Feature | Phase | Pri | Notes |
|---|---|---|---|
| **Strategic Council Engine** (7 agents, two-tier fast/full) | M | Mu | See `07` |
| Auditable agent reasoning (who said what, dissent) | M | Mu | Trust + debugging |
| **AI Memory** (inspect/edit/delete) | M | Mu | GDPR/CCPA-aligned |
| Universal Search (people/reports/companies/communities/meetings/opportunities) | 2 | Sh | <100ms target; MVP search is narrow |
| **Reputation System** (Intelligence Reputation Score) | 2 | Mu | Gates UGC quality |
| Analytics (time/$ saved, opportunities, actions) | M | Sh | Drives retention + upsell |
| Weekly personal intelligence report | M | Sh | Retention |
| Notifications (quality-gated) | M | Mu | Habit driver; noise = death |

## Identity, billing, admin

| Feature | Phase | Pri | Notes |
|---|---|---|---|
| Auth (email + OAuth), MFA/TOTP | M | Mu | WebAuthn fast-follow |
| WebAuthn / hardware keys | 2 | Sh | Enterprise need |
| RBAC | M | Mu | Org/tenant model from day 1 |
| SSO/SCIM | 4 | Mu | Enterprise |
| Subscription billing (Free/Pro) | M | Mu | Stripe |
| Business/Enterprise billing, seats, invoicing | 4 | Mu | |
| Audit logging | M | Mu | Security + compliance |
| Admin dashboard | M | Sh | Ops + moderation tooling |
| Enterprise/compliance dashboard | 4 | Mu | |
| Onboarding flow | M | Mu | Time-to-value |
| Mobile-responsive design system + component library | M | Mu | Mobile-first |

## Explicit "Won't-yet" (Wo) — guardrails against scope creep
- Native mobile apps (start responsive web/PWA) — **Wo until R3** unless data forces it.
- Personalized financial/medical/legal advice — **Wo** (policy, not phase).
- Global multi-geo/multi-lingual coverage — **Wo until R3**; win one geo first.
- Open API / developer platform — **Wo until R4**.
- On-the-fly user-defined custom agents — **Wo until R4** (enterprise custom councils).

## Dependency graph (what blocks what)
```
Auth/RBAC/Tenancy ──> everything
AI Memory + Council ──> Briefing + Opportunity Engine (MVP core)
Briefing retention proven ──> Community Network (R2)
Community + Reputation ──> AI Communities (R3) ──> richer Opportunity Engine
All of the above + Security/Compliance maturity ──> Corporate Rooms + Enterprise (R4)
```
**Rule:** no ecosystem ships before its upstream dependency hits its success gate (see `12`). This is the primary defense against the "five mediocre products" failure mode.
