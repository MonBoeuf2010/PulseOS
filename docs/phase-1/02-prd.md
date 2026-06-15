# 02 — Product Requirements Document (PRD)

## 1. Problem statement

Decision-makers cannot keep up with the volume of signal relevant to their goals, and the tools they have optimize for *consumption* (more articles, more feeds, more chat) rather than *action*. The result is anxiety, missed opportunities, and decisions made on stale or unverified information.

**Job to be done (master JTBD):**
> "When my world is changing faster than I can track, help me know the single most valuable thing to do next, why, and what it costs me to ignore it — without making me read everything or trust a black box."

## 2. The Wedge (the most important section in this document)

The full LifeIQ vision is five ecosystems. **We will not build five products at once.** We pick one wedge: the narrowest thing that delivers the master JTBD to one persona, end-to-end, and creates a daily habit.

### Wedge decision: **The Daily Intelligence Briefing for the "Operator/Builder" persona, in a single vertical we seed ourselves.**

- **Surface:** Page 1 (Intelligence Dashboard) → Daily Briefing, plus the Opportunity Engine *scoped to one domain* (we propose **personal finance + local cost-of-living + career/industry signals** for the founding vertical, because the value is legible, the "savings" are quantifiable, and liability is manageable).
- **Why this wedge:**
  - It delivers the *aha* in <60 seconds on day one (a concrete, quantified action: "do X, save $Y / gain $Z, here's why, 84% confidence").
  - It is a **daily habit** (morning briefing) → retention engine.
  - It is **single-player** — it works with zero other users, so we escape the cold-start problem that kills community-first products.
  - It is the natural top-of-funnel for *every* other ecosystem later.
- **What we explicitly defer:** Corporate Live Rooms, Meeting Intelligence, the full Community Network, AI Communities, multi-domain Opportunity Engine. These are Phase 2–4 (see `12-development-roadmap.md`). They are real and valuable — they are just not the fire we light first.

**The network (community, corporate, reputation) is the moat we build *after* we have retained single-player users.** Communities seeded into a product nobody opens daily are graveyards.

### Falsifiable wedge hypotheses (we kill the wedge if these fail)
- **H1 (value):** ≥40% of activated users mark ≥1 briefing action "useful" in week 1. `[aspirational]`
- **H2 (habit):** ≥25% D30 retention on the briefing for the founding vertical. `[aspirational]`
- **H3 (trust):** Council confidence scores are calibrated within ±10% (predicted vs. realized) on a labeled eval set before we surface them to users. `[aspirational]`
- **H4 (willingness to pay):** ≥5% of activated free users convert to Pro within 60 days. `[aspirational]`

## 3. Scope by release (summary; full detail in `05` and `12`)

| Release | Codename | Scope | Goal |
|---|---|---|---|
| MVP | "Briefing" | Auth, onboarding, personal-data connectors (read-only), Daily Briefing, single-domain Opportunity Engine, Council v1, AI memory (inspect/edit/delete), basic analytics | Prove H1–H4 with 1k–10k users |
| R2 | "Network" | Community Intelligence (reports + verification + reputation), Universal search, Follow system | Add network effects + UGC supply |
| R3 | "Communities" | AI Communities + AI Moderator, richer Opportunity Engine (multi-domain) | Engagement + retention depth |
| R4 | "Enterprise" | Corporate Live Rooms, Meeting Intelligence, custom councils, compliance suite, private deployment | Monetize org segment |

## 4. Functional requirements (MVP)

### 4.1 Onboarding & identity
- FR-1 Email + OAuth (Google/Apple) sign-up; MFA available (TOTP day 1, hardware key/WebAuthn fast-follow).
- FR-2 Goal/interest capture in onboarding (profession, goals, geography, domains, time/money sensitivity) → seeds AI memory.
- FR-3 Consent-gated personal data connectors (start **read-only**: calendar, location-region, optionally bank-via-aggregator in a later MVP iteration behind explicit consent + audit).

### 4.2 Daily Intelligence Briefing (Page 1)
- FR-4 A briefing is generated on a schedule (default daily AM, user-configurable) and on significant events.
- FR-5 Sections: **Immediate Actions, Opportunities, Risks, Time Savings, Money Savings, Upcoming Events, Forecasts.**
- FR-6 Every item carries: action, rationale, **confidence score (calibrated)**, supporting evidence (linked sources), estimated impact (time/$/risk), and **cost-of-inaction**.
- FR-7 Every item is feedback-able (useful / not useful / wrong / acted-on). Feedback trains ranking + memory.
- FR-8 Items are deduplicated and ranked by **expected value × confidence × personal relevance**, with a precision-first threshold (don't show low-confidence noise).

### 4.3 Opportunity Engine (single domain at MVP)
- FR-9 Continuously scans the user's connected + public signals for the founding vertical.
- FR-10 Each opportunity outputs: Opportunity Score, Expected Value, Confidence, Risk Assessment, Recommended Action.
- FR-11 **Regulated-advice guardrail:** opportunities classified as regulated (securities, medical, legal) are either (a) suppressed, or (b) shown as *information with explicit "not advice" framing*, per policy in `10` and `14`. No "buy this security" calls at MVP.

### 4.4 Strategic Council Engine (AI orchestration)
- FR-12 Significant reports pass through the multi-agent pipeline: independent analysis → debate → contradiction detection → consensus → confidence scoring → executive summary.
- FR-13 Output is auditable: which agent said what, where they disagreed, what evidence each cited.
- FR-14 Cost and latency budgets enforced (see §6); the Council is invoked *selectively*, not on every micro-signal (see `07`).

### 4.5 AI Memory
- FR-15 Long-term memory of interests/goals/profession/preferences.
- FR-16 User can **inspect, edit, delete** any memory item (GDPR/CCPA-aligned, see `10`).
- FR-17 Memory changes take effect on the next briefing and are logged in the audit trail.

### 4.6 Analytics
- FR-18 Track per-user: time saved `[modeled]`, money saved `[modeled]`, opportunities surfaced/acted-on, actions completed, briefings read.
- FR-19 Weekly personal intelligence report summarizing value delivered (retention + upgrade driver).

## 5. Non-functional requirements

| ID | Requirement | Target |
|---|---|---|
| NFR-1 | Briefing freshness | Significant events reflected within **≤15 min** of ingestion `[aspirational]` |
| NFR-2 | Search latency | p95 **<100ms** (per brief); MVP acceptable **<300ms** `[aspirational]` |
| NFR-3 | API latency (interactive) | p95 **<250ms** for non-AI endpoints `[aspirational]` |
| NFR-4 | Council report generation | p95 **<60s** async; user is never blocked on it `[modeled]` |
| NFR-5 | Availability | 99.9% MVP → 99.95% at scale `[aspirational]` |
| NFR-6 | Frontend | Lighthouse >95, FCP <1s, CWV "good" `[aspirational]` |
| NFR-7 | Accessibility | WCAG 2.2 AA |
| NFR-8 | Tenant isolation | No cross-tenant data access; per-tenant vector isolation (see `10`,`11`) — **hard requirement, day one** |
| NFR-9 | Cost per active user | AI COGS ≤ **$X/MAU** within free-tier budget (see `08`) `[modeled]` |

> **Honest note on NFR-1/NFR-4 tension:** "real-time" and "council-reviewed by 7 agents" pull against each other. Resolution: a **two-tier pipeline** — a fast, cheap path for time-sensitive alerts (single-model, low latency) and the full Council reserved for *significant* reports surfaced in the briefing. This is a core architectural decision, detailed in `07-ai-strategy.md`.

## 6. Budgets (the constraints that keep the vision honest)
- **Latency budget:** interactive < 250ms; alerting path < 15 min; Council async < 60s.
- **Cost budget:** every free MAU must be servable within the CAC/LTV model in `08`. The Council is expensive; gating *when* it runs is a product requirement, not just an optimization.
- **Trust budget:** a wrong high-confidence action is a severe defect. Target **false-action rate** on high-confidence (>80%) items is a tracked SLO.

## 7. Success metrics (North Star + supporting)

- **North Star:** **Weekly Acted-On Recommendations per Active User (WARU).** Not reads, not sessions — *actions taken*. This forces the whole org toward the master JTBD.
- Activation: % of new users who get a useful action in session 1.
- Retention: D1/D7/D30 on the briefing.
- Trust: confidence calibration error; false-action rate; appeal/overturn rate (R2+).
- Economic value (self-reported + modeled): $ and hours saved per MAU.
- Monetization: free→Pro conversion, NRR (R4 enterprise).

## 8. Explicit non-goals (for now)
- General-purpose chat assistant. (Conversation supports the product; it is not the product.)
- Social feed / engagement-maximizing timeline. We optimize *actions*, not time-on-app.
- Day-one global coverage of every domain/geography. We win one vertical, one geography first.
- Becoming a system of record (we read and recommend; we are not your CRM/ERP).
- Personalized financial/medical/legal *advice* at MVP (liability bright line).

## 9. Key assumptions to validate (challenge log)
- **A1:** Users will *act* on AI recommendations, not just read them. (If false, North Star collapses; pivot toward decision-support-for-experts framing.)
- **A2:** Quantified "savings/EV" are credible enough to drive habit. (Risk: users perceive numbers as fake precision → erodes trust faster than it builds. Mitigation: conservative estimates, ranges, visible methodology.)
- **A3:** A single vertical has enough recurring high-value actions to sustain a *daily* habit. (Risk: most days, nothing important changes → briefing feels empty → churn. Mitigation: blend evergreen optimizations with event-driven alerts; tune frequency.)
- **A4:** Multi-agent Council meaningfully beats a single strong model on synthesis quality, enough to justify cost/latency. (Must be proven on an eval set — see `07`. If not, collapse the Council to fewer agents / single-model + critic.)
- **A5:** We can acquire users below the LTV ceiling in `08`. (Unproven; GTM risk.)
