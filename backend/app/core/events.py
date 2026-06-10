"""Event bus abstraction (transactional outbox → broker). Broker-agnostic so we can
migrate Celery/Redis → RabbitMQ → Kafka without touching producers/consumers.
See docs/phase-2/04-event-driven-architecture.md."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class Event:
    type: str
    data: dict
    tenant_id: str | None = None
    version: int = 1
    event_id: str = field(default_factory=lambda: str(uuid4()))
    trace_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: float = field(default_factory=time.time)
    actor: dict = field(default_factory=lambda: {"kind": "system", "id": None})

    def to_envelope(self) -> dict:
        return asdict(self)


async def emit(session: AsyncSession, event: Event) -> None:
    """Write to the outbox in the SAME transaction as the domain change (no dual-write).
    A relay process publishes outbox rows to the broker and marks them sent. Consumers
    are idempotent (dedupe on event_id)."""
    await session.execute(
        text("""INSERT INTO outbox (id, type, tenant_id, payload, created_at)
                VALUES (:id, :type, :tid, :payload, now())"""),
        {"id": event.event_id, "type": event.type, "tid": event.tenant_id,
         "payload": json.dumps(event.to_envelope())},
    )


# Idempotency helper for consumers (Redis-backed in real impl).
_processed: set[str] = set()  # SCAFFOLD: replace with Redis set + TTL / durable table


def already_processed(event_id: str) -> bool:
    if event_id in _processed:
        return True
    _processed.add(event_id)
    return False
