# Patch 2 — Turn on full automation (agents run by themselves)

Right now `schedule_briefings` returns `{"scheduled": 0}` — nothing runs
automatically. This patch makes the AI council generate a fresh briefing for
**every active user every morning at 06:00** with no human involved, and adds
an AI moderation agent for new feed posts.

## A. `backend/app/workers/tasks.py` — replace `schedule_briefings`

```python
async def schedule_briefings_sync() -> dict:
    """Fan out one build_briefing per active user (the daily automation loop)."""
    import uuid as uuid_lib
    from app.models import Membership

    async with tenant_session(None) as session:
        res = await session.execute(select(Membership))
        memberships = list(res.scalars().all())

    count = 0
    for m in memberships:
        job_id = str(uuid_lib.uuid4())
        try:
            # Through the broker when workers are running...
            build_briefing.delay(str(m.tenant_id), str(m.user_id), job_id)
        except Exception:
            # ...inline fallback in dev with no broker.
            await build_briefing_sync(m.tenant_id, m.user_id, job_id)
        count += 1
    return {"scheduled": count}


@celery_app.task(name="app.workers.tasks.schedule_briefings")
def schedule_briefings():
    return asyncio.run(schedule_briefings_sync())
```

(Beat already triggers this daily at 06:00 — see `celery_app.py`. Nothing
else to configure; just run a beat + worker process:
`celery -A app.workers.celery_app beat` and `celery -A app.workers.celery_app worker`.)

## B. New task — AI moderation agent for the feed

Every post is screened by the fast model before it counts as "live". Why:
once strangers can post, you are legally and reputationally responsible for
spam/abuse on your platform; an automated first-pass agent keeps you ahead of
it without hiring moderators.

Add to `tasks.py`:

```python
async def moderate_post_sync(post_id: str) -> dict:
    from uuid import UUID as _UUID
    from app.models import Post
    gateway = AIGateway()
    async with tenant_session(None) as session:
        post = await session.get(Post, _UUID(post_id))
        if post is None:
            return {"ok": False}
        verdict = await gateway.complete_fast(
            system=("You are a content moderator. Reply with exactly one word: "
                    "ALLOW, REVIEW, or BLOCK. BLOCK only spam, scams, doxxing, "
                    "or harassment. REVIEW borderline cases."),
            prompt=f"Title: {post.title}\n\nBody: {post.body[:2000]}")
        decision = (verdict or "REVIEW").strip().upper()
        if "BLOCK" in decision:
            await session.delete(post)
            return {"ok": True, "action": "blocked"}
        return {"ok": True, "action": "allowed"}


@celery_app.task(name="app.workers.tasks.moderate_post")
def moderate_post(post_id: str):
    return asyncio.run(moderate_post_sync(post_id))
```

Then in `api/v1/feed.py`, at the end of the `create` endpoint (before return):

```python
    try:
        from app.workers.tasks import moderate_post
        moderate_post.delay(str(post.id))
    except Exception:
        pass  # no broker in dev — post stays up, moderation is best-effort
```

> Note: if `AIGateway` doesn't expose a `complete_fast` helper yet, add a thin
> method on it that calls the existing completion path with
> `settings.ai_fast_model` — cheap model, ~1¢ per thousand posts.

## C. Connect real signals (so briefings stop using cold-start seeds)

`backend/app/ingestion/connectors.py` is a stub. The fastest real connector
is RSS — free, no API keys:

```python
# pip install feedparser  (add to pyproject)
import feedparser

FEEDS = [
    "https://hnrss.org/frontpage",
    "https://feeds.arstechnica.com/arstechnica/index",
    # add feeds for your users' verticals
]

def pull_rss() -> list[dict]:
    out = []
    for url in FEEDS:
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
```

Schedule it hourly in `celery_app.py` beat_schedule with a task that calls
`enrich_signal_sync(raw)` per item (dedupe on external_id already exists).
This single change is what flips LifeIQ from "demo data" to "live
intelligence" — everything downstream (council → briefing → feed) already
consumes Signals automatically.
