"""Rate limiting (launch hardening, roadmap Step 5.3).

Bots find public auth/AI endpoints within days of launch, and every AI call
burns real money — so /auth and /chat are throttled per client IP.

Storage: in-memory by default (fine for a single-process VPS launch). For
multi-worker / multi-instance deploys set RATELIMIT_STORAGE_URI to the Redis
URL so counters are shared; we fall back to memory if it's unreachable.
"""
from __future__ import annotations

import os

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings

settings = get_settings()

# Prefer an explicit storage URI; otherwise share the app's Redis in prod, and
# use in-memory in dev so no broker is required to run locally.
_storage_uri = os.environ.get("RATELIMIT_STORAGE_URI")
if not _storage_uri and settings.env != "development":
    _storage_uri = settings.redis_url

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=_storage_uri,            # None → in-memory
    default_limits=[],                   # opt-in per route, no global default
    headers_enabled=True,                # emit X-RateLimit-* headers
)

# Tunable limits (override via env without a code change).
AUTH_LIMIT = os.environ.get("RATELIMIT_AUTH", "10/minute")
CHAT_LIMIT = os.environ.get("RATELIMIT_CHAT", "20/minute")
