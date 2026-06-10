# 11 — Database Overview

Conceptual data model + storage strategy. This is a **domain overview**, not DDL (Phase 2 produces migrations). It establishes entities, relationships, tenancy, and storage choices so the schema can be built without re-litigating fundamentals.

## Storage strategy (polyglot, but minimal at MVP)

| Store | Holds | Why |
|---|---|---|
| **Postgres** (system of record) | Users, orgs, memberships, content, reports, opportunities, briefings, council outputs, billing, audit | Relational integrity, RLS-based tenancy, transactions |
| **pgvector** (in Postgres) | Embeddings: memory, reports, meetings, signals | Co-located, tenant-scoped, no extra system at MVP |
| **OpenSearch** | Full-text + structured search index | <100ms search at scale; mirror of searchable entities |
| **Redis** | Sessions, cache, rate-limit counters, queue broker (MVP) | Speed |
| **Object storage (S3)** | Media (voice/video/docs), raw meeting recordings | Cheap, durable, encrypted |
| **Analytical store** (later) | Event/usage analytics | Keep OLAP off the OLTP DB at scale |

**Every Postgres table carries `tenant_id` and is protected by Row-Level Security** (see `10` §2). This is the backbone of isolation.

## Core domain model (conceptual)

### Identity & tenancy
- **tenant / org** — top-level isolation boundary (a person's personal space is also a tenant; an enterprise is a tenant). `id, type(personal|business|enterprise), plan, settings, region`.
- **user** — `id, email, auth_providers, mfa, status, created_at`.
- **membership** — user ↔ tenant with **role** (RBAC): owner/admin/member/viewer; resource-level grants.
- **session / device** — for anomaly detection + revocation: `device_fingerprint, ip, last_seen, risk`.

### Intelligence core
- **signal** — a normalized unit of incoming information. `id, source, type(news|market|civic|community|personal|corporate), payload, entities[], geo, domain_tags[], occurred_at, ingested_at, dedupe_key, visibility(public|tenant|private)`.
- **source** — provenance + reliability. `id, name, type, historical_reliability_score`.
- **briefing** — a generated daily/event briefing. `id, tenant_id, user_id, generated_at, sections{}, status`.
- **briefing_item** — one ranked action. `id, briefing_id, category(action|opportunity|risk|time|money|event|forecast), title, rationale, confidence, evidence_refs[], expected_value, cost_of_inaction, rank, feedback`.
- **opportunity** — `id, tenant_id, domain, score, expected_value, confidence, risk_assessment, recommended_action, regulated_flag, status, source_signals[]`.
- **council_report** — auditable AI output. `id, tenant_id, subject_ref, executive_summary, consensus, confidence, dissent[], evidence[], agent_traces[], tier(fast|full), cost, latency_ms, created_at`.
- **agent_trace** — per-agent contribution for auditability. `id, council_report_id, agent_role, claims[], citations[], stance`.

### AI memory
- **memory_item** — `id, tenant_id, user_id, kind(interest|goal|profession|preference|episodic), content, embedding, confidence, source, editable(true), created_at, updated_at`. User-inspectable/editable/deletable; deletes cascade to embeddings + search.

### Community & reputation (R2+)
- **report** (community submission) — `id, tenant_id(author), content, geo, domain, verification_score, verification_components{source,cross_source,history,confirmations}, status`.
- **confirmation** — user confirm/dispute of a report.
- **reputation** — `user_id, intelligence_reputation_score, components{accuracy,source_quality,confirmations,expertise}, history[]`.
- **community** (R3) — `id, name, domain, settings`; **membership**, **post**, **comment**, **moderation_action**(with explanation + appeal_status).

### Corporate & meetings (R4)
- **company_account** — verified entity. `id, tenant_id, verification_status, profile`.
- **broadcast** — published update (text/voice/video/doc), `distribution_status`.
- **follow** — user ↔ followable (company/team/gov/uni/startup) → personalized streams.
- **meeting** — `id, tenant_id, recording_ref(S3), transcript_ref, status, access_policy`.
- **meeting_intelligence** — `meeting_id, summary, decisions[], risks[], action_items[], embedding, searchable(true)`. Strict ABAC access; tenant + participant scoped.

### Monetization & ops
- **subscription** — `tenant_id, plan, status, seats, billing_provider_ref(Stripe)`.
- **usage_event** — for metering, fair-use, analytics.
- **audit_log** — immutable: `actor, action, target, tenant_id, ip, timestamp, metadata`. Append-only/tamper-evident.
- **analytics_metric** — derived: time_saved, money_saved, opportunities_surfaced/acted, actions_completed, briefings_read.

## Key relationships (text ERD)
```
tenant 1───* membership *───1 user
tenant 1───* signal | briefing | opportunity | council_report | memory_item | report | meeting | subscription
briefing 1───* briefing_item
council_report 1───* agent_trace
report *───* confirmation ; user 1───1 reputation
company_account 1───* broadcast ; user *───* follow ───* (company|team|gov|uni|startup)
meeting 1───1 meeting_intelligence
everything ───> audit_log
```

## Data lifecycle & retention
- **Signals:** hot for recent window; archived/aggregated after (cost control). Public analyses cached + shared (`07`/`08`).
- **Personal data:** minimized, retention-limited, **user-deletable** (GDPR/CCPA). Deletion propagates to embeddings, search index, and (per policy + legal) backups.
- **Meetings:** "searchable forever" is a product promise but a **cost + liability**; default retention configurable per tenant; enterprise controls residency + deletion. Don't promise literal-forever without a retention/cost policy.
- **Audit log:** long retention (compliance), immutable, isolated access.

## Tenancy & isolation rules (DB-enforced)
1. `tenant_id` mandatory on all tenant-scoped tables; RLS policies enforce it.
2. Vector queries always tenant-scoped; public namespace is the *only* shared embedding space and holds no private data.
3. Cross-tenant joins are forbidden by policy + tested adversarially in CI (`10`).
4. Enterprise option: separate schema/DB/namespace or private deployment.

## Migration & evolution
- Versioned migrations (Alembic) from day 1; backward-compatible, expand→migrate→contract pattern; no destructive deploys without backup + rollback plan.
- Index strategy reviewed per query pattern; pgvector index (HNSW/IVF) tuned at R2 scale.

## Honest caveats
- **pgvector scales well into the millions but not infinitely.** Re-evaluate a dedicated vector store at Stage 3 if recall/latency degrade — but not before (avoid premature systems).
- **"Searchable forever" + per-tenant isolation + AES-256 + analytics** multiply storage cost; model it early.
- **Backups complicate the right-to-deletion.** Define a compliant deletion-from-backup policy (e.g., crypto-shredding via per-tenant keys) up front.
