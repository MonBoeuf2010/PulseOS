"""App-level wiring: health + that the full v1 surface is mounted. No DB (lifespan
is not triggered because we don't enter the TestClient context manager)."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_expected_routes_mounted():
    paths = {r.path for r in app.routes}
    for p in [
        "/v1/auth/register", "/v1/auth/login", "/v1/auth/refresh",
        "/v1/dashboard", "/v1/briefings", "/v1/briefings/{briefing_id}",
        "/v1/council/analyze", "/v1/council/reports/{report_id}",
        "/v1/memory", "/v1/opportunities", "/v1/search",
    ]:
        assert p in paths, f"missing route {p}"


def test_protected_route_requires_auth():
    # No bearer token → 403 from HTTPBearer (auto_error).
    assert client.get("/v1/dashboard").status_code in (401, 403)
