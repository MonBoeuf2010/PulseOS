# 09 — Infrastructure Plan

Aligns with the mandated stack (Next.js/React/TS/Tailwind/Framer/Zustand/TanStack/shadcn; FastAPI/Python async; Postgres; Redis; Celery/RabbitMQ; OpenSearch; pgvector; AWS; Docker/K8s/Terraform; Prometheus/Grafana/Sentry; GitHub Actions). The plan below adds the *judgment* the stack list doesn't: what to build now vs. later, and where the mandated stack is over-engineered for MVP.

## Guiding principle: don't build for 10M users while serving 0

The scalability targets (10k → 10M) are real, but **premature distributed-systems complexity is the #1 way early teams die.** The architecture must be *horizontally-scalable in design* but *operationally simple at MVP*. We adopt a **modular monolith → services** path, not microservices on day one.

---

## 1. Logical architecture

```
                     ┌─────────────────────────────────────────┐
   Clients (web/PWA) │  Next.js (SSR/ISR) + React + shadcn      │
                     └───────────────┬─────────────────────────┘
                                     │ HTTPS / TLS 1.3
                             ┌───────▼────────┐
                             │  API Gateway / │  WAF, rate limit,
                             │  Edge (CDN)    │  DDoS, auth check
                             └───────┬────────┘
                                     │
              ┌──────────────────────┼───────────────────────┐
              │            FastAPI (async) app                 │
              │  Modular monolith: auth, briefing, opportunity,│
              │  council-orchestrator, memory, community,      │
              │  billing, admin (clear module boundaries)      │
              └───┬───────┬──────────┬──────────┬─────────────┘
                  │       │          │          │
         ┌────────▼─┐ ┌───▼────┐ ┌───▼─────┐ ┌──▼──────────┐
         │ Postgres │ │ Redis  │ │OpenSearch│ │ Celery/queue│
         │ +pgvector│ │ cache/ │ │  search  │ │  workers    │
         │ (RLS)    │ │ sessions│ │          │ │             │
         └──────────┘ └────────┘ └──────────┘ └──┬──────────┘
                                                  │
                                   ┌──────────────▼───────────────┐
                                   │  AI Gateway (model-agnostic) │
                                   │  routing, caching, eval hooks│
                                   │  → Claude / other providers  │
                                   └──────────────────────────────┘
   Ingestion: scheduled + streaming connectors (news/markets/civic/web/personal)
   → normalize → dedupe → enrich → index (OpenSearch) + embed (pgvector) → trigger pipelines
```

## 2. Component decisions (with honest "now vs. later")

| Concern | MVP choice | Scale choice | Note |
|---|---|---|---|
| Backend shape | **Modular monolith** (FastAPI) | Extract hot modules to services | Don't do microservices at 0 users |
| DB | **Single Postgres** + pgvector + **Row-Level Security** for tenancy | Read replicas → partitioning → Citus/Aurora; separate analytical store | RLS = defense-in-depth for isolation |
| Vector | **pgvector** (co-located) | Dedicated vector store *only if* pgvector limits hit | Avoid premature extra system |
| Cache/session | Redis | Redis cluster | |
| Queue | **Celery + Redis broker** at MVP; RabbitMQ when fan-out/routing needs it | RabbitMQ / SQS, autoscaled workers | RabbitMQ is overkill for MVP; brief allows both — start simple |
| Search | OpenSearch (managed) | Sharded clusters | <100ms is a *scale* target; MVP can be narrower |
| Frontend | Next.js on Vercel **or** ECS; PWA (no native apps yet) | Same + edge | Responsive/PWA before native (see `05`) |
| Cloud | AWS (EKS or ECS+Fargate) | EKS multi-AZ, autoscaling | **ECS/Fargate at MVP**; EKS when team + scale justify K8s ops cost |
| IaC | Terraform from day 1 | Same, modularized | Reproducibility early is cheap insurance |
| CI/CD | GitHub Actions | + progressive delivery (canary) | Eval-regression gates in CI (see `07`) |
| Observability | Prometheus + Grafana + Sentry; structured logs | + distributed tracing, SLO dashboards | Trace the AI pipeline end-to-end early |

> **Deliberate deviation flagged:** the brief lists Kubernetes + RabbitMQ + dedicated everything. For MVP we recommend **ECS/Fargate + Celery/Redis** and migrate to **EKS + RabbitMQ** at the R2/R3 scale gate. The brief's target architecture is the *destination*, not the starting line. This is documented so it's a conscious decision, not drift.

## 3. Data ingestion & real-time

- **Connectors** (pluggable): news/RSS, market data, weather/civic/economic APIs, web crawl (allow-listed + rate-limited), and *personal* read-only connectors (calendar, location-region, financial via aggregator — consent-gated).
- **Pipeline:** ingest → normalize → dedupe → enrich (entities, geo, domain tags) → index + embed → trigger fast-path / council gating.
- **Real-time:** event-driven via queue; freshness SLO ≤15 min (NFR-1). Streaming (Kafka/Kinesis) is an **R2+** upgrade, not MVP.
- **Shared public-signal compute** (the cost lever from `08`): public analyses computed once, cached, reused; personalization layered per-user.

## 4. Scaling path (mapped to the 10k→10M targets)

| Stage | Users | Key moves |
|---|---|---|
| Launch | 10k | Modular monolith, single Postgres+RLS, ECS, managed Redis/OpenSearch. Optimize time-to-value, not throughput. |
| Stage 2 | 100k | Read replicas, worker autoscaling, CDN/edge caching, queue → RabbitMQ if needed, extract council-orchestrator if it's the hot path. |
| Stage 3 | 1M | DB partitioning/sharding by tenant, EKS, dedicated search clusters, streaming ingestion, multi-AZ, aggressive shared-compute caching. |
| Stage 4 | 10M | Cell-based architecture, regional deployments (data residency), per-segment model routing, full SRE/on-call, cost-optimization as a discipline. |

**Horizontal scalability is preserved from day 1** via: stateless app tier, tenant-keyed data access, queue-based async work, and cacheable shared compute. We don't *implement* sharding early — we *don't preclude* it.

## 5. Cost envelope (the discipline)
- Largest variable cost = **AI inference** (see `07`/`08`). Infra cost (compute/db/search) is secondary until ~Stage 2.
- Track **cost per MAU** and **cost per briefing/council report** as first-class metrics in Grafana from day 1.
- Use spot/Fargate-spot for batch/worker; reserved/savings plans once baseline load is known.

## 6. Reliability & DR
- Multi-AZ from Stage 2; backups + PITR for Postgres from MVP; tested restore runbook.
- SLOs: 99.9% MVP → 99.95% scale; error budgets govern release pace.
- Graceful degradation: if the Council/AI gateway is down, serve last-good briefing + cached intelligence rather than failing the app (the app must be useful even when AI is degraded).

## 7. Environments & delivery
- envs: local (docker-compose) → staging → prod, all Terraform-managed.
- Trunk-based + feature flags; canary at scale; eval + security gates in CI.
- Secrets in AWS Secrets Manager with rotation (see `10`).
