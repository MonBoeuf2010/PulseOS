"""Centralized configuration (12-factor, env-driven). Secrets come from AWS Secrets
Manager in prod (injected as env). Never hard-code secrets."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "development"
    secret_key: str = "dev-only-change-me"

    # Datastores
    database_url: str = "postgresql+asyncpg://pulse:pulse@localhost:5432/pulseos"
    redis_url: str = "redis://localhost:6379/0"
    rabbitmq_url: str = "amqp://pulse:pulse@localhost:5672//"
    opensearch_url: str = "http://localhost:9200"

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

    # Billing
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_monthly: str = ""
    stripe_price_yearly: str = ""
    frontend_base_url: str = "http://localhost:3000"

    cors_origins: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
