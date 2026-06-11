"""Feed ranking algorithm (replaces newest-first ordering).

Score = (engagement + quality) / time_decay, plus a personalization boost.

Why this shape:
- Time decay (Hacker News style) keeps the feed fresh without burying a great
  post the second something newer appears.
- Engagement (reactions) rewards what the community actually found useful.
- Quality prior uses the author's stated confidence so well-calibrated calls
  start above pure noise even with zero reactions.
- Personalization boosts categories the viewer has reacted to before, so two
  users see different orderings of the same posts.

Tune the constants below; nothing else needs to change.
"""
from __future__ import annotations

import math
from datetime import datetime, timezone

# --- Tunables -----------------------------------------------------------
GRAVITY = 1.6            # higher = feed favors newer posts more aggressively
DECAY_OFFSET_HOURS = 2.0 # grace period so brand-new posts aren't divided by ~0
REACTION_WEIGHT = 1.0
CONFIDENCE_WEIGHT = 2.0  # a 0.9-confidence call ≈ worth ~2 reactions at start
PERSONAL_BOOST = 1.25    # multiplier when post category matches viewer interests
AUTHOR_SELF_PENALTY = 0.85  # slightly demote your own posts in your own feed


def post_score(*, reaction_count: int, confidence: float | None,
               created_at: datetime, now: datetime | None = None,
               viewer_interest_match: bool = False,
               is_own_post: bool = False) -> float:
    """Deterministic, cheap to compute in Python over a candidate window."""
    now = now or datetime.now(timezone.utc)
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    age_hours = max(0.0, (now - created_at).total_seconds() / 3600.0)

    quality = (reaction_count * REACTION_WEIGHT
               + (float(confidence) if confidence else 0.0) * CONFIDENCE_WEIGHT
               + 1.0)  # +1 so zero-engagement posts still rank by recency

    score = quality / math.pow(age_hours + DECAY_OFFSET_HOURS, GRAVITY)

    if viewer_interest_match:
        score *= PERSONAL_BOOST
    if is_own_post:
        score *= AUTHOR_SELF_PENALTY
    return score


def rank_posts(posts, *, viewer_user_id, viewer_top_categories: set[str]):
    """Sort a candidate window of Post ORM objects for a specific viewer."""
    now = datetime.now(timezone.utc)
    return sorted(
        posts,
        key=lambda p: post_score(
            reaction_count=p.reaction_count,
            confidence=float(p.confidence) if p.confidence is not None else None,
            created_at=p.created_at, now=now,
            viewer_interest_match=p.category in viewer_top_categories,
            is_own_post=p.author_user_id == viewer_user_id),
        reverse=True)
