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
engine = create_async_engine(settings.database_url, pool_pre_ping=True, pool_size=20, max_overflow=10)
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
