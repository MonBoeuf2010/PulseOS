"""Celery app + Beat schedule (Phase 2.7B). Broker → RabbitMQ at scale, Redis at MVP."""
from celery import Celery
from celery.schedules import crontab

from app.core.config import get_settings

settings = get_settings()

# Broker: RabbitMQ at scale, Redis at MVP. Fall back to Redis when no AMQP URL is
# configured (e.g. free single-box / Render hosting has Redis but no RabbitMQ).
_broker = settings.rabbitmq_url or settings.redis_url
celery_app = Celery("lifeiq", broker=_broker, backend=settings.redis_url)
celery_app.conf.update(
    task_routes={
        "app.workers.tasks.enrich_signal": {"queue": "enrich"},
        "app.workers.tasks.run_council": {"queue": "council"},
        "app.workers.tasks.build_briefing": {"queue": "briefing"},
        "app.workers.tasks.notify": {"queue": "notify"},
    },
    task_acks_late=True, worker_prefetch_multiplier=1, task_reject_on_worker_lost=True,
    task_default_retry_delay=5, task_max_retries=5,
)

celery_app.conf.beat_schedule = {
    "daily-briefings": {"task": "app.workers.tasks.schedule_briefings", "schedule": crontab(hour=6, minute=0)},
    "hourly-rss-ingest": {"task": "app.workers.tasks.ingest_rss", "schedule": crontab(minute=0)},
    "retention-sweep": {"task": "app.workers.tasks.retention_sweep", "schedule": crontab(hour=3, minute=0)},
    "calibration-recompute": {"task": "app.workers.tasks.recompute_calibration", "schedule": crontab(hour=4, minute=0)},
}
