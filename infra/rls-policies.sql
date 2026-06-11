-- PulseOS — OPTIONAL Postgres Row-Level Security (roadmap Step 5.2, defense-in-depth).
--
-- The app ALREADY enforces tenant isolation at the repository layer (every
-- tenant-scoped query filters by tenant_id, set per-transaction via
-- `SELECT set_config('app.tenant_id', <tid>, true)` in app/core/db.py). That is
-- sufficient for launch. This script adds a SECOND, database-level guarantee so
-- a hypothetical app bug still can't leak across tenants.
--
-- WHY IT IS NOT AN ALEMBIC MIGRATION: enabling RLS can hard-break the app if any
-- access path forgets to set the tenant context. Apply it deliberately AFTER you
-- have a staging environment to smoke-test (register → login → briefing → chat →
-- feed). Run it as the DB owner:
--     psql "$DATABASE_URL_PSYCOPG" -f infra/rls-policies.sql
--
-- It is intentionally scoped to PURELY tenant-private tables. Identity tables
-- (users, tenants, sessions, memberships) are cross-tenant by design and are read
-- without a tenant context during login, so they are excluded. The community feed
-- (posts, post_reactions, attachments) and global signals are cross-tenant
-- surfaces and are also excluded.

DO $$
DECLARE
    t text;
    -- Tables that are ALWAYS accessed with a bound app.tenant_id context.
    tenant_tables text[] := ARRAY[
        'briefings', 'briefing_items', 'memory_items', 'council_reports',
        'opportunities', 'feedback', 'conversations', 'chat_messages', 'usage_events'
    ];
BEGIN
    FOREACH t IN ARRAY tenant_tables LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', t);
        -- FORCE so the table owner (the app role) is also subject to the policy.
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', t);
        EXECUTE format('DROP POLICY IF EXISTS tenant_isolation ON %I', t);
        -- current_setting(..., true) returns NULL when unset → no rows match,
        -- so any query without a tenant context is denied (fail-closed).
        EXECUTE format($f$
            CREATE POLICY tenant_isolation ON %I
            USING (tenant_id = current_setting('app.tenant_id', true)::uuid)
            WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid)
        $f$, t);
    END LOOP;
END $$;

-- To roll back:
--   ALTER TABLE <name> DISABLE ROW LEVEL SECURITY;  (per table above)
