# PulseOS — The Real-Time Intelligence Operating System

> Continuously converts global, corporate, community, personal, and economic signals into the **highest-value action you should take right now** — with calibrated confidence, linked evidence, and the dissenting view.

This repository contains the PulseOS architecture documentation and a production-architected reference implementation (backend + frontend scaffold).

## Repository layout
```
docs/
  phase-1/   Strategy & architecture (PRD, personas, journeys, AI strategy, security, risk...)
  phase-2/   Data & API (Postgres schema, ERD, indexing/partitioning, events, OpenAPI, redis/queue/search/AI pipeline)
  phase-3/   Complete security architecture (CISO/SOC2/GDPR)
  phase-4/   Design system + wireframes for every screen
  phase-9/   Testing & reliability (QA + SRE, 99.99% path)
  phase-10/  Launch, growth & enterprise readiness (GTM)
backend/     FastAPI + SQLAlchemy + Celery + Redis + OpenSearch + pgvector (Phases 5,6,8)
frontend/    Next.js + React + TS + Tailwind + shadcn + Framer Motion (Phase 7)
infra/       docker-compose for local dev, env templates
```

## What is implemented
This is a **reference scaffold**, not a finished product. It demonstrates the architecture end-to-end: project structure, domain models, services, API routes, the Strategic Council Engine (orchestrator + 7 agents + prompts + confidence/verification), the ingestion pipeline, and a frontend app shell with the Intelligence Dashboard. It is designed for a senior team to extend along the Phase 12 roadmap. Files note `# SCAFFOLD` where logic is intentionally stubbed for extension.

## Quick start (local dev)
```bash
cp infra/.env.example infra/.env       # fill in secrets / model API keys
docker compose -f infra/docker-compose.yml up --build
# backend → http://localhost:8000  (OpenAPI docs at /docs)
# frontend → http://localhost:3000
```

## Read the docs first
Start with `docs/phase-1/00-README.md`. The single most important idea: **win the wedge first** (the daily briefing for one persona in one vertical), then earn each additional ecosystem behind a hard gate.

## License
Proprietary — © PulseOS.
