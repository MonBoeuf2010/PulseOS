"""Full-council pipeline over the deterministic offline stub (no API key, no DB).

Guards the contract the briefing builder relies on: the stub yields parseable,
structured agent output, the synthesizer produces actions + dissent, and the
calibrated confidence clears the precision-first floor.
"""
import json

import pytest

from app.council.ai_gateway import AIGateway, _stub_completion
from app.council.orchestrator import CouncilEngine, CouncilInput, should_run_full
from app.services.briefing_service import MIN_CONFIDENCE


def test_stub_is_structured_json():
    out = _stub_completion(system="economist", prompt="SUBJECT: rates rising\nEVIDENCE:\n(none)")
    data = json.loads(out)
    assert data["stance"] in ("support", "neutral")
    assert 0.0 <= data["confidence"] <= 1.0
    assert data["recommended_actions"] and data["executive_summary"]


def test_contrarian_stub_diverges():
    eco = json.loads(_stub_completion("you are the economist", "SUBJECT: x"))
    con = json.loads(_stub_completion("you are the contrarian", "SUBJECT: x"))
    assert con["stance"] == "neutral" and con["strongest_counterpoint"]
    assert eco["stance"] == "support"


@pytest.mark.asyncio
async def test_full_council_clears_confidence_floor():
    engine = CouncilEngine(AIGateway(), gate_threshold=0.6)
    ci = CouncilInput(subject="adopt an open-weight model", domain="market",
                      evidence=[{"id": "E1", "source": "arxiv", "reliability": 0.7,
                                 "snippet": "benchmarks closing"}],
                      estimated_value=0.9, uncertainty=0.8, user_relevance=0.85)
    assert should_run_full(ci, 0.6)
    report = await engine.run(ci)
    assert report.tier == "full"
    assert report.confidence >= MIN_CONFIDENCE          # would be surfaced in a briefing
    assert report.recommended_actions                    # synthesizer produced actions
    assert report.executive_summary
