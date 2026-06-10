# 03 — User Personas

Personas are written as **jobs-to-be-done + willingness-to-pay**, not demographics. Each lists the *trigger* (when they need us), the *current alternative* (who we displace), and *what would make them churn*.

We tag each persona by phase: **[Wedge]** (MVP target), **[R2–R3]** (network era), **[R4]** (enterprise).

---

## P1 — "Maya," the Operator/Builder **[Wedge — primary]**

- **Who:** 28–45, founder/operator/senior IC, manages money and career actively, juggles many fast-moving inputs (industry news, markets, local cost-of-living, personal finance, calendar).
- **Master JTBD:** "Tell me the few things that actually move my outcomes today so I can act before the window closes."
- **Trigger:** Morning catch-up; a market/industry shock; a recurring "am I missing something?" anxiety.
- **Current alternatives:** A chaotic mix of newsletters, X/Twitter, a budgeting app, a brokerage app, ChatGPT, and gut feel. None of it is synthesized or ranked by *her* goals.
- **Value she'll pay for:** Time saved + missed-opportunity insurance. A single avoided mistake or captured opportunity pays for years of Pro.
- **What makes her churn:** Empty/obvious briefings; a confidently wrong recommendation; fake-precise numbers; >60s to first value.
- **Willingness to pay:** High for Pro ($10–30/mo). She already pays for 3+ tools we can subsume.

## P2 — "Devin," the Information-Overloaded Professional **[Wedge — secondary]**

- **Who:** 30–55, analyst/consultant/PM/exec-adjacent; paid to be "the person who knows things."
- **JTBD:** "Make sure I never get blindsided in my domain, and give me the synthesized take with sources I can forward."
- **Trigger:** Before meetings; when a topic blows up; weekly prep.
- **Displaces:** Manual reading, paid research newsletters, junior-analyst legwork.
- **Pays for:** The Council's *evidence + dissent* (forwardable, defensible). Confidence + sources are the feature.
- **Churn risk:** Shallow analysis that an expert sees through; no source depth.
- **WTP:** Pro, and a strong Business/Team upsell candidate.

## P3 — "The Community Contributor / Local Expert" **[R2–R3]**

- **Who:** Engaged locals, domain hobbyists, semi-pros who *know things first* (traffic, local economy, a niche market, a team).
- **JTBD:** "Get recognized for being right, and reach people who value it."
- **Trigger:** They witness/know something before the mainstream.
- **Displaces:** Reddit, Nextdoor, local FB groups, niche Discords — none of which reward *accuracy* or build portable reputation.
- **Pays for:** Mostly *status*, not money (reputation, reach). They are **supply**, not primarily revenue. Critical for network value.
- **Churn risk:** Effort with no reach/recognition; moderation that feels unfair; brigading.
- **Design implication:** Reputation system + fair, explainable moderation + appeals are *retention* features for this persona, not nice-to-haves.

## P4 — "The Verified Company / Comms Lead" **[R4]**

- **Who:** Corporate comms, IR, founder-CEO, sports org, university, government office.
- **JTBD:** "Broadcast authoritative updates to the people who follow us, and turn our meetings into searchable institutional memory."
- **Trigger:** Announcements, earnings, board meetings, crises.
- **Displaces:** Email blasts, press releases, scattered Slack/Notion, manual meeting notes.
- **Pays for:** Reach to an engaged, intent-rich audience + Meeting Intelligence (transcription, decisions, action items, searchable forever).
- **Churn risk:** Low audience; meeting AI inaccuracy on names/decisions; **security/compliance failure** (this persona's bar is highest).
- **WTP:** Business/Enterprise ($$$). This is the margin engine.

## P5 — "The Enterprise Buyer / CISO + Economic Buyer" **[R4]**

- **Who:** VP/C-level + security. Buys for a team/org; signs the contract; owns the risk.
- **JTBD (economic buyer):** "Give my org a decisive information advantage and quantifiable ROI."
- **JTBD (CISO):** "Prove you won't leak our data, cross tenants, or fail an audit."
- **Displaces:** Bloomberg/FactSet-tier spend (in spirit), internal BI, consultant retainers, scattered tooling.
- **Pays for:** Private deployment, custom councils, compliance suite (SOC2/ISO), SSO/SCIM, audit logs, data residency.
- **Churn / no-buy risk:** Any tenancy-isolation doubt; no SOC2; unclear data handling. **Security is the deal, not a checkbox** (see `10`).
- **WTP:** Enterprise ($$$$, annual contracts).

---

## Persona → product mapping

| Persona | Primary surface | Primary value | Phase | Revenue role |
|---|---|---|---|---|
| P1 Operator | Daily Briefing + Opportunity Engine | Ranked actions, EV, savings | MVP | Pro revenue |
| P2 Professional | Council reports + Search | Evidence + dissent, no blindsides | MVP/R2 | Pro / Team |
| P3 Contributor | Community Network + Reputation | Recognition + reach | R2–R3 | Supply (low direct rev) |
| P4 Company | Live Rooms + Meeting Intelligence | Authoritative reach + memory | R4 | Business |
| P5 Enterprise | Compliance + private deploy | Advantage + provable safety | R4 | Enterprise (margin) |

## Anti-persona (who we are NOT for, yet)
- **The doomscroller** who wants an engaging feed. We optimize *actions*, not attention; we will feel "too quiet" to them. That's correct.
- **The casual news reader** with no goals to act on. Without goals, the Opportunity/Action engine has nothing to rank. Onboarding must establish goals or the product is empty.
- **Regulated-advice seekers** ("just tell me what stock to buy"). We will frustrate them on purpose (liability bright line).

## The cold-start truth
P1/P2 are **single-player** (valuable with zero other users) — that's why they're the wedge. P3/P4/P5 are **multiplayer** (value depends on a populated network). Sequencing single-player → multiplayer is the entire reason the roadmap looks the way it does.
