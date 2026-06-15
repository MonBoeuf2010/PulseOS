# Phase 4 — Wireframe Descriptions (every screen)

ASCII wireframes + behavior notes. Desktop layout shown; mobile adaptation noted per screen. All screens follow the design system (Phase 4 design-system.md).

---

## Onboarding (first-run, the time-to-value screen)
```
┌──────────────────────────────────────────────┐
│           LifeIQ · Let's tune your intel      │
│                                                │
│   What's your role?     [ Operator ▼ ]         │
│   Your top goals        [ + grow revenue   ]   │
│                         [ + manage finances]   │
│   Where are you?        [ Austin, TX       ]   │
│   Domains to watch      [finance][career][..]  │
│   Sensitivity   time ◉───  money ────◉         │
│                                                │
│   [ Connect calendar ]  [ Connect location ]   │
│   (read-only · revoke anytime · why we ask ⓘ)  │
│                                                │
│              [  Build my first briefing → ]    │
└──────────────────────────────────────────────┘
```
- ≤6 questions, each skippable, each shows *why*. Seeds AI memory. Connectors consent-gated, read-only.
- Submitting → "Building your briefing" (animated, <60s) → Dashboard. **This screen owns the activation metric.**
- Mobile: single-column, full-screen steps, progress dots.

---

## Page 1 — Intelligence Dashboard (home base)
```
┌──────────┬───────────────────────────────────────────────┬───────────────┐
│ SIDEBAR  │  Good morning, Maya · Tue Jun 10 · ⌘K to search │  ●3 notif  ◔  │
│          ├───────────────────────────────────────────────┼───────────────┤
│ ▸Dash    │  TODAY'S BRIEFING            "3 things matter"  │  YOUR STREAMS │
│  Opps    │  ┌─────────────────────────────────────────┐   │  ◷ Acme posted │
│  Communs │  │ ⚡ IMMEDIATE ACTION         conf ▓▓▓▓░ 84%│   │  ◷ Fed: rate.. │
│  Follows │  │ Fill your tank today                     │   │  ◷ TX econ ▲   │
│  Companies│ │ Regional gas +6% forecast next 48h       │   ├───────────────┤
│  Meetings│  │ Save ~$12 (range $8–$18) · ignore → +$12  │  │  THIS WEEK    │
│  Analytics│ │ [Why? ▾]  [Useful] [Acted] [✕]            │  │  ⏱ 4.2h saved │
│  Settings│  └─────────────────────────────────────────┘   │  💲 $86 saved  │
│          │  ┌── OPPORTUNITIES ──┐ ┌── RISKS ──┐           │  🎯 6 acted   │
│          │  │ Refi opportunity  │ │ Subscription│          │               │
│          │  │ EV +$1,400/yr  78%│ │ renews $240 │          │               │
│          │  └───────────────────┘ └─────────────┘          │               │
│          │  ┌ TIME ┐ ┌ MONEY ┐ ┌ EVENTS ┐ ┌ FORECASTS ┐   │               │
└──────────┴───────────────────────────────────────────────┴───────────────┘
```
- Hero = single highest-value action (full-width card). Then a ranked grid of sections (Immediate Actions / Opportunities / Risks / Time / Money / Events / Forecasts) — empty sections hidden or shown as quiet-day state.
- Each card: title, rationale, **ConfidenceMeter**, EV + range, cost-of-inaction, evidence expander, 1-tap feedback.
- "Why?" expands `EvidenceList` + `DissentChips` inline; clicking dissent → `CouncilReportPanel` slide-over.
- Right rail: followed-entity **streams** + **weekly value** stats (retention/upsell).
- **Mobile:** vertical stack, hero first; right-rail content moves below; bottom tab bar.

---

## Council Report Panel (slide-over / full screen mobile)
```
┌─ Council Report ───────────────────────────── ✕ ┐
│ EXECUTIVE SUMMARY                      conf 84% │
│ Fill tank within 48h; regional supply + ...     │
│ ── CONSENSUS ───────────────────────────────    │
│ 5 of 7 agents agree. Net EV +$12 (8–18).        │
│ ── DISSENT ──────────────────────────────────   │
│ ◆ Contrarian: price may dip if refinery reopens │
│ ◆ Statistician: small sample, wide CI           │
│ ── AGENT TRACES (expand) ────────────────────   │
│ ▸ Economist  ▸ Statistician  ▸ Domain Expert    │
│ ── EVIDENCE ─────────────────────────────────   │
│ • EIA regional report  ●reliability  ↗          │
│ • Local price feed     ●              ↗          │
│ ── RECOMMENDED ACTIONS · EST. IMPACT +$12 ──     │
└──────────────────────────────────────────────────┘
```
Progressive disclosure: summary → consensus → dissent → traces → evidence. Every claim links to a source. This is the "show your work" trust surface.

---

## Page 5 — Opportunity Engine
```
┌ Opportunities ──── [All ▾][Financial][Career][Savings] ── sort: EV ▾ ┐
│ ┌──────────────────────────────┐ ┌──────────────────────────────┐  │
│ │ ◍ 78  Refinance mortgage     │ │ ◍ 65  Negotiate internet bill │  │
│ │ EV +$1,400/yr   conf 78%     │ │ EV +$180/yr   conf 71%        │  │
│ │ Risk: low · rate window open │ │ Risk: none · competitor promo │  │
│ │ Action: request quote ▸      │ │ Action: call retention ▸      │  │
│ │ [Act] [Dismiss] [Why?]       │ │ [Act] [Dismiss] [Why?]        │  │
│ └──────────────────────────────┘ └──────────────────────────────┘  │
│ ⓘ Regulated items shown as information, not advice (badge).         │
└─────────────────────────────────────────────────────────────────────┘
```
- Score ring + EV range + risk + recommended action. `[Act]` records WARU. Regulated domains carry a clear "information, not advice" badge.
- Filters by domain/status; sort by EV/score/confidence. Empty → "Scanning for opportunities…".

---

## Page 3 — Community Intelligence Network
```
┌ Community · Austin ──── [Submit report +] ──── filter: domain ▾ ┐
│ ┌───────────────────────────────────────────────┐             │
│ │ 🚦 I-35 closed northbound at 6th — accident    │             │
│ │ by @localdriver ·rep 320· 12m ago              │             │
│ │ Verification ▓▓▓▓░ HIGH 87%  [components ▾]     │             │
│ │   source · cross-source · history · 14 confirms │             │
│ │ [Confirm ✓ 14] [Dispute ✕ 1]                    │             │
│ └───────────────────────────────────────────────┘             │
│ ┌ Submit report ─────────────────────────────────┐            │
│ │ [what's happening?]  domain[▾] location[auto]   │            │
│ └─────────────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```
- Each report shows **VerificationBadge** with expandable components, confirm/dispute (reputation-weighted). AI-moderated with visible, explained actions + appeal link.

---

## Page 4 — AI Communities
```
┌ c/economics ─────────────── [Join] · 12.4k members ───────────┐
│ [Post] [Debate] [Reports] [Live]                              │
│ ┌ pinned: Weekly macro thread ───────────────────────────┐    │
│ │ ▲ 240  "Is the yield curve signal still valid?"        │    │
│ │ by @analyst ·rep 880· · 64 comments                    │    │
│ └─────────────────────────────────────────────────────────┘   │
│ ⚖ AI Moderator: 2 comments limited (manipulation) · appeal ⓘ │
└────────────────────────────────────────────────────────────────┘
```
- Posts/comments/debates/reports/live. Moderation actions shown inline with explanation + appeal. Reputation visible on every author.

---

## Page 2 — Company Page & Live Rooms (Corporate)
```
┌ Acme Corp  ✓verified ──────────────── [Follow] 8.2k followers ┐
│ [Live feed] [Broadcasts] [Meetings(internal)] [About]         │
│ ● LIVE  CEO update · 2,104 watching        [Join room]        │
│ ┌ Latest broadcast ───────────────────────────────────────┐  │
│ │ 📄 Q2 results posted · summary by Council ▾              │  │
│ │ text · voice · video · doc                                │  │
│ └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

### Meeting Recorder / Meeting Intelligence (internal, B/E)
```
┌ Board Meeting · Jun 10 ───────────────── ● Recording 12:04 ──┐
│ [● Rec] [⏸] [⏹ End]   participants: 6   🔒 tenant-isolated    │
│ ── after processing ──────────────────────────────────────    │
│ SUMMARY · DECISIONS(3) · RISKS(2) · ACTION ITEMS(5)           │
│ ▸ Decision: approve hiring plan — owner: CFO                  │
│ ▸ Risk: runway < 9mo if ...                                    │
│ ▸ Action: finalize budget — @maya — due Jun 20                │
│ 🔎 Semantic search across all meetings [ ____ ]               │
└────────────────────────────────────────────────────────────────┘
```
- Record → transcribe → extract decisions/risks/actions → searchable forever (tenant-isolated, ABAC participant-scoped). High-stakes extractions show "AI-generated, verify" + edit.

---

## Universal Search (⌘K)
```
┌ ⌘K ─────────────────────────────────────────────┐
│ 🔎 fed rate                                      │
│ ── ACTIONS ──   Generate briefing · Go to Opps   │
│ ── REPORTS ──   "Fed signals hold" ·rep· 87%     │
│ ── COMPANIES ─  Federal Reserve                  │
│ ── COMMUNITIES  c/economics                      │
│ ── PEOPLE ───   @macro_analyst                   │
│            results in 42ms                       │
└──────────────────────────────────────────────────┘
```
Typed, grouped results across all entities; keyboard-only; <100ms target.

---

## Profile / Settings / AI Memory
```
┌ Settings ── [Account][Security][Memory][Notifs][Billing][Privacy] ┐
│ AI MEMORY (inspect · edit · delete)                               │
│ ┌ goal · "grow ARR to $1M"            [edit][delete] ┐            │
│ ┌ profession · "SaaS founder"          [edit][delete] ┐           │
│ ┌ preference · "concise, data-first"   [edit][delete] ┐           │
│ [+ add memory]   "This is everything LifeIQ remembers about you" │
│ PRIVACY:  [Export my data] [Delete my account]  (GDPR)            │
└────────────────────────────────────────────────────────────────────┘
```
- Full memory transparency (inspect/edit/delete). Security tab: MFA, passkeys, active sessions (revoke). Privacy: export/delete (Phase 3 workflows). Notifications: cadence + channel controls (anti-fatigue).

---

## Notifications
```
┌ Notifications ───────────────── [mark all read] ┐
│ ⚡ Time-sensitive · Fill tank today (briefing)   │
│ 🎯 New opportunity · Refi window (EV +$1,400)    │
│ ◷ Acme posted Q2 results                         │
│ ⚖ A report you confirmed was verified HIGH       │
└──────────────────────────────────────────────────┘
```
Quality-gated; grouped by priority; cadence user-controlled.

---

## Analytics / Weekly Report
```
┌ Your week in intelligence ───────────────────────┐
│ ⏱ 4.2h saved   💲 $86 saved   🎯 6 acted   📈 +12%│
│  sparkline ▁▂▄▆█▅▃   "vs last week"               │
│ Top win: caught subscription renewal ($240)       │
│         [ Upgrade to Pro for unlimited council ]  │
└────────────────────────────────────────────────────┘
```
Quantified value (modeled, conservative) → retention + Pro upsell.

---

## Admin Portal
```
┌ Admin ── [Moderation][Users][Audit][System][Costs] ┐
│ MODERATION QUEUE  (12 pending · 3 appeals)          │
│ ▸ post#... manipulation 0.82 · [uphold][overturn]   │
│ AUDIT  filter actor/tenant/time · export            │
│ SYSTEM  queue depth · council cost/MAU · SLOs       │
└──────────────────────────────────────────────────────┘
```
Moderation review + appeals, audit search, system health, **cost-per-MAU / council-cost dashboards** (the budget discipline). RBAC-gated.

---

## Enterprise Dashboard
```
┌ Enterprise · Acme ── [Org][Members][Security][Compliance][Custom Council][Usage] ┐
│ ORG VALUE: $312k modeled value delivered · 142 seats · NRR 118%                  │
│ SECURITY: SSO ✓ SCIM ✓ MFA enforced ✓ Data residency: EU                         │
│ COMPLIANCE: SOC2 report ↓ · audit log access · DPA · sub-processors              │
│ CUSTOM COUNCIL: [configure agents/domains]                                       │
└────────────────────────────────────────────────────────────────────────────────────┘
```
ROI, member/seat management, security posture, compliance artifacts (download SOC2/DPA), custom council config, usage/cost. This screen *is* the enterprise renewal case.

---

## Cross-screen states
- **Empty:** every list/section has a designed empty state with a primary action (never blank).
- **Loading:** layout-matched skeletons; council streams in progressively.
- **Error:** human copy + recovery + trace id; degraded-AI banner keeps app usable.
- **Quiet day:** "Nothing urgent — here are optimizations" (anti-churn).
- **Mobile:** every screen reflows to single-column; side panels → bottom sheets; primary action thumb-reachable; bottom tab nav.
