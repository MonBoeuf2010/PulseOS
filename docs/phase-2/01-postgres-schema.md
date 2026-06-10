# Phase 2.1 — Complete PostgreSQL Schema

> Target: PostgreSQL 16+ with `pgvector`, `pgcrypto`, `pg_trgm`, `uuid-ossp`. All tenant-scoped tables carry `tenant_id` and are protected by Row-Level Security (RLS). This is a **specification** (DDL is the spec artifact for a schema, not application code).

## Conventions
- PK: `id uuid default gen_random_uuid()`.
- All timestamps `timestamptz`, UTC, `created_at`/`updated_at` with trigger-maintained `updated_at`.
- Soft-delete via `deleted_at timestamptz null` on user-facing content; hard-delete workflows for GDPR (see Phase 3).
- Money stored as `numeric(14,2)`; confidence/scores as `numeric(5,4)` in `[0,1]`.
- Enums via Postgres `CREATE TYPE` for stability + index efficiency.
- `tenant_id` FK → `tenants(id)` on every tenant-scoped table; RLS `USING (tenant_id = current_setting('app.tenant_id')::uuid)`.

```sql
-- ============================================================
-- EXTENSIONS
-- ============================================================
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ============================================================
-- ENUMS
-- ============================================================
CREATE TYPE tenant_type     AS ENUM ('personal','business','enterprise');
CREATE TYPE plan_tier       AS ENUM ('free','pro','business','enterprise');
CREATE TYPE member_role     AS ENUM ('owner','admin','member','viewer');
CREATE TYPE user_status     AS ENUM ('active','suspended','deleted','pending');
CREATE TYPE signal_type     AS ENUM ('news','market','civic','weather','sports','economic','community','personal','corporate','meeting');
CREATE TYPE visibility      AS ENUM ('public','tenant','private');
CREATE TYPE briefing_cat    AS ENUM ('action','opportunity','risk','time_saving','money_saving','event','forecast');
CREATE TYPE council_tier    AS ENUM ('fast','full');
CREATE TYPE agent_role      AS ENUM ('economist','statistician','psychologist','domain_expert','contrarian','research_analyst','synthesizer');
CREATE TYPE agent_stance    AS ENUM ('support','oppose','neutral','abstain');
CREATE TYPE opp_domain      AS ENUM ('financial','career','athletic','education','business','consumer_savings');
CREATE TYPE verification_lvl AS ENUM ('low','medium','high');
CREATE TYPE mod_action_type AS ENUM ('flag','remove','limit_reach','warn','none');
CREATE TYPE mod_status      AS ENUM ('pending','upheld','overturned','appealed');
CREATE TYPE sub_status      AS ENUM ('trialing','active','past_due','canceled','incomplete');
CREATE TYPE memory_kind     AS ENUM ('interest','goal','profession','preference','episodic');
CREATE TYPE follow_kind     AS ENUM ('company','team','university','government','startup');

-- ============================================================
-- IDENTITY & TENANCY
-- ============================================================
CREATE TABLE tenants (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    type          tenant_type NOT NULL DEFAULT 'personal',
    name          text NOT NULL,
    plan          plan_tier NOT NULL DEFAULT 'free',
    region        text NOT NULL DEFAULT 'us-east-1',     -- data residency
    settings      jsonb NOT NULL DEFAULT '{}',
    kms_key_id    text,                                  -- per-tenant CMK for crypto-shredding
    created_at    timestamptz NOT NULL DEFAULT now(),
    updated_at    timestamptz NOT NULL DEFAULT now(),
    deleted_at    timestamptz
);

CREATE TABLE users (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email           citext NOT NULL UNIQUE,
    email_verified  boolean NOT NULL DEFAULT false,
    display_name    text,
    avatar_url      text,
    status          user_status NOT NULL DEFAULT 'pending',
    password_hash   text,                                 -- argon2id; null for OAuth-only
    mfa_enabled     boolean NOT NULL DEFAULT false,
    primary_tenant_id uuid REFERENCES tenants(id),
    locale          text NOT NULL DEFAULT 'en-US',
    timezone        text NOT NULL DEFAULT 'UTC',
    created_at      timestamptz NOT NULL DEFAULT now(),
    updated_at      timestamptz NOT NULL DEFAULT now(),
    deleted_at      timestamptz
);

CREATE TABLE memberships (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id   uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id     uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role        member_role NOT NULL DEFAULT 'member',
    attributes  jsonb NOT NULL DEFAULT '{}',              -- ABAC attributes (dept, clearance...)
    created_at  timestamptz NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, user_id)
);

CREATE TABLE auth_identities (              -- OAuth/passkey/federated identities
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider      text NOT NULL,            -- 'google','apple','passkey','saml:<org>'
    provider_sub  text NOT NULL,            -- subject id at provider
    metadata      jsonb NOT NULL DEFAULT '{}',
    created_at    timestamptz NOT NULL DEFAULT now(),
    UNIQUE (provider, provider_sub)
);

CREATE TABLE mfa_factors (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    kind          text NOT NULL,            -- 'totp','webauthn','recovery_code'
    secret_enc    bytea,                    -- pgcrypto-encrypted TOTP secret
    credential_id text,                     -- WebAuthn credential id
    public_key    bytea,                    -- WebAuthn COSE public key
    sign_count    bigint DEFAULT 0,
    label         text,
    last_used_at  timestamptz,
    created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE sessions (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id       uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    refresh_token_hash text NOT NULL,       -- sha256 of refresh token; access tokens are stateless JWT
    device_fingerprint text,
    ip              inet,
    user_agent      text,
    risk_score      numeric(5,4) DEFAULT 0,
    expires_at      timestamptz NOT NULL,
    revoked_at      timestamptz,
    last_seen_at    timestamptz NOT NULL DEFAULT now(),
    created_at      timestamptz NOT NULL DEFAULT now()
);

-- ============================================================
-- INTELLIGENCE CORE
-- ============================================================
CREATE TABLE sources (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name          text NOT NULL,
    kind          signal_type NOT NULL,
    url           text,
    reliability   numeric(5,4) NOT NULL DEFAULT 0.5,      -- historical reliability
    metadata      jsonb NOT NULL DEFAULT '{}',
    created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE signals (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id     uuid REFERENCES tenants(id) ON DELETE CASCADE,  -- null => global/public signal
    source_id     uuid REFERENCES sources(id),
    type          signal_type NOT NULL,
    visibility    visibility NOT NULL DEFAULT 'public',
    title         text,
    body          text,
    payload       jsonb NOT NULL DEFAULT '{}',
    entities      text[] NOT NULL DEFAULT '{}',           -- extracted entities
    domain_tags   text[] NOT NULL DEFAULT '{}',
    geo           geography(Point,4326),                  -- PostGIS optional; or jsonb
    dedupe_key    text,                                   -- content hash for dedup
    occurred_at   timestamptz,
    ingested_at   timestamptz NOT NULL DEFAULT now()
) PARTITION BY RANGE (ingested_at);                       -- time-partitioned (see indexing doc)

CREATE TABLE signal_embeddings (
    signal_id     uuid PRIMARY KEY REFERENCES signals(id) ON DELETE CASCADE,
    tenant_id     uuid,                                   -- null => public namespace
    embedding     vector(1536) NOT NULL,
    model         text NOT NULL
);

CREATE TABLE briefings (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id       uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    generated_at  timestamptz NOT NULL DEFAULT now(),
    period        text NOT NULL DEFAULT 'daily',
    status        text NOT NULL DEFAULT 'ready',
    summary       text,
    metadata      jsonb NOT NULL DEFAULT '{}'
);

CREATE TABLE briefing_items (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    briefing_id     uuid NOT NULL REFERENCES briefings(id) ON DELETE CASCADE,
    tenant_id       uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    category        briefing_cat NOT NULL,
    title           text NOT NULL,
    rationale       text NOT NULL,
    confidence      numeric(5,4) NOT NULL,
    expected_value  numeric(14,2),
    ev_low          numeric(14,2),
    ev_high         numeric(14,2),
    cost_of_inaction text,
    evidence_refs   uuid[] NOT NULL DEFAULT '{}',         -- signal ids
    council_report_id uuid,
    rank            int NOT NULL DEFAULT 0,
    created_at      timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE briefing_feedback (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    item_id       uuid NOT NULL REFERENCES briefing_items(id) ON DELETE CASCADE,
    tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id       uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    verdict       text NOT NULL,            -- 'useful','not_useful','wrong','acted_on'
    note          text,
    created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE opportunities (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id         uuid REFERENCES users(id) ON DELETE CASCADE,
    domain          opp_domain NOT NULL,
    title           text NOT NULL,
    score           numeric(5,4) NOT NULL,
    expected_value  numeric(14,2),
    confidence      numeric(5,4) NOT NULL,
    risk_assessment text,
    recommended_action text,
    regulated_flag  boolean NOT NULL DEFAULT false,
    source_signals  uuid[] NOT NULL DEFAULT '{}',
    council_report_id uuid,
    status          text NOT NULL DEFAULT 'open',
    created_at      timestamptz NOT NULL DEFAULT now()
);

-- ============================================================
-- STRATEGIC COUNCIL ENGINE
-- ============================================================
CREATE TABLE council_reports (
    id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id         uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    subject_type      text NOT NULL,        -- 'briefing_item','opportunity','report','adhoc'
    subject_id        uuid,
    tier              council_tier NOT NULL,
    executive_summary text,
    consensus         text,
    confidence        numeric(5,4),
    calibration_bucket text,                -- for calibration tracking
    dissent           jsonb NOT NULL DEFAULT '[]',
    evidence          jsonb NOT NULL DEFAULT '[]',
    cost_usd          numeric(10,4),
    latency_ms        int,
    model_routing     jsonb NOT NULL DEFAULT '{}',
    created_at        timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE agent_traces (
    id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    council_report_id uuid NOT NULL REFERENCES council_reports(id) ON DELETE CASCADE,
    tenant_id         uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    agent             agent_role NOT NULL,
    stance            agent_stance NOT NULL DEFAULT 'neutral',
    claims            jsonb NOT NULL DEFAULT '[]',
    citations         jsonb NOT NULL DEFAULT '[]',
    raw_output        text,
    tokens_in         int,
    tokens_out        int,
    model             text,
    created_at        timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE council_outcomes (             -- calibration / outcome data (the moat)
    id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    council_report_id uuid NOT NULL REFERENCES council_reports(id) ON DELETE CASCADE,
    tenant_id         uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    predicted_confidence numeric(5,4),
    realized          boolean,              -- did the recommendation prove correct?
    realized_value    numeric(14,2),
    observed_at       timestamptz,
    created_at        timestamptz NOT NULL DEFAULT now()
);

-- ============================================================
-- AI MEMORY
-- ============================================================
CREATE TABLE memory_items (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id       uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    kind          memory_kind NOT NULL,
    content       text NOT NULL,
    confidence    numeric(5,4) NOT NULL DEFAULT 0.7,
    source        text,                     -- 'onboarding','inferred','user_edit'
    embedding     vector(1536),
    editable      boolean NOT NULL DEFAULT true,
    created_at    timestamptz NOT NULL DEFAULT now(),
    updated_at    timestamptz NOT NULL DEFAULT now(),
    deleted_at    timestamptz
);

-- ============================================================
-- COMMUNITY & REPUTATION  (R2+)
-- ============================================================
CREATE TABLE reports (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    author_id       uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content         text NOT NULL,
    domain          text,
    geo             geography(Point,4326),
    verification_score numeric(5,4),
    verification_level verification_lvl,
    verification_components jsonb NOT NULL DEFAULT '{}',
    status          text NOT NULL DEFAULT 'active',
    created_at      timestamptz NOT NULL DEFAULT now(),
    deleted_at      timestamptz
);

CREATE TABLE confirmations (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id     uuid NOT NULL REFERENCES reports(id) ON DELETE CASCADE,
    user_id       uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stance        text NOT NULL,            -- 'confirm','dispute'
    weight        numeric(5,4) NOT NULL DEFAULT 1.0,  -- weighted by reputation
    created_at    timestamptz NOT NULL DEFAULT now(),
    UNIQUE (report_id, user_id)
);

CREATE TABLE reputation (
    user_id       uuid PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    score         numeric(6,2) NOT NULL DEFAULT 100,
    components    jsonb NOT NULL DEFAULT '{}',  -- accuracy/source_quality/confirmations/expertise
    updated_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE reputation_events (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    delta         numeric(6,2) NOT NULL,
    reason        text NOT NULL,
    ref_type      text,
    ref_id        uuid,
    created_at    timestamptz NOT NULL DEFAULT now()
);

-- ============================================================
-- COMMUNITIES & MODERATION  (R3)
-- ============================================================
CREATE TABLE communities (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    slug          text NOT NULL UNIQUE,
    name          text NOT NULL,
    domain        text,
    settings      jsonb NOT NULL DEFAULT '{}',
    created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE community_members (
    community_id  uuid NOT NULL REFERENCES communities(id) ON DELETE CASCADE,
    user_id       uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role          text NOT NULL DEFAULT 'member',
    joined_at     timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (community_id, user_id)
);

CREATE TABLE posts (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    community_id  uuid NOT NULL REFERENCES communities(id) ON DELETE CASCADE,
    author_id     uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title         text,
    body          text NOT NULL,
    parent_id     uuid REFERENCES posts(id) ON DELETE CASCADE,   -- comments/threads
    score         numeric(6,2) NOT NULL DEFAULT 0,
    created_at    timestamptz NOT NULL DEFAULT now(),
    deleted_at    timestamptz
);

CREATE TABLE moderation_actions (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    target_type   text NOT NULL,            -- 'post','report','user'
    target_id     uuid NOT NULL,
    action        mod_action_type NOT NULL,
    reason        text NOT NULL,
    explanation   text NOT NULL,            -- always explainable (policy)
    automated     boolean NOT NULL DEFAULT true,
    status        mod_status NOT NULL DEFAULT 'pending',
    appeal_note   text,
    decided_by    uuid REFERENCES users(id),
    created_at    timestamptz NOT NULL DEFAULT now()
);

-- ============================================================
-- CORPORATE & MEETINGS  (R4)
-- ============================================================
CREATE TABLE company_accounts (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    slug          text NOT NULL UNIQUE,
    name          text NOT NULL,
    verification_status text NOT NULL DEFAULT 'unverified',
    profile       jsonb NOT NULL DEFAULT '{}',
    created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE broadcasts (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id    uuid NOT NULL REFERENCES company_accounts(id) ON DELETE CASCADE,
    tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    kind          text NOT NULL,            -- 'text','voice','video','document'
    title         text,
    body          text,
    media_url     text,
    distribution_status text NOT NULL DEFAULT 'pending',
    published_at  timestamptz,
    created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE follows (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    target_kind   follow_kind NOT NULL,
    target_id     uuid NOT NULL,
    created_at    timestamptz NOT NULL DEFAULT now(),
    UNIQUE (user_id, target_kind, target_id)
);

CREATE TABLE meetings (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    title         text,
    recording_ref text,                     -- s3 key (encrypted)
    transcript_ref text,
    access_policy jsonb NOT NULL DEFAULT '{}',  -- ABAC: participants, roles
    status        text NOT NULL DEFAULT 'processing',
    created_at    timestamptz NOT NULL DEFAULT now(),
    retention_until timestamptz             -- configurable retention
);

CREATE TABLE meeting_intelligence (
    meeting_id    uuid PRIMARY KEY REFERENCES meetings(id) ON DELETE CASCADE,
    tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    summary       text,
    decisions     jsonb NOT NULL DEFAULT '[]',
    risks         jsonb NOT NULL DEFAULT '[]',
    action_items  jsonb NOT NULL DEFAULT '[]',
    embedding     vector(1536),
    created_at    timestamptz NOT NULL DEFAULT now()
);

-- ============================================================
-- MONETIZATION & OPS
-- ============================================================
CREATE TABLE subscriptions (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    plan          plan_tier NOT NULL,
    status        sub_status NOT NULL DEFAULT 'trialing',
    seats         int NOT NULL DEFAULT 1,
    provider_ref  text,                     -- Stripe subscription id
    current_period_end timestamptz,
    created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE usage_events (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id       uuid REFERENCES users(id),
    kind          text NOT NULL,            -- 'briefing_generated','council_full','opportunity_view'
    quantity      numeric(12,4) NOT NULL DEFAULT 1,
    cost_usd      numeric(10,4),
    metadata      jsonb NOT NULL DEFAULT '{}',
    occurred_at   timestamptz NOT NULL DEFAULT now()
) PARTITION BY RANGE (occurred_at);

CREATE TABLE analytics_metrics (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id       uuid REFERENCES users(id),
    metric        text NOT NULL,            -- 'time_saved_min','money_saved_usd', etc.
    value         numeric(14,2) NOT NULL,
    period_start  date NOT NULL,
    period_end    date NOT NULL,
    created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE audit_log (                    -- append-only, tamper-evident
    id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id     uuid,
    actor_id      uuid,
    action        text NOT NULL,
    target_type   text,
    target_id     uuid,
    ip            inet,
    user_agent    text,
    metadata      jsonb NOT NULL DEFAULT '{}',
    prev_hash     bytea,                    -- hash chain for tamper-evidence
    row_hash      bytea,
    created_at    timestamptz NOT NULL DEFAULT now()
) PARTITION BY RANGE (created_at);

CREATE TABLE data_deletion_requests (      -- GDPR/CCPA workflow
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id     uuid REFERENCES tenants(id),
    user_id       uuid REFERENCES users(id),
    kind          text NOT NULL,           -- 'export','delete','rectify'
    status        text NOT NULL DEFAULT 'received',
    requested_at  timestamptz NOT NULL DEFAULT now(),
    completed_at  timestamptz,
    receipt       jsonb NOT NULL DEFAULT '{}'
);
```

## Row-Level Security (applied to every tenant-scoped table)
```sql
ALTER TABLE briefings ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON briefings
  USING (tenant_id = current_setting('app.tenant_id', true)::uuid);
-- repeated for every tenant-scoped table; app sets `SET app.tenant_id` per request via connection pooler hook.
-- A separate `app_admin` role bypasses RLS only for break-glass ops (audited).
```

## `updated_at` trigger (applied where present)
```sql
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS trigger AS $$
BEGIN NEW.updated_at = now(); RETURN NEW; END $$ LANGUAGE plpgsql;
-- CREATE TRIGGER trg_updated_at BEFORE UPDATE ON <table>
--   FOR EACH ROW EXECUTE FUNCTION set_updated_at();
```

See `02-erd.md` for relationships and `03-indexing-partitioning.md` for indexes and partitioning.
