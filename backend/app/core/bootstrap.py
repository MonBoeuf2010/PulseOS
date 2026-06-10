"""Dev/test database bootstrap.

Production schema changes go through Alembic migrations. For local dev and tests we
create the pgvector extension and the ORM tables directly. RLS policies are applied by
migrations in prod; in dev, tenant isolation is enforced at the repository layer (every
query filters by tenant_id), so create_all alone is sufficient to run end-to-end.
"""
from __future__ import annotations

from sqlalchemy import text

from app.core.db import Base, engine
import app.models  # noqa: F401  ensure all models are registered on Base.metadata


async def init_db() -> None:
    async with engine.begin() as conn:
        # pgvector extension is required for the Vector columns.
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)


async def drop_all() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
