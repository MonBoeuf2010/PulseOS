# Phase 2.5 — Service Boundaries & Microservice Breakdown

## Stance: modular monolith first, extract on evidence
We define **clear service boundaries now** (so the code is organized around them and can be extracted later) but **deploy a modular monolith at MVP**. Premature microservices are an operational tax a pre-PMF team cannot afford. Each module below = a future service; today it's a package with an enforced internal API and its own schema namespace.

```
                 ┌────────────────────────────────────────────────┐
                 │                   API Gateway                    │
                 │  authn, rate-limit, WAF, routing, request trace  │
                 └───────────────┬───────────────────┬─────────────┘
        ┌──────────────┬─────────┴───────┬───────────┴───────┬───────────────┐
        ▼              ▼                 ▼                   ▼               ▼
   ┌─────────┐   ┌───────────┐    ┌────────────┐     ┌────────────┐   ┌──────────┐
   │ Identity│   │ Briefing  │    │  Council   │     │ Opportunity│   │ Community│
   │ &Access │   │ &Dashboard│    │  Engine    │     │  Engine    │   │ &Network │
   └─────────┘   └───────────┘    └────────────┘     └────────────┘   └──────────┘
        ▼              ▼                 ▼                   ▼               ▼
   ┌─────────┐   ┌───────────┐    ┌────────────┐     ┌────────────┐   ┌──────────┐
   │ Memory  │   │ Ingestion │    │  Search    │     │ Corporate  │   │ Billing  │
   │ Service │   │ Pipeline  │    │  Service   │     │ &Meetings  │   │ &Usage   │
   └─────────┘   └───────────┘    └────────────┘     └────────────┘   └──────────┘
        ▼                                                                  ▼
   ┌──────────────────────────── Platform services ──────────────────────────────┐
   │  Notifications · Audit/Compliance · Admin · AI Gateway · Event Bus           │
   └──────────────────────────────────────────────────────────────────────────────┘
```

## Service catalog

| # | Service | Owns (data) | Responsibilities | Sync API | Events in/out |
|---|---|---|---|---|---|
| 1 | **Identity & Access** | tenants, users, memberships, sessions, mfa, auth_identities | authn, RBAC/ABAC, MFA/passkeys, sessions, SSO/SCIM | `/auth/*`, `/users/*`, `/tenants/*` | out: `user.*`, `security.anomaly` |
| 2 | **Briefing & Dashboard** | briefings, briefing_items, feedback | assemble/rank briefings, serve dashboard, capture feedback | `/briefings/*`, `/dashboard` | in: `signal.indexed`, `council.completed`; out: `briefing.generated`, `briefing.item_feedback` |
| 3 | **Council Engine** | council_reports, agent_traces, council_outcomes | orchestrate agents, debate, consensus, confidence, calibration | `/council/*` (internal) | in: `council.requested`; out: `council.completed` |
| 4 | **Opportunity Engine** | opportunities | detect/score opportunities, EV, risk, guardrails | `/opportunities/*` | in: `signal.enriched`, `council.completed`; out: `opportunity.detected` |
| 5 | **Memory** | memory_items | store/inspect/edit/delete user memory, embeddings | `/memory/*` | out: memory updates |
| 6 | **Ingestion Pipeline** | sources, signals, signal_embeddings | connectors, normalize, dedupe, enrich, embed, index | internal | out: `signal.*` |
| 7 | **Search** | OpenSearch indices (mirror) | universal search, indexing, ranking | `/search` | in: `*.indexed` |
| 8 | **Community & Network** | reports, confirmations, reputation, communities, posts, moderation | UGC, verification, reputation, communities, AI moderation, follows | `/community/*`, `/reports/*`, `/follows/*` | in/out: `report.*`, `moderation.*`, `reputation.changed` |
| 9 | **Corporate & Meetings** | company_accounts, broadcasts, meetings, meeting_intelligence | verified accounts, broadcast fan-out, meeting intelligence | `/companies/*`, `/meetings/*`, `/broadcasts/*` | in: `broadcast.published`, `meeting.recorded`; out: `meeting.analyzed` |
| 10 | **Billing & Usage** | subscriptions, usage_events, analytics_metrics | Stripe, plans/seats, metering, fair-use, analytics | `/billing/*`, `/analytics/*` | in: `usage.recorded` |
| 11 | **Notifications** | (stateless + prefs) | push/email/in-app, quality gating | `/notifications/*` | in: many; out: deliveries |
| 12 | **Audit & Compliance** | audit_log, data_deletion_requests | append-only audit, GDPR export/erase orchestration | `/admin/audit/*`, `/privacy/*` | in: all; out: erasure steps |
| 13 | **Admin** | (cross-cutting reads) | ops console, moderation queue, support tooling | `/admin/*` | — |
| 14 | **AI Gateway** | (stateless) | model-agnostic routing, caching, cost/eval hooks, PII redaction | internal SDK | — |

## Boundary rules (enforced)
1. **No cross-service DB access.** A service touches only its own tables/schema. Cross-service reads go through the service's API or via events (data is replicated into read models where needed). This is what makes later extraction mechanical.
2. **Tenant context flows everywhere.** `tenant_id` is set on the DB connection (RLS) and present on every event/request.
3. **Sync for queries that block a user; async (events) for everything else.** A briefing read is sync; generating it is async.
4. **The AI Gateway is the only path to model providers.** No service calls a model vendor directly (cost, routing, redaction, eval, isolation).
5. **Audit & Compliance subscribes to everything** but is on no service's critical path.

## Extraction order (when the monolith strains)
1. **Council Engine** + **Ingestion** (most CPU/cost-intensive, independent scaling) — extract first.
2. **Search** (different runtime/scaling profile).
3. **Corporate & Meetings** (media/transcription heavy, enterprise isolation).
4. **Notifications** (spiky fan-out).
Identity, Billing, Briefing stay in the core longest (chatty, transactional).

## Internal contracts
Each module exposes a typed internal interface (Python Protocols / Pydantic models) identical in shape to its future REST/gRPC contract, so extraction = swap in-process call for network call behind the same interface. Contract tests guard both sides.
