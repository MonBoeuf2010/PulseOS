# 07 — AI Strategy

This is the heart of PulseOS's defensibility *and* its biggest cost/quality/latency risk. The strategy below is built around one principle: **be model-agnostic, own the orchestration + evaluation + outcome data.** Models are rented; the trust layer and the data are owned.

---

## 1. The Strategic Council Engine

A multi-agent pipeline that turns messy signals into auditable, dissent-aware, confidence-scored intelligence.

### Agents (roles, not necessarily 7 separate model calls)
1. **Economist** — incentives, second-order effects, EV/cost framing.
2. **Statistician** — base rates, sample/selection bias, calibration sanity.
3. **Behavioral Psychologist** — human reaction, framing, bias in the *source* and the *user*.
4. **Domain Expert** — vertical specifics (finance/sports/local/etc.).
5. **Contrarian** — actively argues the opposite; surfaces the dissent we are required to show.
6. **Research Analyst** — gathers + grounds claims in evidence (retrieval, citation).
7. **Executive Synthesizer** — produces the consensus + confidence + exec summary, *preserving* dissent.

### Pipeline
```
Input signal(s)
  → Research Analyst grounds + retrieves evidence
  → Independent analysis (Economist, Statistician, Psychologist, Domain Expert, Contrarian in parallel)
  → Cross-agent debate (structured; agents see each other's claims)
  → Contradiction detection (explicit: where do they disagree, and why)
  → Consensus generation (Synthesizer)
  → Confidence scoring (calibrated — see §4)
  → Executive summary (action, evidence, dissent, EV, cost-of-inaction)
```

### The honest critique (A4 from the PRD)
A 7-agent debate is **expensive and slow**. We must *prove* it beats a single strong model + critic on a labeled eval set before we pay for it at scale. Therefore:

- **Default architecture is collapsible.** Start with the *minimum* council that wins evals (often: 1 strong generator + Contrarian + Synthesizer + grounded retrieval). Add agents only where evals show marginal lift > marginal cost/latency.
- **Agents may be the same base model with different system prompts/tools**, not 7 different models. Diversity of *role and prompt* matters more than diversity of *vendor* for most lift; we add a second vendor where it measurably de-correlates errors.

---

## 2. Two-tier pipeline (resolves the real-time vs. council tension)

| Tier | When | Latency | Cost | Mechanism |
|---|---|---|---|---|
| **Fast path** | Time-sensitive alerts, simple signals, ranking pre-filter | <2s | low | Single fast model + cached retrieval + rules |
| **Full Council** | "Significant reports": high EV, high stakes, surfaced in briefing | async <60s | high | Full/collapsed council, gated |

**Gating logic (a product requirement, not an afterthought):** only escalate to the full Council when `estimated_value × uncertainty × user_relevance` exceeds a threshold. Most signals never trigger it. This is how we keep COGS inside the budget in `08`.

---

## 3. Model strategy

- **Model-agnostic abstraction layer.** All agents call through an internal gateway (provider/model behind config). Never hard-code a vendor. Lets us route by cost/quality/latency and survive price/availability shocks (R-7).
- **Tiered routing:** cheap/fast model for fast path + pre-ranking; frontier reasoning model for the Council's hard synthesis; embeddings model for retrieval/memory.
- **Use the latest, most capable Claude models for the Council's reasoning-heavy synthesis** (the brief specifies the Claude 4.x family / Fable 5; pick the strongest available reasoning model for Synthesizer + Contrarian, with the option to add a second vendor where evals show error de-correlation).
- **Build vs. buy:** *buy* foundation models; *build* orchestration, retrieval, memory, evaluation, calibration, and the outcome-data flywheel. We never train a foundation model; we may fine-tune small models for routing/classification/verification where data justifies it (R2+).

## 4. Calibration & confidence (the trust layer — our actual moat)

Confidence scores are worthless unless **calibrated**: when we say 80%, it should be right ~80% of the time.

- **Calibration is a measured KPI.** Maintain a labeled eval set per domain; track predicted-vs-realized; report calibration error (e.g., ECE/Brier). Gate user-facing confidence display on hitting a calibration bar (PRD H3).
- **Outcome capture:** when a recommendation's outcome is observable (price moved, deal closed, savings realized, user feedback), log it. Over time this becomes proprietary calibration data → the recommendations get measurably better → the moat.
- **Confidence is shown as ranges + methodology**, never false-precise single numbers without provenance.

## 5. Evaluation framework (non-negotiable, built before scale)

- **Golden eval sets** per surface (briefing relevance, opportunity EV accuracy, verification correctness, council synthesis quality).
- **LLM-as-judge + human spot-checks** with anti-gaming (rotating rubrics, human audits of the judge).
- **Regression gates in CI:** no model/prompt change ships if it regresses eval or calibration beyond threshold.
- **Online metrics:** false-action rate (high-confidence items later judged wrong), feedback signals, acted-on rate. Offline eval predicts; online metrics confirm.
- **Red-team set:** adversarial inputs (misinformation, prompt injection from ingested web content, manipulation attempts).

## 6. AI safety, security & abuse

- **Prompt injection is a primary threat** because we ingest untrusted web/community content into agent context. Defenses: treat all ingested content as untrusted data (not instructions), content/instruction separation, allow-listed tools, output validation, no autonomous high-impact actions without user confirmation. (See `10`.)
- **Hallucination control:** retrieval-grounding required for factual claims; unsupported claims are flagged or suppressed; "I don't know / insufficient evidence" is a valid, encouraged output.
- **Tenant isolation in AI:** per-tenant memory + retrieval; **no shared vector store across tenants**; user/tenant context never leaks into another's prompt (hard requirement, `10`/`11`).
- **No regulated advice:** classifier gates securities/medical/legal outputs to "information, not advice."

## 7. AI memory system

- Long-term, structured user memory (interests, goals, profession, preferences) + episodic (past actions/feedback).
- **User-controlled:** inspect / edit / delete (GDPR/CCPA). Deletions propagate to embeddings/retrieval.
- Memory feeds personalization of ranking, briefings, and the Opportunity Engine. It is the switching-cost moat (`06`).

## 8. Cost discipline (ties to `08`)

- Per-MAU AI COGS budget enforced via: Council gating, aggressive caching (embeddings, retrieval, repeated public-signal analysis is shared across users — *public* analysis is multi-tenant-safe; *personal* synthesis is not), model routing, batching, and prompt compression.
- **Shared compute for public signals:** the analysis of a public event (e.g., "gas prices rising regionally") is computed once and reused across all relevant users; only the *personalization* layer is per-user. This is the key cost lever and is tenant-safe because the shared layer touches no private data.

## 9. AI roadmap

- **MVP:** collapsed Council (proven on evals), fast path, calibration v1, memory, single-domain opportunity model, eval harness + CI gates.
- **R2:** verification model for community reports, reputation scoring, search/embeddings at scale.
- **R3:** AI moderator, multi-domain opportunity models, fine-tuned routing/classification models.
- **R4:** custom/enterprise councils, private-deployment model routing, domain-tuned models per enterprise (isolated).

## 10. Key AI bets & how we'll know we're wrong
- **Bet:** multi-agent synthesis + calibration is a durable advantage. **Falsified if:** single-model + critic matches Council on evals (then we collapse it) *and* frontier models ship calibrated personalized briefings natively (then our moat must be data/network/vertical, not orchestration).
- **Bet:** outcome data compounds into a moat. **Falsified if:** outcomes are too noisy/unobservable to learn from in our verticals (then calibration plateaus and recommendations stay generic).
