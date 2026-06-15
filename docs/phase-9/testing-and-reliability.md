# Phase 9 — Testing & Reliability

> Authored as a world-class QA + SRE organization. Target: **99.99% uptime** (≈52 min/yr downtime), enterprise reliability, millions of users. Reliability is a *budget* (error budgets gate release velocity), not a slogan.

## 1. Test strategy (the pyramid + the AI-specific layer)
```
        /\        E2E + journey (few, critical paths)
       /  \       Contract tests (service boundaries, OpenAPI)
      /----\      Integration (DB+Redis+queue+search, real deps in containers)
     /------\     Unit (many, fast, pure logic)
    /--------\    + AI Eval layer (calibration, hallucination, prompt-injection) — LifeIQ-specific
```

### Unit
- Pure domain logic, services, scorers, policy engine (RBAC/ABAC decisions), ranking, EV math.
- Frameworks: backend `pytest` (+ `hypothesis` property tests for scoring/calibration math, money rounding, dedupe); frontend `vitest` + React Testing Library.
- Coverage target **≥85% on core domain** (not a vanity 100%; cover branches that matter — authz, money, isolation).

### Integration
- Real Postgres (+pgvector), Redis, OpenSearch, broker in `testcontainers` / docker-compose. No mocks for the data layer.
- **Tenancy isolation tests are mandatory and adversarial:** every repository test attempts a cross-tenant read/write and asserts RLS denies it. A passing cross-tenant access **fails CI** (ties to Phase 3 §2.3).
- Migration tests: up/down, idempotency, zero-downtime expand→contract.

### Contract
- OpenAPI as source of truth → generated client/server stubs; **consumer-driven contract tests** (Pact-style) at every service boundary so extraction (Phase 2.5) is safe.
- Webhook signature/replay tests (Stripe inbound, outbound HMAC).

### E2E (critical journeys only)
- Playwright. Cover Phase 1 journeys: first-run→briefing (<60s activation), feedback loop, opportunity→act (WARU), council deep-dive, community submit→verify, enterprise meeting→intelligence, privacy export/delete.
- Run on staging against real services + seeded data; visual regression on key screens.

### AI eval layer (unique to LifeIQ — gates model/prompt changes)
- **Golden eval sets** per surface (briefing relevance, opportunity EV accuracy, verification correctness, council synthesis quality).
- **Calibration tests:** predicted vs. realized confidence; ECE/Brier must stay within bar (Phase 1 H3) or the change is blocked.
- **Hallucination tests:** factual claims must be source-grounded; ungrounded claims flagged → fail.
- **Prompt-injection / red-team suite:** adversarial inputs (instructions hidden in ingested content) must not change agent behavior or leak context (Phase 3 vector #2).
- **LLM-as-judge** with human audit of the judge (anti-gaming); regression gates in CI.

## 2. Non-functional / specialized tests

### Load & performance
- `k6`/Locust scenarios mapped to scale stages (10k→1M). Assert NFRs: API p95 <250ms, search p95 <100ms (scale), briefing freshness ≤15min, council async p95 <60s.
- Soak (24h) for memory leaks; spike tests for fan-out (broadcast to N followers); **cost-load tests** (does council gating hold COGS under load?).

### Security tests (continuous)
- SAST, SCA (deps), secret scanning, container scanning, IaC scanning (CSPM/policy-as-code) — every PR.
- DAST + auth/IDOR/BOLA fuzzing pre-release; annual third-party pen test + bug bounty (R2).
- Authz fuzzing on every `/{id}` route (object-level access).

### Chaos engineering
- Game-days injecting: DB primary failover, Redis loss, broker outage, **AI Gateway/provider outage** (assert graceful degradation → last-good briefing, app stays useful), region AZ loss, latency injection, dependency timeouts.
- Tooling: fault injection (e.g., AWS FIS / chaos-mesh on k8s). Steady-state hypotheses + automated rollback. Run in staging, then controlled prod game-days.

## 3. Reliability architecture (SRE)

### SLOs & error budgets
| Service | SLI | SLO | Error budget policy |
|---|---|---|---|
| API (interactive) | availability, p95 latency | 99.95% / <250ms | budget burn freezes feature releases |
| Briefing freshness | ingest→briefing | ≤15 min (99%) | |
| Council async | completion <60s | 99% | |
| Search | p95 <100ms | 99.9% | |
| Platform overall | composite | **99.99%** | multi-burn-rate alerts |
- Multi-window, multi-burn-rate alerting; budgets reviewed weekly; **releases slow when budget is spent** (reliability governs velocity).

### Redundancy & failover
- Multi-AZ from Stage 2; multi-region (active-passive → active-active) at Stage 3+ for residency + DR.
- Stateless app tier behind LB; autoscaling; PgBouncer; read replicas; Redis replica/cluster; queue HA; OpenSearch multi-node.
- **Graceful degradation tiers:** (1) full; (2) AI degraded → serve cached intelligence + last briefing; (3) read-only mode; (4) static status page. The app must be *useful* at tier 2.

### Monitoring architecture
- **Metrics:** Prometheus + Grafana (RED + USE + business KPIs: WARU, cost/MAU, calibration error, council cost).
- **Tracing:** OpenTelemetry end-to-end (request → events → council → providers); `trace_id` everywhere.
- **Logs:** structured JSON, centralized (Loki/ELK), no PII/secrets, correlated by trace_id.
- **Errors:** Sentry (frontend + backend) with release health.
- **Synthetic monitoring:** uptime + critical-journey probes from multiple regions.
- **Alerting:** PagerDuty/on-call; symptom-based (SLO burn) over cause-based; runbooks linked from every alert; sane thresholds to avoid fatigue.

## 4. Backup & disaster recovery

### Backup architecture
- Postgres: continuous WAL archiving + PITR (35-day window) + periodic full snapshots; **cross-region** copies; encrypted (per-tenant keys → crypto-shred compatible).
- S3 (media/exports): versioning + Object Lock (WORM) for audit/compliance artifacts; cross-region replication.
- OpenSearch: snapshots to S3 (it's derived from Postgres → fast rebuild path also exists).
- Redis: AOF for durable workloads; cache is disposable.
- **Backups are tested:** automated monthly restore drills into an isolated env; restore success is a tracked metric. *An untested backup is not a backup.*

### DR
- **RPO ≤ 5 min** (WAL/PITR), **RTO ≤ 1 h** (Stage 2) → **RTO ≤ 15 min** (Stage 3, multi-region warm standby).
- Documented, rehearsed runbooks: region failover, primary promotion, point-in-time restore, partial corruption recovery, ransomware/crypto-shred recovery.
- DR game-days quarterly; failover automation tested, not assumed.

## 5. Release engineering & quality gates
- Trunk-based + feature flags; CI gates: lint → unit → integration → contract → **isolation tests** → **AI evals/calibration** → security scans → build → deploy staging → E2E → canary prod → progressive rollout with auto-rollback on SLO breach.
- DB migrations: expand→migrate→contract, backward-compatible, never block.
- **Definition of done** includes: tests, a11y check, telemetry/SLO instrumentation, runbook update, security review for sensitive paths.

## 6. Reaching 99.99% — the honest path
99.99% is earned in stages, not at launch:
- MVP: target 99.9% (single region, multi-AZ), instrument everything, build the muscle.
- Stage 2: 99.95% (HA all tiers, error budgets enforced, chaos game-days).
- Stage 3+: 99.99% (multi-region active-active, automated failover, mature SRE/on-call, DR rehearsed).
Promising 99.99% on day one would be dishonest; the architecture *supports* it and the program *converges* to it.
