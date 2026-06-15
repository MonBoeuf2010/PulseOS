# LifeIQ — Phase 1 Founding Documentation

**The Real-Time Intelligence Operating System.**

> Status: Phase 1 — Strategy & Architecture (no code)
> Owner: Founding team
> Last updated: 2026-06-09

This directory is the canonical source of truth for *why* LifeIQ exists, *what* it is, *who* it serves, *how* it makes money, and *how* it is built and defended. It is written to guide a team for multiple years and to survive contact with investors, enterprise security reviews, and the first 10,000 → 10,000,000 users.

It is deliberately **opinionated and self-critical**. Where the original brief makes an optimistic assumption, these documents name it, stress-test it, and propose a falsifiable way to validate or kill it.

---

## The one-sentence thesis

People are drowning in information and starved for decisions. LifeIQ continuously converts the firehose of global, corporate, community, personal, and economic signals into a ranked list of **the highest-value actions a given user should take right now**, each with confidence, evidence, expected value, and the cost of ignoring it.

## The one honest risk

This is five products (dashboard, corporate live rooms, community network, AI communities, opportunity engine) wearing one trench coat. The single greatest threat to LifeIQ is **building all five at once and being mediocre at all of them.** Phase 1's most important output is therefore not the grand vision — it is the **wedge**: the one user, one job, one loop we win first. See `02-prd.md` §"The Wedge" and `11-development-roadmap.md`.

---

## Document index

| # | Document | What it answers |
|---|----------|-----------------|
| 00 | [README](00-README.md) | How to read this set; thesis; wedge |
| 01 | [Vision & Company](01-vision-and-company.md) | Mission, principles, what we are/aren't, naming, ethics |
| 02 | [Product Requirements Document](02-prd.md) | Problem, wedge, scope, requirements, success metrics, non-goals |
| 03 | [User Personas](03-personas.md) | Who we serve; jobs-to-be-done; willingness to pay |
| 04 | [User Journeys](04-user-journeys.md) | End-to-end flows for each persona + key loops |
| 05 | [Feature Map](05-feature-map.md) | Full feature inventory, MoSCoW, phasing, dependencies |
| 06 | [Competitive Analysis](06-competitive-analysis.md) | Who we displace, moats, why-now, honest threats |
| 07 | [AI Strategy](07-ai-strategy.md) | Strategic Council Engine, model strategy, evals, cost, safety |
| 08 | [Monetization](08-monetization.md) | Pricing, packaging, unit economics, GTM |
| 09 | [Infrastructure Plan](09-infrastructure-plan.md) | Cloud, services, scaling, data flow, cost envelope |
| 10 | [Security & Compliance Plan](10-security-plan.md) | Zero-trust, tenancy isolation, RBAC, compliance roadmap |
| 11 | [Database Overview](11-database-overview.md) | Domain model, storage choices, multi-tenancy, retention |
| 12 | [Development Roadmap](12-development-roadmap.md) | 0→24 month plan, milestones, gates, build-vs-buy |
| 13 | [Hiring Roadmap](13-hiring-roadmap.md) | Org by stage, first 10 hires, comp philosophy |
| 14 | [Risk Analysis](14-risk-analysis.md) | Product, technical, legal, market, financial, existential risks |
| 15 | [Glossary & Open Questions](15-glossary-and-open-questions.md) | Shared vocabulary; unresolved decisions |

## How to read this

- **Investors:** 01 → 02 (thesis + wedge) → 06 → 08 → 14.
- **Engineers:** 02 → 05 → 07 → 09 → 10 → 11 → 12.
- **Enterprise security reviewers:** 10 → 11 → 09 → 14.
- **New team members:** 00 → 01 → 02 → 15, then your discipline's doc.

## A note on intellectual honesty

Every section that asserts a number (savings, latency, conversion, cost) tags it as one of:
- **[measured]** — from a real system or experiment.
- **[modeled]** — from an explicit, documented assumption (assumptions live in the doc).
- **[aspirational]** — a target we have not yet earned the right to claim.

In Phase 1, almost everything is `[modeled]` or `[aspirational]`. That is correct and expected. The job of Phase 2+ is to convert these into `[measured]`.
