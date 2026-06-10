"""Pluggable source connectors (Phase 8). Each is rate-limited, ToS/robots-aware, and
attaches provenance. Add a connector by subclassing Connector and registering it."""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from app.ingestion.pipeline import RawSignal


class Connector(ABC):
    source_id: str
    source_name: str
    rate_limit_per_min: int = 60

    @abstractmethod
    async def fetch(self) -> AsyncIterator[RawSignal]:
        ...


class RSSNewsConnector(Connector):
    source_id = "rss"; source_name = "RSS News"

    def __init__(self, feeds: list[str]):
        self.feeds = feeds

    async def fetch(self) -> AsyncIterator[RawSignal]:
        # SCAFFOLD: parse feeds, yield RawSignal(type="news", visibility="public", ...)
        if False:
            yield  # pragma: no cover


class MarketDataConnector(Connector):
    source_id = "market"; source_name = "Market Data API"
    async def fetch(self) -> AsyncIterator[RawSignal]:
        if False:
            yield


class PersonalCalendarConnector(Connector):
    """Consent-gated, READ-ONLY, tenant-private. Never enters shared cache."""
    source_id = "calendar"; source_name = "Calendar"

    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id

    async def fetch(self) -> AsyncIterator[RawSignal]:
        if False:
            yield


REGISTRY: dict[str, type[Connector]] = {
    "rss": RSSNewsConnector, "market": MarketDataConnector, "calendar": PersonalCalendarConnector,
}
