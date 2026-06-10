"""Model-agnostic AI Gateway — the ONLY path to model providers (cost, routing,
caching, PII redaction, eval hooks, isolation). See docs/phase-2/07 §D and phase-1/07.

No service calls a vendor SDK directly. Swapping/adding providers is a change here only.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass

from app.core.config import get_settings

settings = get_settings()

# ---- PII redaction (pre-provider). Conservative; expand with a real NER pass. ----
_PII_PATTERNS = [
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[SSN]"),
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"), "[EMAIL]"),
    (re.compile(r"\b(?:\d[ -]?){13,16}\b"), "[CARD]"),
]


def redact(text: str) -> str:
    for pat, repl in _PII_PATTERNS:
        text = pat.sub(repl, text)
    return text


def _extract_subject(prompt: str) -> str:
    for line in prompt.splitlines():
        if line.startswith("SUBJECT:"):
            return line[len("SUBJECT:"):].strip()[:160]
    return prompt.strip()[:160]


def _stub_completion(system: str, prompt: str) -> str:
    """Deterministic, role-aware structured JSON so the pipeline is exercisable offline.

    A configured ANTHROPIC_API_KEY replaces this with real model output; the JSON shape
    here mirrors what the prompts in council/prompts.py instruct the models to return.
    """
    subject = _extract_subject(prompt)
    sys = system.lower()
    if "contrarian" in sys:
        stance = "neutral"
        counter = f"The consensus on '{subject}' may over-weight recent signal and ignore base rates."
    else:
        stance = "support"
        counter = ""
    body = {
        "stance": stance,
        "confidence": 0.8,
        "executive_summary": (f"The highest-value action on '{subject}' is to act early but small: "
                              "validate with one cheap, reversible step this week."),
        "consensus": (f"Evidence leans toward a time-sensitive, asymmetric upside on '{subject}'. "
                      "Cost of waiting exceeds the cost of a bounded first move."),
        "key_findings": [
            f"'{subject}' is trending across multiple independent signals.",
            "Downside of a small first move is capped; upside is non-linear.",
        ],
        "recommended_actions": [
            f"Take one reversible step on '{subject}' within 7 days [E1].",
            "Set a explicit review checkpoint in 30 days to scale or cut.",
        ],
        "estimated_impact": 1500,
        "cost_of_inaction": "Each week of delay compounds an estimated opportunity cost.",
        "strongest_counterpoint": counter,
        "dissent": [{"agent": "contrarian", "position": counter, "rationale": "base-rate caution"}]
        if counter else [],
    }
    return json.dumps(body)


@dataclass
class LLMResponse:
    text: str
    model: str
    tokens_in: int
    tokens_out: int
    cost_usd: float
    cached: bool = False


class AIGateway:
    """Routes by tier, caches shareable public-signal results, meters cost."""

    def __init__(self, cache=None, meter=None):
        self.cache = cache            # Redis client; public results only (no tenant data)
        self.meter = meter            # emits usage.recorded

    def _route(self, tier: str) -> str:
        return settings.anthropic_model if tier == "full" else settings.ai_fast_model

    async def complete(
        self, *, prompt: str, system: str = "", tier: str = "full",
        tenant_scoped: bool = True, max_tokens: int = 1500, temperature: float = 0.3,
    ) -> LLMResponse:
        model = self._route(tier)
        safe_prompt = redact(prompt)

        # Shared cache ONLY for non-tenant (public-signal) analysis — the COGS lever.
        cache_key = None
        if not tenant_scoped and self.cache is not None:
            cache_key = "ai:public:" + hashlib.sha256(f"{model}{system}{safe_prompt}".encode()).hexdigest()
            hit = await self.cache.get(cache_key)
            if hit:
                payload = json.loads(hit)
                return LLMResponse(**payload, cached=True)

        resp = await self._call_provider(model, system, safe_prompt, max_tokens, temperature)

        if cache_key is not None:
            await self.cache.set(cache_key, json.dumps(resp.__dict__), ex=3600)
        if self.meter is not None:
            await self.meter(kind="ai_completion", cost_usd=resp.cost_usd,
                             metadata={"model": model, "tier": tier})
        return resp

    async def _call_provider(self, model, system, prompt, max_tokens, temperature) -> LLMResponse:
        """Real impl uses the Anthropic async SDK. Returns a deterministic *structured*
        stub when no API key is configured so the full council pipeline (parsing,
        confidence scoring, synthesis, dissent) runs end-to-end in dev."""
        if not settings.anthropic_api_key:
            text = _stub_completion(system, prompt)
            return LLMResponse(text=text, model=model, tokens_in=len(prompt) // 4,
                               tokens_out=len(text) // 4, cost_usd=0.0)
        import anthropic  # imported lazily
        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        msg = await client.messages.create(
            model=model, max_tokens=max_tokens, temperature=temperature,
            system=system or "You are a precise analyst. Cite evidence. State uncertainty.",
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(b.text for b in msg.content if b.type == "text")
        ti, to = msg.usage.input_tokens, msg.usage.output_tokens
        cost = ti / 1e6 * 5 + to / 1e6 * 25  # SCAFFOLD pricing; route to live price table
        return LLMResponse(text=text, model=model, tokens_in=ti, tokens_out=to, cost_usd=cost)

    async def embed(self, text: str) -> list[float]:
        """SCAFFOLD: returns zero vector without a key; real impl calls embedding model."""
        if not settings.anthropic_api_key:
            return [0.0] * settings.embedding_dim
        # ... provider embedding call ...
        return [0.0] * settings.embedding_dim
