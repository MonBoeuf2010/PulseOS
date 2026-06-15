"""Async SQLAlchemy engine + per-request tenant scoping (RLS backstop).

Tenant isolation is defense-in-depth: app-layer ABAC AND Postgres RLS. We set
`app.tenant_id` per transaction so the RLS policy
  USING (tenant_id = current_setting('app.tenant_id')::uuid)
filters every tenant-scoped table. With a transaction-pooled connection (PgBouncer),
this MUST be SET LOCAL inside the active transaction.
"""
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()


def asyncpg_connect_args(url: str) -> dict:
    """Driver connect args. For asyncpg, disable prepared-statement caching (both
    SQLAlchemy's adapt-layer cache and asyncpg's native one) so the same
    DATABASE_URL works through a transaction pooler (Neon/Supabase use PgBouncer)
    without "prepared statement does not exist" errors. No-op for any other
    driver, so local dev and tests are unaffected."""
    if "+asyncpg" in url:
        return {"prepared_statement_cache_size": 0, "statement_cache_size": 0}
    return {}


engine = create_async_engine(
    settings.database_url, pool_pre_ping=True, pool_size=20, max_overflow=10,
    connect_args=asyncpg_connect_args(settings.database_url),
)
SessionMaker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


@asynccontextmanager
async def tenant_session(tenant_id: UUID | None) -> AsyncIterator[AsyncSession]:
    """Yield a session with RLS tenant context bound for the transaction's lifetime."""
    async with SessionMaker() as session:
        async with session.begin():
            if tenant_id is not None:
                # SET LOCAL is scoped to this transaction → safe with transaction pooling.
                await session.execute(
                    text("SELECT set_config('app.tenant_id', :tid, true)"),
                    {"tid": str(tenant_id)},
                )
            yield session


async def get_db_for_request(tenant_id: UUID | None) -> AsyncIterator[AsyncSession]:
    """FastAPI dependency wrapper."""
    async with tenant_session(tenant_id) as session:
        yield session
