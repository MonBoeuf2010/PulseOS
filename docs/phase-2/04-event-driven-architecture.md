# Phase 2.4 — Event-Driven Architecture

## Why event-driven
PulseOS is *continuous*, not request/response. Ingestion, enrichment, council analysis, briefing generation, fan-out distribution, and analytics are all asynchronous reactions to events. The event backbone decouples producers from consumers and is the substrate for horizontal scaling.

## Backbone choice (now vs. later)
- **MVP–R2:** **Celery + Redis broker** for task queues + a lightweight **outbox → fan-out** pattern in Postgres for domain events. Simple, low-ops.
- **R2–R3:** introduce **RabbitMQ** for richer routing (topic exchanges, per-consumer-group fan-out, dead-letter exchanges) once distribution/fan-out fan-out demands it.
- **R3+ (streaming):** **Kafka/Kinesis** for the high-volume ingestion + analytics stream where replay, partitioned ordering, and stream processing matter.

> Documented deviation from the brief's "RabbitMQ from day 1": start on Celery/Redis, graduate to RabbitMQ at the routing-complexity gate. The event *contracts* below are broker-agnostic, so migration is a transport swap, not a redesign.

## Transactional Outbox (exactly-once-ish domain events)
Domain state changes and their events are committed in the **same DB transaction** to an `outbox` table; a relay publishes to the broker and marks rows sent. This avoids the dual-write problem (DB committed but event lost, or vice-versa).
```
service writes domain row + outbox row  (one txn)
        → outbox relay (poller/logical-decoding) → broker → consumers (idempotent)
```
Consumers are **idempotent** (dedupe on `event_id`), giving effective exactly-once processing on top of at-least-once delivery.

## Canonical event envelope
```json
{
  "event_id": "uuid",
  "type": "signal.ingested",
  "version": 1,
  "tenant_id": "uuid|null",
  "occurred_at": "RFC3339",
  "trace_id": "uuid",
  "actor": {"kind": "system|user|service", "id": "uuid|null"},
  "data": { /* type-specific payload (schema-registry validated) */ }
}
```
- **Versioned** types; additive evolution; breaking changes bump `version` and run dual-consumers during migration.
- **`trace_id`** propagates end-to-end for distributed tracing across the pipeline.
- Payloads validated against a **schema registry** (JSON Schema) in CI and at publish time.

## Core event catalog
| Event type | Producer | Primary consumers | Effect |
|---|---|---|---|
| `signal.ingested` | ingestion connectors | normalize, dedupe, enrich workers | start pipeline |
| `signal.enriched` | enrichment worker | embed worker, relevance scorer, council gater | index + score |
| `signal.indexed` | embed/index worker | briefing builder | available for retrieval |
| `council.requested` | gater / API | council orchestrator | run analysis (fast/full) |
| `council.completed` | council orchestrator | briefing builder, opportunity engine, notifier | attach report, score calibration |
| `briefing.generated` | briefing builder | notifier, analytics | push + record |
| `briefing.item_feedback` | API | ranking trainer, memory updater | learn |
| `opportunity.detected` | opportunity engine | notifier, briefing builder | surface |
| `report.submitted` | API (community) | verification pipeline, moderation | verify + screen |
| `report.verified` | verification pipeline | feed builder, reputation | publish + score |
| `moderation.flagged` | AI moderator | notifier, admin queue | act + explain |
| `broadcast.published` | corporate API | fan-out distributor | deliver to followers |
| `meeting.recorded` | corporate API | transcription, meeting-intel worker | analyze |
| `meeting.analyzed` | meeting-intel worker | indexer, notifier | searchable |
| `reputation.changed` | reputation engine | feed weighting | adjust reach |
| `user.deletion_requested` | API | erasure orchestrator | GDPR workflow (Phase 3) |
| `usage.recorded` | all services | metering, cost dashboards | billing + COGS |
| `security.anomaly` | threat detection | session manager, alerting | step-up / revoke |

## Pipeline (the AI data flow, event view)
```
[connectors] --signal.ingested--> [normalize] --> [dedupe] --> [enrich(entities,geo,tags)]
   --signal.enriched--> [embed+index] --signal.indexed--> [relevance score per user]
   --(gate: value*uncertainty*relevance)--> council.requested
        --> [Strategic Council Engine] --council.completed-->
            [briefing builder] --briefing.generated--> [notifier] --> user
```

## Delivery guarantees & failure handling
- **At-least-once** delivery + **idempotent** consumers ⇒ effective exactly-once.
- **Dead-letter queues** per consumer group; poison messages parked + alerted after N retries with exponential backoff + jitter.
- **Ordering:** only guaranteed *per partition key* (e.g., per `tenant_id`/`signal_id`) where it matters; most consumers are commutative by design.
- **Backpressure:** bounded queues; shed/deprioritize low-value signals first (the gater already filters most signals away from the expensive Council).
- **Replay:** outbox + (later) Kafka retention allow reprocessing after a consumer bug fix.

## Idempotency keys
Every consumer persists processed `event_id`s (Redis set with TTL for hot path; `processed_events` table for durable). Re-delivery is a no-op.

## Observability
- Every event carries `trace_id`; OpenTelemetry spans wrap publish/consume.
- Metrics: queue depth, consumer lag, DLQ rate, processing latency p50/p95/p99 per consumer, end-to-end "ingest→briefing" latency (the NFR-1 freshness SLO).
- Alerts on lag/DLQ thresholds and on the default partition receiving rows.
