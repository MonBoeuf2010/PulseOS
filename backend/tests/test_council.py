"""Council engine tests (Phase 9). Runs against the stub gateway (no API key needed)."""
import pytest

from app.council.ai_gateway import AIGateway, redact
from app.council.orchestrator import CouncilEngine, CouncilInput, should_run_full
from app.council.confidence import calibrate, score_confidence


def test_pii_redaction():
    out = redact("email me at a@b.com or 123-45-6789")
    assert "a@b.com" not in out and "123-45-6789" not in out


def test_council_gate_threshold():
    high = CouncilInput(subject="x", estimated_value=0.9, uncertainty=0.9, user_relevance=0.9)
    low = CouncilInput(subject="x", estimated_value=0.1, uncertainty=0.1, user_relevance=0.1)
    assert should_run_full(high, 0.6) and not should_run_full(low, 0.6)


def test_calibration_monotonic():
    assert calibrate(0.8) <= 0.8                 # calibration pulls overconfidence down
    assert calibrate(0.0) <= calibrate(0.5) <= calibrate(1.0)


def test_confidence_penalizes_contradictions():
    traces = [{"parsed": {"stance": "support", "confidence": 0.8}, "role": "economist"},
              {"parsed": {"stance": "oppose", "confidence": 0.7}, "role": "contrarian"}]
    ev = [{"reliability": 0.8}]
    c0 = score_confidence(traces=traces, evidence=ev, contradictions=[], domain="general")
    c1 = score_confidence(traces=traces, evidence=ev,
                          contradictions=[{"type": "stance_conflict"}], domain="general")
    assert c1 <= c0


@pytest.mark.asyncio
async def test_fast_path_runs_without_api_key():
    engine = CouncilEngine(AIGateway(), gate_threshold=0.6)
    report = await engine.run(CouncilInput(subject="gas prices rising",
                                            estimated_value=0.1, uncertainty=0.1, user_relevance=0.1))
    assert report.tier == "fast" and 0.0 <= report.confidence <= 1.0
