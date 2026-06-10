# Phase 2.7 — Redis, Queue, Search & AI Data Pipeline Architecture

## A. Redis strategy

Redis is used for **five distinct concerns**, logically separated by key-prefix and (at scale) by dedicated instances/databases so one workload can't evict another.

| Concern | Pattern | Keying | TTL / eviction | Notes |
|---|---|---|---|---|
| **Session/refresh** | hash | `sess:{session_id}` | = session expiry | refresh-token hash, device, risk; revocation = delete |
| **Cache (read models)** | string/JSON | `cache:dash:{tenant}:{user}` | 30–120s | dashboard, briefing render; invalidated on `briefing.generated` |
| **AI response cache** | string | `ai:public:{sha256(prompt+model)}` | hours–days | **shared public-signal analyses** (the COGS lever) — only for non-tenant data |
| **Rate limiting** | sorted-set / token bucket | `rl:{scope}:{id}:{window}` | window | sliding-window + token bucket; per-user/tenant/endpoint |
| **Queue broker (MVP)** | lists/streams | Celery default | — | graduate to RabbitMQ at R2 |
| **Idempotency / dedupe** | set | `idem:{key}`, `evt:{event_id}` | 24h | safe retries, exactly-once consumers |
| **Locks** | string + token | `lock:{resource}` | short | Redlock-style for single-flight (e.g., one briefing build per user) |
| **Realtime pub/sub** | pub/sub / streams | `rt:{tenant}:{user}` | — | push council/briefing completion to SSE/WS gateway |

### Caching rules (critical for cost + correctness)
- **Public-signal analysis is cached and shared across tenants** (no private data in key or value) — this is what makes AI COGS sub-linear (`08`, Phase 1).
- **Per-user/personalized results are cached per (tenant,user)** and never shared.
- **Cache-aside** for reads; **write-through invalidation** on the triggering event. Never cache a tenant-scoped value under a non-tenant key.
- Eviction policy: `allkeys-lru` for cache DBs; **`noeviction`** for the broker/session DB (losing those silently is a correctness bug, not a cache miss).
- Single-flight via locks to prevent thundering-herd recompute of an expired hot key.

### HA / scale
- MVP: single managed Redis (ElastiCache) + replica for failover.
- Scale: **Redis Cluster** (sharded) for cache; separate cluster for rate-limit (hot, small); broker migrates to RabbitMQ; sessions on their own replicated instance. Persistence: AOF everywhere except pure cache (RDB snapshot only).

## B. Queue architecture

### Topology (broker-agnostic; RRabbitMQ exchange names shown for R2+)
```
exchange: pulse.events            (topic)
  routing keys: signal.*, council.*, briefing.*, report.*, broadcast.*, meeting.*, security.*

queues (per consumer group, bound to keys):
  q.enrich            <- signal.ingested
  q.embed             <- signal.enriched
  q.council           <- council.requested            (priority queue; fast vs full)
  q.briefing          <- council.completed, signal.indexed
  q.opportunity       <- signal.enriched, council.completed
  q.verify            <- report.submitted
  q.moderation        <- report.submitted, post.created
  q.distribute        <- broadcast.published           (fan-out, sharded by follower range)
  q.meeting           <- meeting.recorded
  q.notify            <- briefing.generated, opportunity.detected, moderation.flagged
  q.analytics         <- usage.recorded, *.completed   (low priority)
  q.audit             <- #  (all events; never on critical path)
  dlx: pulse.dlx -> q.dead.<name>   (per-queue dead-letter)
```

### Worker pools (Celery → autoscaled)
| Pool | Concurrency model | Scaling signal | Isolation |
|---|---|---|---|
| ingestion/enrich | I/O-bound, high concurrency | queue depth | own pool |
| embed/index | batch, GPU-less | backlog age | batched calls to AI Gateway |
| **council** | CPU+network heavy, gated | depth + cost budget | **separate pool/cluster** (most expensive) |
| briefing | mixed | per-user schedule + events | — |
| distribute/notify | spiky fan-out | depth | own pool, rate-limited egress |
| meeting | long-running, media | job count | own pool (transcription) |
| analytics/audit | low priority | lag tolerance | cheapest instances/spot |

### Reliability
- **Priority queues:** time-sensitive alerts > scheduled briefings > analytics.
- **Retries:** exponential backoff + jitter, max attempts, then DLQ + alert.
- **Idempotency:** every task keyed by `event_id`; re-delivery is a no-op.
- **Poison handling:** DLQ inspection tooling in Admin; replay after fix.
- **Backpressure:** the council gater sheds low-value work first; bounded prefetch per worker.
- **Scheduled work:** Celery Beat for periodic briefings, retention sweeps, calibration recompute, reputation decay.

## C. Search architecture (OpenSearch)

### Indices
| Index | Source of truth | Fields | Refresh |
|---|---|---|---|
| `idx_signals` | signals | title, body, entities, tags, geo, ts | near-real-time |
| `idx_reports` | reports | content, domain, geo, verification | NRT |
| `idx_companies` | company_accounts | name, profile | on change |
| `idx_communities` | communities/posts | name, body | NRT |
| `idx_meetings` | meeting_intelligence | summary, decisions, actions (tenant-scoped) | on analyze |
| `idx_opportunities` | opportunities | title, domain, action | on create |
| `idx_people` | users (opt-in/public) | display_name, expertise | on change |

### Design
- **Postgres is the system of record; OpenSearch is a derived index** fed by `*.indexed` events (CDC/outbox → indexer worker). Never write search-only data.
- **Tenant isolation in search:** every doc carries `tenant_id`; **every query is filtered by tenant** (and `visibility`) via a mandatory filter injected server-side — clients cannot remove it. Meetings/private docs are hard-scoped; public signals live in a shared, no-PII namespace.
- **Hybrid retrieval:** BM25 (OpenSearch) **+ vector** (pgvector or OpenSearch k-NN) fused via reciprocal-rank-fusion; re-ranked by relevance + recency + source reliability + personalization (memory).
- **Universal search** queries multiple indices in parallel, merges, returns typed results. Target p95 <100ms at scale (MVP <300ms acceptable).
- **Analyzers:** language analyzers, synonyms, edge-ngram for prefix; entity fields keyword for filtering.
- **Index lifecycle (ILM):** hot→warm→cold rollover for time-series signal index; delete per retention.

### Consistency model
Search is **eventually consistent** with Postgres (sub-second target). For "must be exact" reads (a single record), the API hits Postgres, not search. Reconciliation job re-indexes drift nightly.

## D. AI data pipeline architecture (end-to-end)

```
SOURCES                INGEST            ENRICH                INDEX/EMBED         INTELLIGENCE
news/RSS  ┐                                                                       ┌ briefing
markets   ├─ connectors ─ normalize ─ dedupe ─ entity/geo/   ─ embed(pgvector) ─ ┤ opportunity
civic/econ│   (rate-     (schema)    (hash)    domain tag      + index(OS)        │ council (gated)
weather   │    limited)                         classify                          └ search
sports    │
web crawl ┘                              │
personal* (consent, read-only) ──────────┘   (*tenant-private, never shared compute)
```

### Stages
1. **Connectors** (pluggable, per-source): pull/stream, respect ToS + rate limits + robots; attach `source_id` + provenance. Personal connectors are consent-gated, read-only, tenant-private.
2. **Normalize:** map to canonical `signal` shape; language detect; strip boilerplate.
3. **Dedupe:** content hash (`dedupe_key`) + near-dup (minhash/embedding cosine) to avoid re-analyzing the same story N times (cost lever).
4. **Enrich:** entity extraction, geo-tag, domain classification, sentiment/impact tag, source-reliability join.
5. **Embed + Index:** embeddings → pgvector (tenant-scoped or public namespace); full-text → OpenSearch.
6. **Relevance scoring:** per active user, score signal against memory/goals (cheap model + features) → decides whose briefing it can enter.
7. **Council gating:** `value × uncertainty × relevance > θ` → `council.requested` (full); else fast-path summarize. Most signals stop here.
8. **Strategic Council Engine:** (Phase 6) produces calibrated, dissent-aware report → `council.completed`.
9. **Assembly:** briefing builder + opportunity engine compose ranked, personalized outputs.

### Cross-cutting
- **Shared vs. private compute:** public-signal enrichment/analysis computed once, cached (`ai:public:*`), reused across users; personalization is the only per-user cost. **No private data ever enters shared cache.**
- **Provenance & attribution:** every derived claim carries `signal_id` → source; surfaced as evidence; legal/source-attribution preserved end-to-end (Phase 8 compliance).
- **PII redaction** before any provider call (AI Gateway), where feasible.
- **Eval hooks:** sampled outputs flow to the eval/calibration harness (Phase 6/9); regressions gate model/prompt changes in CI.
- **Cost metering:** every AI Gateway call emits `usage.recorded` with token + USD cost → COGS dashboards (the budget discipline from Phase 1).
