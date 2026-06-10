"""Strategic Council Engine orchestrator (Phase 6).

Pipeline: ground → independent analysis (parallel) → debate → contradiction detection →
consensus → confidence scoring → executive summary. Two-tier: fast path vs full council,
gated by value*uncertainty*relevance to control COGS/latency (Phase 1/07).
"""
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field

from app.council.ai_gateway import AIGateway
from app.council.prompts import REGISTRY
from app.council.confidence import score_confidence, calibrate
from app.council.verification import detect_contradictions, ground_claims

INDEPENDENT = ["economist", "statistician", "psychologist", "domain_expert", "contrarian"]


@dataclass
class CouncilInput:
    subject: str
    domain: str = "general"
    evidence: list[dict] = field(default_factory=list)   # [{id, source, reliability, snippet}]
    user_relevance: float = 0.5
    estimated_value: float = 0.5
    uncertainty: float = 0.5


@dataclass
class CouncilReport:
    tier: str
    executive_summary: str
    consensus: str
    confidence: float
    dissent: list[dict]
    evidence: list[dict]
    recommended_actions: list[str]
    estimated_impact: float | None
    cost_of_inaction: str | None
    agent_traces: list[dict]
    cost_usd: float
    latency_ms: int


def should_run_full(ci: CouncilInput, threshold: float) -> bool:
    """Gate: only the highest-value, most-uncertain, most-relevant items get full council."""
    return (ci.estimated_value * ci.uncertainty * ci.user_relevance) >= threshold


class CouncilEngine:
    def __init__(self, gateway: AIGateway, gate_threshold: float = 0.6):
        self.ai = gateway
        self.threshold = gate_threshold

    async def run(self, ci: CouncilInput) -> CouncilReport:
        import time
        t0 = time.monotonic()
        tier = "full" if should_run_full(ci, self.threshold) else "fast"
        if tier == "fast":
            report = await self._fast_path(ci)
        else:
            report = await self._full_council(ci)
        report.latency_ms = int((time.monotonic() - t0) * 1000)
        return report

    # ---- Fast path: single grounded summary, cheap model, public-cacheable ----
    async def _fast_path(self, ci: CouncilInput) -> CouncilReport:
        ev_block = _format_evidence(ci.evidence)
        prompt = (f"SUBJECT: {ci.subject}\nEVIDENCE:\n{ev_block}\n"
                  "Summarize the single most valuable action, with confidence and cost of inaction.")
        r = await self.ai.complete(prompt=prompt, tier="fast", tenant_scoped=False, max_tokens=400)
        conf = calibrate(0.6, ci.domain)
        return CouncilReport(
            tier="fast", executive_summary=r.text, consensus=r.text, confidence=conf,
            dissent=[], evidence=ci.evidence, recommended_actions=[], estimated_impact=None,
            cost_of_inaction=None, agent_traces=[], cost_usd=r.cost_usd, latency_ms=0)

    # ---- Full council ----
    async def _full_council(self, ci: CouncilInput) -> CouncilReport:
        ev_block = _format_evidence(ci.evidence)
        base = f"SUBJECT: {ci.subject}\nDOMAIN: {ci.domain}\nEVIDENCE:\n{ev_block}\n"

        # 1. Research analyst grounds first (evidence map + gaps).
        grounding = await self._agent("research_analyst", base, ci.domain)

        # 2. Independent analyses in parallel (tenant-scoped; not shared-cached).
        analyses = await asyncio.gather(*[
            self._agent(role, base + f"\nEVIDENCE_MAP:{grounding['raw']}", ci.domain)
            for role in INDEPENDENT
        ])
        traces = {INDEPENDENT[i]: analyses[i] for i in range(len(INDEPENDENT))}
        traces["research_analyst"] = grounding

        # 3. Debate + contradiction detection (structured, deterministic over outputs).
        contradictions = detect_contradictions(list(traces.values()))

        # 4. Synthesis preserving dissent.
        synth_prompt = (base + f"\nAGENT_ANALYSES:{json.dumps([t['parsed'] for t in traces.values()])}"
                        f"\nCONTRADICTIONS:{json.dumps(contradictions)}")
        synth = await self._agent("synthesizer", synth_prompt, ci.domain, max_tokens=900)
        s = synth["parsed"]

        # 5. Confidence: blend agent agreement + evidence strength + calibration.
        conf = score_confidence(traces=list(traces.values()), evidence=ci.evidence,
                                contradictions=contradictions, domain=ci.domain)

        grounded_actions = ground_claims(s.get("recommended_actions", []), ci.evidence)
        total_cost = sum(t["cost"] for t in traces.values()) + synth["cost"]
        return CouncilReport(
            tier="full",
            executive_summary=s.get("executive_summary", synth["raw"][:500]),
            consensus=s.get("consensus", ""),
            confidence=conf,
            dissent=s.get("dissent", [{"agent": "contrarian",
                                       "position": traces["contrarian"]["parsed"].get("strongest_counterpoint", ""),
                                       "rationale": ""}]),
            evidence=ci.evidence,
            recommended_actions=grounded_actions,
            estimated_impact=s.get("estimated_impact"),
            cost_of_inaction=s.get("cost_of_inaction"),
            agent_traces=[{"agent": k, **v["parsed"]} for k, v in traces.items()],
            cost_usd=total_cost, latency_ms=0)

    async def _agent(self, role: str, prompt: str, domain: str, max_tokens: int = 600) -> dict:
        system = REGISTRY[role].format(domain=domain) if "{domain}" in REGISTRY[role] else REGISTRY[role]
        r = await self.ai.complete(prompt=prompt, system=system, tier="full",
                                   tenant_scoped=True, max_tokens=max_tokens)
        return {"raw": r.text, "parsed": _safe_json(r.text), "cost": r.cost_usd, "role": role}


def _format_evidence(ev: list[dict]) -> str:
    return "\n".join(f"[E{i+1}] ({e.get('source','?')}, rel={e.get('reliability',0.5)}): "
                     f"{e.get('snippet','')}" for i, e in enumerate(ev)) or "(none)"


def _safe_json(text: str) -> dict:
    try:
        start, end = text.find("{"), text.rfind("}")
        return json.loads(text[start:end + 1]) if start >= 0 else {"_text": text}
    except Exception:
        return {"_text": text}
