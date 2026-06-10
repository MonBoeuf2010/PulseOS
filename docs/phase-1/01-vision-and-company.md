# 01 — Vision & Company

## Mission

Turn the world's information into the right next action for each person and organization — continuously, transparently, and with its uncertainty made explicit.

## The problem we are actually solving

The constraint on modern decision-making is no longer *access* to information. It is **triage and synthesis under time pressure**. A knowledge worker, an operator, or an investor receives more signal in a day than they can read in a week. The expensive cognitive work is:

1. **Filtering** — which 1% of this matters to *me*?
2. **Synthesizing** — what does this collection of signals mean together?
3. **Deciding** — what should I do, and what happens if I don't?
4. **Trusting** — can I act on this without re-verifying it myself?

Search engines, news apps, and chatbots help with (1) and partially (2). Almost nothing systematically does (3) and (4). PulseOS's entire reason to exist is to own **(3) decisions** and **(4) trust** — and to make (4) a first-class, visible property (confidence, evidence, dissent) rather than a hidden assumption.

## What PulseOS is

- A **continuously-operating** intelligence layer (not request/response). It works while you sleep and tells you what changed and what to do.
- A **decision engine** whose primary output is a ranked action list, each item carrying confidence, evidence, expected value, and cost-of-inaction.
- A **multi-agent reasoning system** (the Strategic Council Engine) that produces auditable, dissent-aware analysis instead of a single confident voice.
- A **network**: corporate broadcasts, community reports, and reputation make the intelligence richer than any single user could assemble alone.

## What PulseOS is explicitly NOT

- **Not a chatbot.** Conversation is an interface, not the product. The product is the standing answer to "what should I do now?"
- **Not a news reader.** News is an input. We are judged on actions, not articles read.
- **Not a productivity/to-do tool.** We tell you what is *worth* doing; we are not primarily about tracking what you've decided to do.
- **Not an undifferentiated "everything app."** The five ecosystems are a destination, not a launch surface. See the wedge.

## Operating principles

1. **Decisions over information.** Every surface answers "so what / now what," not just "what."
2. **Calibrated honesty.** A visible, *calibrated* confidence score beats a confident guess. We would rather say "62%, here's the dissent" than fake certainty. Calibration is a measured KPI (see `07-ai-strategy.md`).
3. **Show your work.** Every recommendation links to evidence and to the dissenting view. No black-box verdicts.
4. **The user owns their mind.** Memory is inspectable, editable, deletable. Data isolation is non-negotiable.
5. **Latency is a feature.** Real-time intelligence that arrives late is just history. Speed budgets are in the PRD and infra plan.
6. **Earn trust before scale.** A wrong "fill your tank today" costs more credibility than a hundred right ones earn. Precision over recall in the action feed.
7. **Network effects compound; start a fire small enough to light.** Win one community/vertical completely before spreading.

## Ethics & stance (decided up front, not retrofitted)

- **We do not sell user data.** Monetization is subscription/enterprise, never data brokerage. This is a strategic commitment, because our entire value prop is trust.
- **We label AI-generated and AI-verified content.** Verification scores are estimates, shown as such, never laundered into false authority.
- **Misinformation is an existential product risk, not an edge case.** A community intelligence network that amplifies confident falsehoods is worse than nothing. Verification, reputation, and human appeal are core, day-one features — not bolt-ons (see `14-risk-analysis.md` R-2).
- **Financial/medical/legal "opportunities" carry liability.** "Fill your tank, save $12" is benign. "Buy this stock" is regulated advice. We will draw and enforce a bright line (see `08`, `10`, `14`).

## Naming & brand

- **PulseOS** — "Pulse" = real-time, alive, vital signs of your world; "OS" = the substrate other decisions run on.
- Voice: calm, precise, Bloomberg-meets-Linear. Never hype, never alarmist. The product earns attention by being *right and brief*, not loud.

## The "why now" (the bet)

Three curves cross in our favor:
1. **LLM cost/quality** crossed the line where multi-agent synthesis of long, messy inputs is affordable at consumer scale (cents, not dollars, per briefing) — and still falling.
2. **Information overload** is monotonically increasing; the human triage budget is fixed.
3. **Trust in single-source feeds collapsed** (algorithmic timelines, AI slop), creating demand for *adjudicated*, evidence-linked intelligence.

If any of these reverses (esp. #1 — if frontier reasoning re-inflates in price), the unit economics of the core loop are threatened. This is tracked as R-7 in the risk doc.
