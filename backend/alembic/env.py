"""Alembic environment — async engine, app-driven URL, pgvector-aware.

The DB URL comes from app settings (env-driven), and target_metadata is the
live ORM metadata, so `alembic revision --autogenerate` diffs against the real
models. Importing app.models registers every table on Base.metadata.
"""
from __future__ import annotations

import asyncio
from logging.config import fileConfig

import pgvector.sqlalchemy
from alembic import context
from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool

from app.core.config import get_settings
from app.core.db import Base
import app.models  # noqa: F401 — registers all tables on Base.metadata

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Inject the app's DB URL (async driver) at runtime.
config.set_main_option("sqlalchemy.url", get_settings().database_url)

target_metadata = Base.metadata


def render_item(type_, obj, autogen_context):
    """Render pgvector columns as pgvector.sqlalchemy.Vector(dim=N) with the import."""
    if type_ == "type" and isinstance(obj, pgvector.sqlalchemy.Vector):
        autogen_context.imports.add("import pgvector.sqlalchemy")
        dim = getattr(obj, "dim", None)
        return f"pgvector.sqlalchemy.Vector(dim={dim})" if dim else "pgvector.sqlalchemy.Vector()"
    return False


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_item=render_item,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_item=render_item,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
