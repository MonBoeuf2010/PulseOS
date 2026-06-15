"""Rate limiting (launch hardening, roadmap Step 5.3).

Bots find public auth/AI endpoints within days of launch, and every AI call
burns real money — so /auth and /chat are throttled per client IP.

Storage: in-memory by default — no Redis required, which keeps free/single-box
hosting (one web instance) truly dependency-free. Only multi-instance deploys
need shared counters: set RATELIMIT_STORAGE_URI to a Redis URL to enable them.
"""
from __future__ import annotations

import os

from slowapi import Limiter
from slowapi.util import get_remote_address

# In-memory unless an explicit shared store is configured. A single web instance
# (free Render / one VPS container) rate-limits correctly in-memory; no Redis.
_storage_uri = os.environ.get("RATELIMIT_STORAGE_URI") or None

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=_storage_uri,            # None → in-memory
    default_limits=[],                   # opt-in per route, no global default
    headers_enabled=True,                # emit X-RateLimit-* headers
)

# Tunable limits (override via env without a code change).
AUTH_LIMIT = os.environ.get("RATELIMIT_AUTH", "10/minute")
CHAT_LIMIT = os.environ.get("RATELIMIT_CHAT", "20/minute")
