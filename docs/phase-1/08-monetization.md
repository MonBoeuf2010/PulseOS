# 08 — Monetization

## Principle: we sell decisions and trust, not data

Revenue is **subscription + enterprise**, never data brokerage. This is a strategic constraint: the entire value prop is trust, and trust is incompatible with selling user data. (See `01` ethics.)

## Packaging (the brief's four tiers, made concrete)

| Tier | Price (hypothesis) | Who | Headline value | Gating |
|---|---|---|---|---|
| **Free** | $0 | P1/P2 top-of-funnel | Daily briefing (limited domains), communities, follows, limited Council/opportunities | Acquisition + supply |
| **Pro** | **$15–25/mo** `[modeled]` | P1 Operator, P2 Professional | Unlimited analyses, advanced Council reports, multi-domain opportunities, full memory, weekly reports, priority freshness | Core consumer revenue |
| **Business** | **$40–80/seat/mo** `[modeled]` | P4 small orgs, teams | Live rooms, Meeting Intelligence, team workspaces, shared intelligence, follower analytics | Team revenue |
| **Enterprise** | **Custom, annual ($25k–$250k+)** `[modeled]` | P5 | Private/segregated deployment, custom councils, compliance suite (SOC2/ISO), SSO/SCIM, audit, data residency, SLA | Margin engine |

> All prices are `[modeled]` hypotheses to be tested via pricing experiments and willingness-to-pay interviews. The *structure* (free wedge → prosumer Pro → team Business → enterprise margin) is the strategic bet; the numbers will move.

## Free → Pro conversion logic
- Free delivers a *real* daily habit (the wedge) but caps depth: fewer domains, capped Council deep-dives, delayed freshness, no multi-domain Opportunity Engine.
- The upgrade trigger is **value made visible**: the weekly "you saved ~$X / Yh, captured N opportunities" report + paywalled "see the full Council analysis / unlock this opportunity domain."
- Target free→Pro ≥5% within 60 days (PRD H4) `[aspirational]`.

## Unit economics model (illustrative, `[modeled]` — must be validated)

The whole model lives or dies on **AI COGS per MAU < revenue per MAU**.

- **Free MAU AI COGS target:** keep within a small monthly budget per free MAU via Council gating + shared public-signal compute + caching + model routing (see `07` §8). If a free MAU costs more than its expected conversion value × LTV, free tier is unsustainable → tighten gating. **This is the single most important number to instrument early.**
- **Pro:** at $15–25/mo, with disciplined AI COGS (cents–low-dollars/MAU/mo via gating + shared compute), gross margin target **70%+** `[modeled]`. Heavy users are the risk; usage-aware fair-use caps protect margin.
- **Enterprise:** software-like gross margin minus private-deployment + support cost; annual contracts + NRR are the value driver.

### LTV/CAC discipline
- Target **LTV:CAC ≥ 3:1** at steady state `[aspirational]`.
- CAC kept low early via the **shareable Council report** (organic/viral loop — Devin forwards cited summaries) and content/SEO, not paid acquisition. Paid spend only after the value loop is proven.

## Why the COGS structure can work (the key insight)
The expensive part (analyzing public signals) is **shared across all users** — computed once, personalized cheaply per user. Personal data synthesis is per-user but lighter. This means **AI cost scales sub-linearly with users** in the dominant (public-signal) component. That's the economic bet that makes a consumer AI-intelligence product viable. If it's false (i.e., everything must be per-user-expensive), the consumer tier is structurally unprofitable and we pivot upmarket (prosumer/enterprise-first). Tracked as R-7/R-8.

## Pricing risks
- **Free tier as a cost bomb:** AI COGS on free users could exceed acquisition value. Mitigation: hard gating, shared compute, generous-but-bounded free.
- **Value legibility:** if users don't *believe* the saved-$/time numbers, conversion stalls. Mitigation: conservative, ranged, methodology-visible claims.
- **Enterprise sales cycle:** 6–12 months, security-gated. Don't model enterprise revenue before R4 + SOC2.
- **Anchoring:** priced too low → can't fund AI COGS; too high → no habit/funnel. Test aggressively.

## Go-to-market (brief summary; expanded in roadmap)
1. **Wedge GTM:** founding vertical + persona (Operator), seeded by us with high-quality intelligence, organic + content-led. Prove retention before spend.
2. **Network GTM (R2–R3):** invite top contributors, seed communities in the founding vertical/geo; reputation as the hook.
3. **Enterprise GTM (R4):** land via Meeting Intelligence / Live Rooms wedge inside companies that already have Pro users (bottom-up → top-down), then expand to compliance suite.

## Revenue mix over time `[modeled]`
- Year 1: ~all Pro (small), funded by investment, focus on retention not revenue.
- Year 2: Pro scales + early Business.
- Year 3+: Enterprise becomes the margin and ACV driver; Pro is the funnel/brand.

## The honest monetization truth
Consumer AI subscriptions have **high churn and price sensitivity**. The durable money is almost certainly **enterprise** (Meeting Intelligence + compliance + private deployment). The consumer wedge's primary job may be **funnel, brand, and data**, not profit. We should be open to the possibility that LifeIQ is ultimately an enterprise intelligence company with a consumer top-of-funnel — and not over-invest in consumer monetization before that's clear.
