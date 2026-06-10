"""Contradiction detection, evidence grounding, hallucination reduction (Phase 6)."""
from __future__ import annotations


def detect_contradictions(traces: list[dict]) -> list[dict]:
    """Surface where agents disagree. SCAFFOLD: stance + claim-polarity heuristic;
    production uses an NLI model over claim pairs."""
    out: list[dict] = []
    stances = {t["role"]: t["parsed"].get("stance") for t in traces if t.get("role")}
    opposers = [r for r, s in stances.items() if s == "oppose"]
    supporters = [r for r, s in stances.items() if s == "support"]
    if opposers and supporters:
        out.append({"type": "stance_conflict", "support": supporters, "oppose": opposers})
    return out


def ground_claims(claims: list, evidence: list[dict]) -> list[str]:
    """Hallucination reduction: drop/flag claims with no supporting evidence reference."""
    if not evidence:
        return [c if isinstance(c, str) else str(c) for c in claims]
    grounded = []
    for c in claims:
        text = c if isinstance(c, str) else c.get("text", str(c))
        grounded.append(text)   # SCAFFOLD: real impl checks [E#] refs / semantic support
    return grounded


def aggregate_evidence(signals: list[dict]) -> list[dict]:
    """Build the evidence list passed to the council from enriched signals, carrying
    source + reliability for provenance/attribution (Phase 8 compliance)."""
    return [{"id": f"E{i+1}", "signal_id": s.get("id"), "source": s.get("source", "?"),
             "url": s.get("url"), "reliability": s.get("reliability", 0.5),
             "snippet": (s.get("title") or s.get("body") or "")[:240]}
            for i, s in enumerate(signals)]
