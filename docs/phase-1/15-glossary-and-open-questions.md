# 15 — Glossary & Open Questions

## Glossary (shared vocabulary)

- **WARU** — Weekly Acted-on Recommendations per Active User. The North Star metric: actions taken, not articles read.
- **The Wedge** — the narrow, single-player, daily-habit entry point (Daily Briefing + single-domain Opportunity Engine for the Operator persona) we win first.
- **Strategic Council Engine** — the multi-agent reasoning pipeline (economist, statistician, psychologist, domain expert, contrarian, research analyst, executive synthesizer) producing auditable, dissent-aware, confidence-scored intelligence.
- **Two-tier pipeline** — fast path (cheap/low-latency) for time-sensitive alerts; full Council (expensive/async) for significant reports. Gating decides which runs.
- **Calibration** — the property that a stated confidence (e.g., 80%) matches realized accuracy. A gated, measured KPI; the core of the trust layer.
- **False-action rate** — share of high-confidence recommendations later judged wrong. A trust SLO.
- **Cost-of-inaction** — what the user loses by ignoring a recommendation; shown on every briefing item.
- **Expected Value (EV)** — modeled value of acting, with a range, not false precision.
- **Tenant** — the top-level isolation boundary (a person, a business, or an enterprise). Enforced by `tenant_id` + Postgres RLS + vector scoping.
- **Shared public-signal compute** — analysis of public events computed once and reused across users; the key AI-cost lever (sub-linear scaling).
- **Single-player vs. multiplayer** — features valuable with zero other users (briefing, opportunities) vs. those needing a populated network (community, corporate, reputation).
- **Gate** — hard exit criteria a release must pass before the next ecosystem begins.
- **Regulated-advice bright line** — the policy that LifeIQ gives information, not directive securities/medical/legal advice.
- **Tag conventions** — `[measured]` (from real data), `[modeled]` (from stated assumptions), `[aspirational]` (a target not yet earned).

## Open questions (must be resolved in/just after Phase 1)

### Product / strategy
1. **Which exact founding vertical + geography?** (We propose personal-finance/cost-of-living/career signals in one English-speaking metro/country — needs a decision + market validation.)
2. **Which exact persona is the very first user?** (Operator vs. Professional — affects onboarding, vertical, pricing.)
3. **Daily vs. event-driven default cadence?** (Drives the "empty briefing" risk R-6.)
4. **Is the long-term company consumer-led or enterprise-led?** (`08` raises that enterprise may be the real business. Decide what consumer is *for*.)

### AI
5. **Minimum viable Council** — how many agents actually beat single-model+critic on evals? (Must be measured before scale; collapses cost.)
6. **Which outcome signals are observable enough to drive calibration** in the founding vertical? (Determines whether the moat compounds — R-10.)
7. **Primary model provider + routing policy**, and second-vendor strategy for error de-correlation.
8. **PII handling with model providers** — redaction vs. enterprise/private inference; contractual terms.

### Monetization
9. **Real price points** for Free/Pro/Business/Enterprise (test, don't assume).
10. **Free-tier AI-cost ceiling** — what gating keeps a free MAU profitable-to-acquire?

### Infra / security
11. **ECS→EKS and Celery→RabbitMQ migration triggers** — what scale metric flips each?
12. **"Searchable forever" retention + cost + deletion policy** for meetings.
13. **Deletion-from-backups** mechanism (crypto-shredding via per-tenant keys?).
14. **When do we ingest deep financial data**, and what security bar (SOC2?) gates it?

### Org / funding
15. **Founding team composition** — who covers CEO/CTO/Principal-AI; where are the gaps?
16. **Funding milestones** mapped to the gates in `12`.

## How to use this document
- Nothing in this set is frozen except the *discipline*: wedge first, gates hard, trust/isolation non-negotiable.
- When an open question is resolved, update the relevant doc and note the decision + date here.
- Revisit this file at every gate review.

---

## Decision log (append as resolved)
| Date | Question | Decision | Rationale |
|---|---|---|---|
| 2026-06-09 | Build order | Wedge-first, gated releases (single→multiplayer) | Avoid five-mediocre-products failure (R-1) |
| _TBD_ | Founding vertical/geo | _open (Q1)_ | |
| _TBD_ | Min viable Council | _open (Q5)_ | |
