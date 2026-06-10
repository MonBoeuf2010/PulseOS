"""Confidence scoring + calibration — the trust moat (Phase 1/07, Phase 6).
Confidence must be CALIBRATED (80% => right ~80% of the time). Calibration maps raw
model confidence onto the empirical curve learned from council_outcomes."""
from __future__ import annotations

from statistics import mean

# SCAFFOLD: per-domain calibration maps learned offline from council_outcomes
# (predicted vs realized). Replace with a fitted isotonic/Platt model per domain.
_CALIBRATION: dict[str, list[tuple[float, float]]] = {
    "general": [(0.0, 0.0), (0.5, 0.45), (0.8, 0.72), (1.0, 0.95)],
}


def calibrate(raw: float, domain: str = "general") -> float:
    """Piecewise-linear remap of raw confidence onto the empirical reliability curve."""
    pts = _CALIBRATION.get(domain, _CALIBRATION["general"])
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= raw <= x1:
            t = 0 if x1 == x0 else (raw - x0) / (x1 - x0)
            return round(y0 + t * (y1 - y0), 4)
    return round(raw, 4)


def _agreement(traces: list[dict]) -> float:
    stances = [t["parsed"].get("stance") for t in traces if t["parsed"].get("stance")]
    if not stances:
        return 0.5
    support = sum(1 for s in stances if s in ("support", "neutral"))
    return support / len(stances)


def _evidence_strength(evidence: list[dict]) -> float:
    if not evidence:
        return 0.2
    return min(1.0, mean(e.get("reliability", 0.5) for e in evidence) * (1 + 0.1 * len(evidence)))


def score_confidence(*, traces: list[dict], evidence: list[dict],
                     contradictions: list[dict], domain: str) -> float:
    """Blend agent agreement, evidence strength, and contradiction penalty, then calibrate."""
    agreement = _agreement(traces)
    strength = _evidence_strength(evidence)
    raw_confs = [t["parsed"].get("confidence") for t in traces
                 if isinstance(t["parsed"].get("confidence"), (int, float))]
    model_conf = mean(raw_confs) if raw_confs else 0.5
    contradiction_penalty = min(0.3, 0.1 * len(contradictions))
    raw = max(0.0, 0.4 * agreement + 0.3 * strength + 0.3 * model_conf - contradiction_penalty)
    return calibrate(raw, domain)
