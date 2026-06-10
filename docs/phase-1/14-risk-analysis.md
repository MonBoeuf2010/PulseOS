# 14 — Risk Analysis

Risks are rated **Likelihood × Impact** (L/M/H) and ordered by severity. Each has an *owner discipline*, a *mitigation*, and a *kill/early-warning signal*. This is the document an investor or board should read first.

---

## Existential / top risks

### R-1 — Scope sprawl: five products, none great. **L:H · I:H**
- **Why:** The brief is five ecosystems. Building them in parallel guarantees mediocrity and burn.
- **Mitigation:** The Wedge (`02`) + hard gates (`12`). Single-player → multiplayer sequencing. Ruthless "Won't-yet" list (`05`).
- **Early warning:** Roadmap pressure to start R2+ before the MVP gate passes. **Kill signal:** if leadership can't name the one wedge, stop and re-decide.

### R-2 — Misinformation amplification destroys trust. **L:M · I:H**
- **Why:** A community intelligence network that shows confident falsehoods as "High verification" is worse than useless and legally hazardous.
- **Mitigation:** Verification + reputation + AI moderation + human appeal are **core, not bolt-on**; humility-biased confidence; fast dispute surfacing; red-team for manipulation/brigading; Trust & Safety lead at R2.
- **Warning:** rising verified-but-wrong reports; brigading patterns; complaints. **Kill signal:** can't keep false-"High-confidence" rate below bar → delay the network ecosystem.

### R-3 — A wrong high-confidence recommendation breaks trust (and maybe the law). **L:M · I:H**
- **Why:** "Fill your tank, save $12" is benign; "do X with your money/health" is not. One confident, harmful, wrong call can end the brand.
- **Mitigation:** Calibration as a gated KPI (H3); precision-first ranking; **regulated-advice bright line** (no securities/medical/legal directives); conservative/ranged estimates + visible methodology; cost-of-inaction framed honestly.
- **Warning:** rising false-action rate on high-confidence items. **Kill signal:** calibration won't converge → don't surface confidence numbers; reframe as decision-support, not directives.

### R-4 — Platform/model-provider disintermediation. **L:M · I:H**
- **Why:** OpenAI/Anthropic/Google could ship "proactive personalized briefings + memory" as a default feature.
- **Mitigation:** Moat = proprietary outcome/calibration data + network + vertical depth + trust brand + enterprise compliance (`06`). Never compete on "we have good models."
- **Warning:** a major assistant ships our core loop. **Response:** lean into data/network/enterprise differentiation they won't replicate.

### R-5 — Tenancy isolation / security breach. **L:L · I:H (catastrophic)**
- **Why:** Cross-tenant leak or meeting breach is company-ending, especially for enterprise.
- **Mitigation:** RLS + app + vector isolation, defense-in-depth, automated adversarial isolation tests in CI, zero-trust, pen tests, encryption, audit (`10`). Delay deep financial-data ingestion until security maturity.
- **Warning:** any isolation-test failure; anomalous cross-tenant access. **This risk is low-likelihood by design and must stay that way — it is non-negotiable.**

---

## Major risks

### R-6 — The "empty briefing" / habit failure. **L:M · I:H**
- Most days, nothing critical changes → briefing feels thin → churn (PRD A3).
- **Mitigation:** blend event-driven alerts with evergreen optimizations; tune frequency; quality-gated notifications; honest "quiet day" states. **Warning:** D7/D30 retention below H2.

### R-7 — AI cost re-inflation / COGS blows the model. **L:M · I:H**
- If frontier reasoning prices rise or per-user compute can't be shared, the consumer tier is unprofitable (`08`).
- **Mitigation:** model-agnostic routing, Council gating, shared public-signal compute, caching, fair-use caps; instrument cost-per-MAU from day 1. **Fallback:** pivot upmarket (prosumer/enterprise-first). **Warning:** cost-per-MAU trending above conversion value.

### R-8 — No product-market fit in the wedge. **L:M · I:H**
- Users read but don't *act*; WARU (North Star) stays flat (PRD A1).
- **Mitigation:** validate H1–H4 before scaling; tight feedback loops; be willing to re-pick the wedge/persona/vertical. **Kill signal:** repeated wedge iterations fail → fundamental thesis (people will act on AI recs) is wrong → reframe toward expert decision-support.

### R-9 — Over-hiring / over-building before PMF. **L:M · I:H**
- **Mitigation:** stay small/senior to the gate (`13`); fund to milestones; resist building network/enterprise before the wedge retains.

### R-10 — Calibration is genuinely hard (the sleeper risk). **L:M · I:M-H**
- Confidence may not calibrate in noisy real-world domains; outcomes may be unobservable → the moat (`07`) doesn't compound.
- **Mitigation:** start in domains with observable outcomes; humble confidence; treat calibration as a research track with explicit success bars. **Warning:** persistent high calibration error.

### R-11 — Prompt injection / AI abuse via ingested content. **L:M · I:M-H**
- We feed untrusted web/community content to agents.
- **Mitigation:** instruction/data separation, untrusted-content handling, tool allow-listing, no autonomous high-impact actions, red-team suite in CI + prod monitoring (`07`/`10`).

---

## Moderate risks

### R-12 — Regulatory/liability (financial/medical/legal advice, GDPR/CCPA). **L:M · I:M-H**
- **Mitigation:** bright line on regulated advice; privacy-by-design; inspect/edit/delete; DPAs; legal review before entering regulated verticals; SOC2/ISO when enterprise.

### R-13 — Cold-start in network/community features. **L:H · I:M**
- Communities/marketplaces are graveyards without seeded supply.
- **Mitigation:** single-player value first; seed founding vertical/geo; reputation as the hook; don't launch communities broadly until one thrives (`12`).

### R-14 — Notification fatigue / becoming noise. **L:M · I:M**
- One noisy push trains users to mute us.
- **Mitigation:** quality-gated notifications as an SLO; precision-first; user control over cadence.

### R-15 — Meeting Intelligence accuracy + liability. **L:M · I:M**
- Misattributed decisions in board/investor contexts are dangerous.
- **Mitigation:** human-in-the-loop confirmation for high-stakes extractions; clear "AI-generated, verify" framing; strict access control.

### R-16 — Data-source dependency / API cost & availability. **L:M · I:M**
- Reliance on third-party news/market/civic APIs (price hikes, ToS changes, rate limits).
- **Mitigation:** pluggable connectors, multi-source redundancy, caching, contracts; don't single-source critical signals.

### R-17 — Fundraising / runway. **L:M · I:M-H**
- AI infra + long enterprise cycles are capital-intensive.
- **Mitigation:** milestone-based funding tied to gates; keep burn low pre-PMF; the wedge produces a crisp, fundable story.

### R-18 — Talent concentration / key-person risk. **L:M · I:M**
- The AI/calibration moat may live in 1–2 heads.
- **Mitigation:** documentation culture (this set), eval/data as shared assets, redundancy in critical knowledge.

### R-19 — Accessibility/performance debt. **L:M · I:L-M**
- WCAG 2.2 AA + Lighthouse >95 are hard to retrofit.
- **Mitigation:** enforce in CI from day 1, not at the end.

---

## Risk dashboard (watch-list, top 6)
| Risk | Metric to watch | Threshold that triggers action |
|---|---|---|
| R-1 Sprawl | # ecosystems in active dev pre-gate | >1 |
| R-3 Wrong rec | false-action rate (high-conf items) | above SLO |
| R-7 COGS | cost per MAU vs. conversion value | cost > value |
| R-8 No PMF | WARU / D30 retention | below H2 |
| R-10 Calibration | calibration error (ECE/Brier) | above bar (H3) |
| R-5 Isolation | adversarial isolation test pass rate | <100% |

## Meta-risk: believing the vision is the plan
The biggest risk is treating the grand five-ecosystem vision as the *execution plan*. It is the *destination*. The plan is the wedge, the gates, and the discipline to not skip them. Every other risk gets worse if this one isn't held.
