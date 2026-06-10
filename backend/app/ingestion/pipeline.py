"""AI data ingestion pipeline (Phase 8): ingest → normalize → dedupe → enrich → embed/index.
Legal: connectors respect ToS/robots/rate-limits; provenance + source attribution preserved
end-to-end. Personal connectors are consent-gated, read-only, tenant-private (never shared cache)."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field


@dataclass
class RawSignal:
    source_id: str
    source_name: str
    type: str
    title: str = ""
    body: str = ""
    url: str | None = None
    payload: dict = field(default_factory=dict)
    visibility: str = "public"          # public | tenant | private
    tenant_id: str | None = None


@dataclass
class EnrichedSignal:
    raw: RawSignal
    dedupe_key: str
    entities: list[str]
    domain_tags: list[str]
    geo: dict | None
    reliability: float
    impact: float


def normalize(raw: RawSignal) -> RawSignal:
    raw.title = (raw.title or "").strip()
    raw.body = (raw.body or "").strip()
    return raw


def dedupe_key(raw: RawSignal) -> str:
    return hashlib.sha256(f"{raw.type}|{raw.title}|{raw.url}".encode()).hexdigest()


def enrich(raw: RawSignal, reliability: float = 0.5) -> EnrichedSignal:
    # SCAFFOLD: entity extraction + geo + domain classification + impact scoring (ML).
    text = f"{raw.title} {raw.body}".lower()
    entities = [w for w in {"fed", "gas", "rate", "earnings"} if w in text]
    tags = ["economy"] if any(e in text for e in ("fed", "rate")) else []
    return EnrichedSignal(raw=raw, dedupe_key=dedupe_key(raw), entities=entities,
                          domain_tags=tags, geo=None, reliability=reliability, impact=0.5)


async def process(raw: RawSignal, gateway) -> EnrichedSignal:
    """Run a raw signal through the pipeline and emit events at each stage.
    Public signals → shared-cacheable analysis; private → tenant-scoped only."""
    raw = normalize(raw)
    enriched = enrich(raw)
    # embed + index (pgvector + OpenSearch); emit signal.enriched / signal.indexed.
    # await gateway.embed(...) ; await index_to_opensearch(...)
    return enriched
