# Patch 1 — Wire the ranking algorithm into the feed

## A. `backend/app/repositories/posts.py` — replace the `feed()` method

```python
from app.feed.ranking import rank_posts
from sqlalchemy import desc, select

    async def feed(self, *, viewer_user_id, limit: int = 50,
                   candidate_window: int = 200) -> list:
        """Pull a recent candidate window, then rank it for THIS viewer.

        Why a window: ranking in Python over the last N posts is simple and
        fast at your scale (<50K users). Move to a materialized score column
        only if the window query ever becomes the bottleneck.
        """
        res = await self.session.execute(
            select(Post).order_by(desc(Post.created_at)).limit(candidate_window))
        candidates = list(res.scalars().all())

        # Viewer's top categories = categories of posts they reacted to.
        cat_res = await self.session.execute(
            select(Post.category)
            .join(PostReaction, PostReaction.post_id == Post.id)
            .where(PostReaction.user_id == viewer_user_id)
            .limit(100))
        top_categories = set(cat_res.scalars().all())

        ranked = rank_posts(candidates, viewer_user_id=viewer_user_id,
                            viewer_top_categories=top_categories)
        return ranked[:limit]
```

## B. `backend/app/api/v1/feed.py` — pass the viewer in

Change the `feed` endpoint's repo call from:

```python
    posts = await repo.feed()
```
to:
```python
    posts = await repo.feed(viewer_user_id=subject.user_id)
```

That's it — the feed is now personalized, decays over time, and rewards
engagement instead of just showing newest-first.
