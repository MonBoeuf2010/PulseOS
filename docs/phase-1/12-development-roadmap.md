# 12 — Development Roadmap

A 0→24 month plan organized around **gated releases**. Each gate has *exit criteria* — we do not start the next ecosystem until the prior one earns it. This is the structural defense against "five mediocre products."

> Timeboxes assume a small, senior team (see `13`) and are `[modeled]`. Sequence and gates matter more than exact weeks.

---

## Phase 0 — Foundations (Weeks 0–6)
**Goal:** the rails everything rides on; nothing user-facing yet.
- Repos, CI/CD (GitHub Actions), Terraform baseline, environments (local/staging/prod), ECS/Fargate.
- Auth (email+OAuth, MFA/TOTP), RBAC + **tenancy + RLS from line one**, audit logging skeleton.
- AI Gateway (model-agnostic) + eval-harness skeleton + observability (Prometheus/Grafana/Sentry).
- Postgres + pgvector + Redis provisioned; design-system + component-library foundation (shadcn/Tailwind).
- **Security baseline:** secrets mgmt, encryption, dependency/secret scanning in CI.

**Exit:** a logged-in user exists in an isolated tenant; an agent call routes through the gateway; CI runs eval + security gates; cross-tenant test fails-closed.

## Phase 1 — MVP "Briefing" (Weeks 6–20)
**Goal:** prove the wedge (PRD H1–H4) — Daily Briefing + single-domain Opportunity Engine for the Operator persona in one vertical/geo.
- Onboarding + goal capture → AI memory (inspect/edit/delete).
- Read-only public + low-sensitivity personal connectors (calendar, location-region, public economic/market/civic). **Defer deep financial-data ingestion** (`10` §11).
- Daily Briefing (7 sections, ranked items w/ confidence/evidence/EV/cost-of-inaction, 1-tap feedback).
- **Collapsed Council** proven on evals (start minimal; add agents only where evals justify); two-tier fast/full pipeline; calibration v1 (gate confidence display on H3).
- Single-domain Opportunity Engine + regulated-advice guardrail.
- Analytics (time/$ saved `[modeled]`, actions) + weekly report; Free + Pro billing (Stripe).
- Notifications (quality-gated).

**Exit gate (must pass before R2):** H1 (≥40% find an action useful wk1), H2 (≥25% D30), H3 (calibration ±10%), H4 (≥5% Pro in 60d) — or a clear, evidence-based fix path. **If the wedge fails, we iterate the wedge — we do NOT proceed to network features to mask weak retention.**

## Phase 2 — "Network" (Months 5–9)
**Goal:** add supply + network effects *on top of a retaining product*.
- Community Intelligence Network: report submission + **AI Verification Score** + confidence display + confirm/dispute.
- **Reputation System** (Intelligence Reputation Score) — gates UGC quality, anti-brigading.
- Follow system + personalized streams.
- Universal Search (OpenSearch) — broaden coverage toward <100ms.
- WebAuthn/hardware keys; scale moves (read replicas, worker autoscaling) as load requires.

**Exit gate:** healthy contributor supply + verification precision above bar (low false-"High-confidence" rate) + network adds measurable retention, without degrading trust.

## Phase 3 — "Communities" (Months 9–15)
**Goal:** engagement depth + richer intelligence.
- AI Communities (create/join, posts/comments/debates) + **AI Moderator** (spam/abuse/misinfo/brigading/manipulation) with **explanations + human appeals**.
- Multi-domain Opportunity Engine (uses community + corporate signals).
- Migrate to EKS / RabbitMQ / streaming ingestion as scale (Stage 2→3) demands.
- Fine-tuned routing/classification/verification models where data justifies.

**Exit gate:** moderation precision/recall + appeal-overturn rate acceptable; communities are net-positive to retention (not graveyards or toxicity sinks).

## Phase 4 — "Enterprise" (Months 15–24)
**Goal:** monetize the org segment; the margin engine.
- Corporate Live Rooms (verified accounts, multi-media broadcast, real-time distribution).
- **Meeting Intelligence** (record→transcribe→decisions/risks/actions→report, semantic search, strict isolation).
- Enterprise: SSO/SCIM, custom councils, **compliance suite**, private/segregated deployment, data residency, audit-log access.
- **SOC 2 Type II** observation completed (controls started at MVP); pen tests; enterprise dashboard.

**Exit gate:** first paying enterprise logos; SOC2 achieved; tenant-isolation proven under audit; NRR trending up.

---

## Build vs. buy (decisions)
- **Buy:** foundation models, auth primitives (consider Auth provider), Stripe billing, managed Postgres/Redis/OpenSearch, transcription (initially), email/push, CDN/WAF.
- **Build:** Council orchestration, calibration/eval/outcome data, AI memory, tenancy isolation, the briefing/opportunity ranking, reputation, verification — **i.e., the moat.**

## Cross-cutting, every phase
- Eval + calibration discipline (no model/prompt change ships on a regression).
- Security: scanning, isolation tests, periodic pen tests, incident readiness.
- Accessibility (WCAG 2.2 AA) and performance budgets (Lighthouse >95) enforced in CI, not retrofitted.
- Cost-per-MAU / cost-per-report dashboards watched from day 1.

## What could compress or stretch this
- **Compress** if: the collapsed Council clearly wins early, retention is strong, and a clear enterprise pull appears (consider pulling Meeting Intelligence forward as a standalone enterprise wedge — it's the most independently sellable piece).
- **Stretch** if: calibration is hard to achieve (H3 is the sleeper risk), AI COGS won't fit budget, or the wedge needs multiple iterations. **Do not paper over a failing wedge with more features.**

## The single most important roadmap rule
**Gates are hard.** Each ecosystem ships only after its predecessor passes its exit criteria. Violating this is how the vision becomes five half-products. If forced to choose between "on schedule" and "the gate passed," the gate wins.
