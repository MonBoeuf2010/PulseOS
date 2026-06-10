# 13 — Hiring Roadmap

Principle: **stay small and senior until the wedge is proven.** PulseOS's hardest early problems (AI orchestration, calibration, tenancy isolation, time-to-value) are senior-generalist problems, not headcount problems. Over-hiring before product-market fit is a top startup killer (see `14` R-9).

## Org philosophy
- Founders + a tiny team of senior, full-stack-minded builders through MVP.
- **Hire for the gate you're trying to pass, not the vision.** No community/enterprise specialists before there are communities/enterprises.
- Security and AI-eval discipline are owned from day one (by founders/early hires), even before dedicated roles exist.

---

## Founding team (ideal coverage, may be 2–4 people)
The brief's "founding team" wears many hats. Realistically these competencies must be covered, by as few people as possible:
- **CEO / product & GTM** — owns wedge, users, narrative, fundraising.
- **CTO / architecture** — owns infra, tenancy/security posture, build-vs-buy.
- **Principal AI engineer** — owns Council, evals, calibration, the AI moat.
- (Often one person covers two of these early.)

## First ~10 hires (Phase 0–1, MVP)
Order is priority, not necessarily simultaneous:

1. **Founding full-stack engineer** (Next.js + FastAPI) — ship the briefing end-to-end.
2. **AI/ML engineer** — Council orchestration, eval harness, calibration, RAG/memory. (Core moat.)
3. **Full-stack / frontend-leaning engineer** — design system, performance, accessibility, the UX that delivers <60s time-to-value.
4. **Backend / data engineer** — ingestion connectors, pipelines, dedupe/enrich, OpenSearch/pgvector.
5. **Product designer** (premium, dense-but-clear UX — Apple/Linear/Bloomberg sensibility). Possibly contract→FT.
6. **Platform / DevOps-SRE engineer** — Terraform, CI/CD, observability, cost discipline, on-call foundation.
7. **Security engineer (or strong security-minded eng + fractional CISO/advisor)** — tenancy isolation, threat modeling, compliance groundwork. **Do not skip security ownership.**
8. **Founding product manager / PMM** (or founder-led until ~here) — metrics, experiments, wedge validation, pricing tests.
9. **Data scientist / eval specialist** — calibration, outcome data, eval rigor (the trust moat). Could be merged with #2 early.
10. **Generalist / customer + community lead** — early user love, support, community seeding for R2.

## Phase 2–3 (Network/Communities, Months 5–15)
Add as gates pass:
- 2–4 more **full-stack engineers** (community, search, reputation, moderation).
- **Trust & Safety lead** + ML for verification/moderation (misinfo is existential — `14` R-2).
- **Community/growth** roles to seed and nurture (avoid graveyards).
- **Designer #2**, **PM #2** (network + monetization surfaces).
- **SRE #2** as scale hits Stage 2→3.

## Phase 4 (Enterprise, Months 15–24)
- **Enterprise account executives + sales engineer** (security-literate; they sell *trust*).
- **Compliance/GRC lead** (SOC2/ISO program), **dedicated CISO** by ~Series A/enterprise entry.
- **Customer success** (enterprise onboarding, retention/NRR).
- **Backend/security engineers** for private deployment, SSO/SCIM, data residency.
- **Finance/ops** as headcount + contracts grow.

## Roles to deliberately delay
- Heavy sales team — before enterprise readiness + SOC2 (you'll burn cash selling what you can't deliver/secure).
- Specialized vertical experts beyond the founding vertical — before multi-domain proven.
- Large eng team — before the wedge gate; throughput ≠ progress pre-PMF.
- Mobile-native team — PWA first (`05`).

## Comp & culture
- Senior, high-ownership, generalist early hires; competitive cash + meaningful equity (small team, big slices).
- Bias to people who've shipped AI products *with eval/trust discipline*, not just demos.
- Remote-friendly but with strong async writing culture (this doc set is the artifact of that culture).
- **Security/ethics literacy is a hiring criterion**, not a nice-to-have, given the data we touch.

## Headcount sketch `[modeled]`
| Stage | ~Team size | Focus |
|---|---|---|
| Pre-seed/MVP | 4–8 | Prove the wedge |
| Seed / R2 | 10–18 | Network + scale foundations |
| A / R3 | 20–40 | Communities, moderation, multi-domain, scale |
| A→B / R4 | 40–80 | Enterprise, compliance, GTM engine |

## The honest hiring caveat
The temptation will be to hire ahead of the vision (a community team, an enterprise team, a sales team) before the wedge retains. **Resist it.** Every doc in this set points to the same discipline: prove single-player retention + trust first, then add people to amplify a working loop — never to manufacture one.
