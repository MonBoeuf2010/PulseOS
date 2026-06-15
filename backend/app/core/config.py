"""Centralized configuration (12-factor, env-driven). Secrets come from AWS Secrets
Manager in prod (injected as env). Never hard-code secrets."""
from functools import lru_cache
from urllib.parse import urlsplit, urlunsplit

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _normalize_async_pg(url: str) -> str:
    """Coerce a managed-host Postgres URL into the asyncpg form the app uses.

    Free/managed Postgres (Neon, Supabase, Render, Railway, Heroku, Fly) hand out
    `postgres://`/`postgresql://` URLs, usually with a `?sslmode=require` (and
    sometimes `channel_binding=require`) query. asyncpg's connect() does NOT
    accept the libpq spellings `sslmode`/`channel_binding` and errors on them —
    but SQLAlchemy's asyncpg dialect *does* understand `ssl=require`. So we:
      • rewrite the scheme to `postgresql+asyncpg://`
      • rename `sslmode` → `ssl` (keeps TLS on, which Neon/Supabase require)
      • drop `channel_binding` (libpq-only)
    The result is one DATABASE_URL that works unchanged across every provider —
    paste the connection string the host shows you, nothing to edit by hand.
    """
    if not url:
        return url
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+asyncpg://" + url[len("postgresql://"):]
    if "+asyncpg" in url and "?" in url:
        parts = urlsplit(url)
        out = []
        for kv in parts.query.split("&"):
            if not kv:
                continue
            key, _eq, val = kv.partition("=")
            if key == "channel_binding":
                continue
            if key == "sslmode":
                key = "ssl"
            out.append(f"{key}={val}" if val else key)
        url = urlunsplit(parts._replace(query="&".join(out)))
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "development"
    secret_key: str = "dev-only-change-me"

    # Datastores
    database_url: str = "postgresql+asyncpg://pulse:pulse@localhost:5432/lifeiq"
    redis_url: str = "redis://localhost:6379/0"
    rabbitmq_url: str = "amqp://pulse:pulse@localhost:5672//"
    opensearch_url: str = "http://localhost:9200"

    # Background jobs: Celery worker + beat (ingestion, scheduled briefings,
    # moderation). Off by default so the API runs standalone on free/single-box
    # hosting — briefings build inline in the request and posts skip async
    # moderation. Flip on once a worker + broker are deployed.
    enable_background_jobs: bool = False

    @field_validator("database_url", mode="before")
    @classmethod
    def _coerce_database_url(cls, v: str) -> str:
        return _normalize_async_pg(v)

    # Auth
    jwt_private_key_pem: str = ""
    jwt_public_key_pem: str = ""
    jwt_alg: str = "EdDSA"
    access_token_ttl_seconds: int = 900          # 15 min
    refresh_token_ttl_seconds: int = 60 * 60 * 24 * 30

    # AI Gateway
    ai_provider: str = "anthropic"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-opus-4-8"     # latest capable reasoning model
    ai_fast_model: str = "claude-haiku-4-5-20251001"
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536

    # Council cost/latency budgets (Phase 7 AI strategy)
    council_full_max_usd: float = 0.50
    council_gate_threshold: float = 0.6          # value*uncertainty*relevance gate

    # AI usage caps (launch hardening, Step 5.4) — protect the API budget.
    free_daily_ai_limit: int = 25                # chat/council calls per free user per day
    premium_daily_ai_limit: int = 1000           # generous ceiling for paying users
    global_daily_ai_spend_cap_usd: float = 50.0  # hard kill-switch across all users/day

    # Billing
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_basic: str = ""                 # Basic $5/mo (ad-supported)
    stripe_price_monthly: str = ""               # Pro monthly
    stripe_price_yearly: str = ""                # Pro yearly
    frontend_base_url: str = "http://localhost:3000"
    revenuecat_webhook_auth: str = ""            # shared secret for the iOS IAP webhook

    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
