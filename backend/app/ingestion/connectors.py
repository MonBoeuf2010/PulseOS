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


# Default public feeds — free, no API keys. Add feeds for your users' verticals.
FEEDS = [
    "https://hnrss.org/frontpage",
    "https://feeds.arstechnica.com/arstechnica/index",
]


def pull_rss(feeds: list[str] | None = None) -> list[dict]:
    """Fetch RSS entries as raw signal dicts (shape consumed by enrich_signal_sync).

    Dedupe happens downstream on external_id, so re-pulling the same feed is safe.
    """
    import feedparser  # heavy import kept local to the call

    out: list[dict] = []
    for url in (feeds or FEEDS):
        parsed = feedparser.parse(url)
        for e in parsed.entries[:20]:
            out.append({
                "source": parsed.feed.get("title", url),
                "external_id": e.get("id") or e.get("link"),
                "domain": "market",
                "title": e.get("title", "(untitled)"),
                "snippet": (e.get("summary") or "")[:500],
                "url": e.get("link"),
                "reliability": 0.6, "impact": 0.5,
            })
    return out
