# Phase 2.3 — Indexing & Partitioning Strategy

## Principles
- Index for the **actual access patterns** below, not speculatively. Every index has a write cost.
- Tenant-scoped queries always lead with `tenant_id` in composite indexes (matches RLS predicate, enables index-only tenant pruning).
- Vector indexes (HNSW) are memory-heavy; build at R2 scale, tune `m`/`ef_construction`.
- Partition the three high-volume, time-series tables; keep everything else unpartitioned until proven necessary.

## Access patterns → indexes

### Identity
```sql
CREATE UNIQUE INDEX idx_users_email ON users (email);
CREATE INDEX idx_memberships_user ON memberships (user_id);
CREATE INDEX idx_memberships_tenant ON memberships (tenant_id, role);
CREATE INDEX idx_sessions_user_active ON sessions (user_id) WHERE revoked_at IS NULL;
CREATE INDEX idx_sessions_refresh ON sessions (refresh_token_hash);
CREATE INDEX idx_auth_provider ON auth_identities (provider, provider_sub);
```

### Intelligence core
```sql
-- briefings: "latest briefing for user"
CREATE INDEX idx_briefings_user_recent ON briefings (tenant_id, user_id, generated_at DESC);
-- briefing items: render ordered, filter by category
CREATE INDEX idx_bitems_briefing_rank ON briefing_items (briefing_id, rank);
CREATE INDEX idx_bitems_cat ON briefing_items (tenant_id, category);
-- feedback aggregation for ranking model
CREATE INDEX idx_feedback_item ON briefing_feedback (item_id, verdict);
-- opportunities: open, by domain, by score
CREATE INDEX idx_opps_open ON opportunities (tenant_id, domain, score DESC) WHERE status = 'open';
-- signals: dedup + entity + recency (per partition)
CREATE INDEX idx_signals_dedupe ON signals (dedupe_key);
CREATE INDEX idx_signals_entities ON signals USING gin (entities);
CREATE INDEX idx_signals_tags ON signals USING gin (domain_tags);
CREATE INDEX idx_signals_recent ON signals (type, ingested_at DESC);
CREATE INDEX idx_signals_geo ON signals USING gist (geo);
```

### Vector (pgvector HNSW)
```sql
-- Public namespace and per-tenant scoping handled by partial/filtered queries.
CREATE INDEX idx_signal_emb_hnsw ON signal_embeddings
  USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX idx_memory_emb_hnsw ON memory_items
  USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX idx_meeting_emb_hnsw ON meeting_intelligence
  USING hnsw (embedding vector_cosine_ops);
-- Tenant filter pushed into the query: WHERE tenant_id = :t ORDER BY embedding <=> :q LIMIT k
-- (post-filtering acceptable at MVP; at scale, per-tenant partial indexes or partitioned vector tables.)
```

### Council
```sql
CREATE INDEX idx_council_subject ON council_reports (subject_type, subject_id);
CREATE INDEX idx_council_tenant_recent ON council_reports (tenant_id, created_at DESC);
CREATE INDEX idx_traces_report ON agent_traces (council_report_id);
CREATE INDEX idx_outcomes_calib ON council_outcomes (predicted_confidence, realized);  -- calibration queries
```

### Community / reputation / communities
```sql
CREATE INDEX idx_reports_geo_domain ON reports (domain) ;
CREATE INDEX idx_reports_geo ON reports USING gist (geo);
CREATE INDEX idx_reports_verif ON reports (verification_level, created_at DESC);
CREATE INDEX idx_confirm_report ON confirmations (report_id);
CREATE INDEX idx_repevents_user ON reputation_events (user_id, created_at DESC);
CREATE INDEX idx_posts_community_recent ON posts (community_id, created_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_posts_thread ON posts (parent_id);
CREATE INDEX idx_mod_target ON moderation_actions (target_type, target_id);
CREATE INDEX idx_mod_status ON moderation_actions (status) WHERE status IN ('pending','appealed');
```

### Enterprise
```sql
CREATE INDEX idx_broadcasts_company_recent ON broadcasts (company_id, published_at DESC);
CREATE INDEX idx_follows_user ON follows (user_id);
CREATE INDEX idx_follows_target ON follows (target_kind, target_id);   -- fan-out distribution
CREATE INDEX idx_meetings_tenant ON meetings (tenant_id, created_at DESC);
CREATE INDEX idx_meetings_retention ON meetings (retention_until) WHERE retention_until IS NOT NULL;
```

### Ops
```sql
CREATE INDEX idx_usage_tenant_kind ON usage_events (tenant_id, kind, occurred_at);  -- per partition
CREATE INDEX idx_analytics_tenant_metric ON analytics_metrics (tenant_id, metric, period_start);
CREATE INDEX idx_audit_tenant_time ON audit_log (tenant_id, created_at DESC);       -- per partition
CREATE INDEX idx_audit_actor ON audit_log (actor_id, created_at DESC);
CREATE INDEX idx_deletion_status ON data_deletion_requests (status, requested_at);
```

### Trigram (fuzzy text fallback before OpenSearch)
```sql
CREATE INDEX idx_signals_title_trgm ON signals USING gin (title gin_trgm_ops);
CREATE INDEX idx_company_name_trgm ON company_accounts USING gin (name gin_trgm_ops);
```

## Partitioning strategy

| Table | Strategy | Key | Rotation | Rationale |
|---|---|---|---|---|
| `signals` | RANGE by `ingested_at` | monthly | drop/archive >18mo (config) | highest write volume; recency-biased reads |
| `usage_events` | RANGE by `occurred_at` | monthly | roll to cold storage after 13mo | metering/billing windows are monthly |
| `audit_log` | RANGE by `created_at` | monthly | retain ≥7y (compliance), move cold | append-only, compliance retention, time-range reads |

### Why these three only
They are append-heavy, time-series, and pruned by time. Everything else (briefings, opportunities, council_reports) grows linearly with users and is queried by `tenant_id`, not time-range — **list-partition by tenant only at Stage 3** (1M+ users), and even then likely by `hash(tenant_id)` into N partitions to bound table size, not per-tenant (per-tenant partitioning explodes catalog size).

### Mechanics
```sql
-- Declarative partitioning + pg_partman for automated monthly creation & retention.
CREATE TABLE signals_2026_06 PARTITION OF signals
  FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');
-- pg_partman maintains a rolling window (premake = 3 months) and detaches old partitions to S3 via pg_dump/COPY.
```
- **Default partition** captures stragglers; alerts if it ever receives rows (clock skew / late data).
- Indexes are created on the **partitioned parent** so they propagate to children (PG16).
- Constraint exclusion + partition pruning give time-bounded queries near-linear scans only on relevant partitions.

## Scale-out roadmap (DB)
1. **MVP–100k:** single primary + 1 read replica; the indexes above; monthly partitions on the 3 tables.
2. **100k–1M:** 2–3 read replicas (route briefing reads + search hydration); connection pooling (PgBouncer transaction mode, which mandates `SET app.tenant_id` via `SET LOCAL` inside the txn for RLS); move analytics to a separate warehouse (no OLAP on OLTP).
3. **1M–10M:** hash-partition the linear-growth tables by `tenant_id`; evaluate Citus/Aurora Limitless for horizontal sharding; per-region primaries for residency; dedicated vector store only if pgvector recall/latency degrade.

## Maintenance & health
- `autovacuum` tuned per high-churn table (`feedback`, `usage_events`, `sessions`); `fillfactor 80` on hot-update tables (`sessions`, `reputation`).
- Weekly `REINDEX CONCURRENTLY` budget for HNSW/GIN bloat at scale.
- Index usage audited via `pg_stat_user_indexes`; drop unused indexes quarterly (write-cost hygiene).
