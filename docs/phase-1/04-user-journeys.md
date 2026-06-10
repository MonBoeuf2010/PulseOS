# 04 — User Journeys

Journeys are written as step → system behavior → success criterion. The **first-run journey** is the most important asset PulseOS has: if Maya doesn't get a concrete, credible action in <60s, nothing else matters.

---

## J1 — First run (Maya, Operator) — the "time-to-value" journey **[critical]**

| Step | User does | System does | Success criterion |
|---|---|---|---|
| 1 | Lands, signs up (OAuth, ~10s) | Creates account, prompts MFA (skippable at MVP, enforced for sensitive connectors) | <15s to authenticated |
| 2 | Answers 4–6 onboarding Qs (role, goals, geography, domains, time/$ sensitivity) | Seeds AI memory; sets vertical context | User sees *why* each Q matters; can skip |
| 3 | Optionally connects calendar / location-region (consent screen) | Read-only ingest begins; clear audit + revoke | Connect or skip in <30s; trust preserved |
| 4 | Waits ~seconds on a "building your first briefing" state | Fast-path generation: pulls public + connected signals, ranks, runs Council on top items | First briefing in <60s `[aspirational]` |
| 5 | Sees Daily Briefing | Renders ranked actions w/ confidence, evidence, EV, cost-of-inaction | ≥1 item feels "for me," specific, credible |
| 6 | Taps an action → "Why?" | Expands evidence + dissenting view + methodology | User trusts it enough to act or save |
| 7 | Marks "useful" / "acted on" / "not for me" | Updates ranking + memory; logs to analytics | Feedback loop closed in 1 tap |

**Failure modes to design against:** empty briefing (no goals captured → force a minimal goal), generic briefing (looks like a news app → must reference *her* goals), fake precision (round/range numbers, show methodology).

---

## J2 — Daily habit loop (Maya) — the retention journey

1. **Morning push/notification:** "3 things worth your attention — 1 time-sensitive." (Notification quality is a retention SLO; a single noisy notification trains users to mute us.)
2. Opens briefing → scans ranked actions (≤60s).
3. Acts on 0–2 items; dismisses rest with one tap (signal).
4. **Weekly:** receives "intelligence report" — *this week you saved ~$X / Yh, captured N opportunities* `[modeled]` → reinforces value + nudges Pro.

**North-Star event:** an *acted-on* recommendation (WARU). Every loop element optimizes for it.

---

## J3 — Opportunity discovery → action (Maya / Devin)

1. Opportunity Engine detects a window (e.g., a recurring bill is renegotiable; an industry shift creates a career move; a local cost spike is avoidable).
2. Produces: Opportunity Score, Expected Value (with range), Confidence, Risk, Recommended Action.
3. User taps "How did you get this?" → Council breakdown (economist/statistician/contrarian views, dissent, evidence).
4. User acts (or snoozes / dismisses). If regulated-domain → "information, not advice" framing + no directive.
5. Outcome (if observable) feeds back into reputation of sources + calibration of the engine.

---

## J4 — Council report deep-dive (Devin, Professional)

1. A significant report is generated (event-driven or requested).
2. Pipeline runs: independent analysis → cross-agent debate → contradiction detection → consensus → confidence → executive summary (async, <60s, non-blocking).
3. Devin reads the **executive summary first**, then expands: supporting evidence, dissenting opinions, recommended actions, estimated impact.
4. Devin forwards/export the summary (with citations) — *this shareability is the viral + professional-credibility loop.*

---

## J5 — Community contributor (P3) **[R2+]**

1. Contributor submits a report (local news / traffic / market signal).
2. AI Verification: source analysis + cross-source validation + historical reliability + community confirmations → **Verification Score + confidence**, shown transparently.
3. Other users confirm/dispute; the AI Moderator screens spam/abuse/misinfo/brigading with *explanations*.
4. Accurate contributions raise the contributor's **Intelligence Reputation Score** → more reach; inaccurate ones lose reach.
5. Contributor sees their standing and the (explainable) reasons for any moderation; can **appeal to a human**.

**Design tension (named):** speed of UGC vs. accuracy of verification. A wrong report shown as "High confidence" is catastrophic. Default to *humility* in scores and make disputes visible fast.

---

## J6 — Company broadcast + meeting intelligence (P4) **[R4]**

1. Verified company publishes (text/voice/video/doc) → real-time distribution to followers' streams.
2. Company records a meeting/board/investor call → AI transcribes, summarizes, extracts decisions, risks, action items → executive report; searchable forever (semantic search), tenant-isolated.
3. Followers get the public broadcast; internal participants get the private meeting intelligence (strict access control).

**Highest-stakes journey for security/compliance:** wrong attribution of a decision, or a meeting leaking across tenants, is a company-ending defect. See `10`.

---

## J7 — Enterprise procurement (P5) **[R4]**

1. Economic buyer sees ROI case (analytics: value delivered to their users/org).
2. CISO runs security review → we provide SOC2 report, architecture docs (`10`,`11`), pen-test results, data-handling/DPA, tenancy-isolation proof, SSO/SCIM.
3. Pilot (private/segregated) → success metrics → annual contract.
4. Ongoing: custom councils, compliance suite, audit-log access, data residency.

---

## Cross-cutting loops (what makes the flywheel turn)

- **Feedback loop:** user feedback → better ranking + memory → more useful briefings → more feedback.
- **Trust loop:** calibrated confidence + visible evidence/dissent → user acts → outcome observed → calibration improves → more trust.
- **Network loop [R2+]:** contributors add signal → richer intelligence → more users → more contributors + reputation stakes → higher quality.
- **Economic loop:** value delivered (saved $/time, captured opportunities) → weekly report → Pro upgrade → funds better AI → more value.

> The flywheel only spins if the **single-player trust loop** works first. Network and economic loops are amplifiers, not igniters.
