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
A **working end-to-end vertical slice**, not just a scaffold:

- **Auth** — register / password login / rotating-refresh sessions (Argon2id + JWT), RBAC/ABAC.
- **Strategic Council Engine** — orchestrator, 7 agent prompts, confidence calibration, contradiction-aware synthesis with preserved dissent. Runs fully offline against a deterministic structured stub when no `ANTHROPIC_API_KEY` is set; swaps to the real Anthropic SDK when one is.
- **Briefing pipeline** — gather signals → gate the council → calibrated, precision-first ranking (EV × confidence) → persisted briefing. Cold-start seeds a useful first briefing.
- **Repositories + DB** — async SQLAlchemy over Postgres + pgvector, tenant-scoped queries, the full schema (tenants, users, memberships, sessions, briefings, items, memory, signals, council reports, opportunities, usage events, feedback).
- **AI Analyst chat** — a conversational analyst grounded in the user's own memory + latest briefing; multi-turn conversations persisted. Uses the AI Gateway (live Anthropic with a key, coherent offline stub without).
- **Community feed** — users publish intelligence "calls"; cross-user community visibility with toggleable reactions.
- **API** — dashboard, briefings (+ feedback), opportunities (+ act), memory (add/list/delete), council analyze/report, chat (+ conversations), community feed (+ react), universal search (Postgres lexical fallback).
- **North-Star wired** — `acted_on` feedback / opportunity acts emit the WARU usage event and flow into the dashboard's realized-value analytics.
- **Frontend** — Next.js 14 (App Router) + TypeScript + Tailwind, styled to a Webflow-inspired design system (`DESIGN.md`): marketing landing + pricing, login, the flagship Intelligence Dashboard, AI Analyst chat, community feed, opportunities, memory, and search with an "Ask the Council" panel.

Still stubbed for extension (marked `# SCAFFOLD`): OpenSearch hybrid/vector search + reranking, real ingestion connectors + embeddings, WebAuthn passkeys, Stripe billing, offline calibration fitting, and Alembic migrations (dev uses `create_all`). `DESIGN.md` (Webflow-inspired tokens) is the UI reference followed by the frontend.

## Quick start — full stack (Docker)
```bash
cp infra/.env.example infra/.env       # fill in secrets / model API keys (optional in dev)
docker compose -f infra/docker-compose.yml up --build
# backend → http://localhost:8000  (OpenAPI docs at /docs)
# frontend → http://localhost:3000
```

## Quick start — without Docker
```bash
# 1. Postgres 16 with the pgvector extension, then:
createdb pulseos && psql -d pulseos -c 'CREATE EXTENSION IF NOT EXISTS vector;'

# 2. Backend
cd backend && python -m venv .venv && . .venv/bin/activate
pip install -e .
export DATABASE_URL="postgresql+asyncpg://<user>@localhost:5432/pulseos"
export ENV=development SECRET_KEY="<32+ byte secret>"
python -m scripts.seed                 # creates demo data + a first briefing
uvicorn app.main:app --reload          # → http://localhost:8000/docs

# 3. Frontend (new shell)
cd frontend && npm install
NEXT_PUBLIC_API_BASE=http://localhost:8000 npm run dev   # → http://localhost:3000

# Demo login:  demo@pulseos.com  /  pulsedemo123
```

Tests: `cd backend && pytest` (no DB or API key required — runs against the deterministic council stub).

## Read the docs first
Start with `docs/phase-1/00-README.md`. The single most important idea: **win the wedge first** (the daily briefing for one persona in one vertical), then earn each additional ecosystem behind a hard gate.

## License
Proprietary — © PulseOS.
