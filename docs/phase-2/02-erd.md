# Phase 2.2 — ER Diagrams & Relationships

Rendered with Mermaid (GitHub-native). Split by bounded context to stay legible.

## Core: Identity, Tenancy & Intelligence
```mermaid
erDiagram
    tenants ||--o{ memberships : has
    users   ||--o{ memberships : in
    tenants ||--o{ subscriptions : bills
    users   ||--o{ auth_identities : federates
    users   ||--o{ mfa_factors : secures
    users   ||--o{ sessions : opens
    tenants ||--o{ sessions : scopes

    tenants ||--o{ signals : owns
    sources ||--o{ signals : produces
    signals ||--|| signal_embeddings : vectorizes

    tenants  ||--o{ briefings : generates
    users    ||--o{ briefings : for
    briefings ||--o{ briefing_items : contains
    briefing_items ||--o{ briefing_feedback : receives
    briefing_items }o--o{ signals : "evidence_refs"

    tenants ||--o{ opportunities : surfaces
    tenants ||--o{ memory_items : remembers
    users   ||--o{ memory_items : owns

    tenants  ||--o{ council_reports : produces
    council_reports ||--o{ agent_traces : "7 agents"
    council_reports ||--o{ council_outcomes : "calibration"
    briefing_items  }o--|| council_reports : "explained_by"
    opportunities   }o--|| council_reports : "explained_by"
```

## Network: Community, Reputation, Communities
```mermaid
erDiagram
    tenants ||--o{ reports : hosts
    users   ||--o{ reports : authors
    reports ||--o{ confirmations : validated_by
    users   ||--|| reputation : scored_by
    users   ||--o{ reputation_events : history

    communities ||--o{ community_members : has
    users       ||--o{ community_members : joins
    communities ||--o{ posts : contains
    users       ||--o{ posts : writes
    posts       ||--o{ posts : "replies (parent_id)"
    posts       ||--o{ moderation_actions : "may trigger"
    reports     ||--o{ moderation_actions : "may trigger"
```

## Enterprise: Corporate Rooms & Meetings
```mermaid
erDiagram
    tenants ||--o{ company_accounts : owns
    company_accounts ||--o{ broadcasts : publishes
    users ||--o{ follows : follows
    company_accounts ||--o{ follows : "followed_as company"
    tenants ||--o{ meetings : records
    meetings ||--|| meeting_intelligence : analyzed_to
```

## Ops & Compliance
```mermaid
erDiagram
    tenants ||--o{ usage_events : meters
    tenants ||--o{ analytics_metrics : measures
    tenants ||--o{ audit_log : logs
    users   ||--o{ data_deletion_requests : files
    tenants ||--o{ data_deletion_requests : scopes
```

## Relationship rules (referential integrity & cascade policy)
| Parent | Child | On delete | Reason |
|---|---|---|---|
| tenants | (all tenant-scoped) | CASCADE | tenant offboarding / hard-delete |
| users | memberships, sessions, mfa_factors, auth_identities | CASCADE | account deletion |
| users | memory_items, briefings, reports | CASCADE (then crypto-shred) | GDPR erasure |
| briefings | briefing_items | CASCADE | composition |
| council_reports | agent_traces, council_outcomes | CASCADE | composition |
| communities | posts, community_members | CASCADE | composition |
| meetings | meeting_intelligence | CASCADE | composition |
| audit_log | — | RESTRICT (never cascade) | tamper-evidence; retained per compliance |

**Note:** `audit_log` and `data_deletion_requests` are intentionally NOT cascade-deleted when a user is erased — they retain a minimized, lawful record of the erasure itself (legal basis: compliance obligation). PII within them is tokenized/redacted, not the event.

## Polymorphic references
`moderation_actions.target_id`, `council_reports.subject_id`, `usage_events`, `reputation_events.ref_id` use `(type, id)` pairs rather than FKs (polymorphic). Integrity enforced at the service layer + periodic reconciliation jobs, not DB FKs — a deliberate trade-off for flexibility documented here so it isn't mistaken for a missing constraint.
