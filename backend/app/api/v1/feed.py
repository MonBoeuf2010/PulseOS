"""Community feed endpoints — users publish intelligence calls others can react to."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_subject, db
from app.api.v1.uploads import link_attachments_to_post
from app.core.config import get_settings
from app.core.security import Subject
from app.models import User
from app.repositories.posts import PostRepository
from app.schemas import PostIn, PostOut

router = APIRouter()


def _to_out(post, reacted: bool, attachments: list[dict] | None = None) -> PostOut:
    return PostOut(
        id=post.id, author_name=post.author_name, category=post.category, title=post.title,
        body=post.body, confidence=float(post.confidence) if post.confidence is not None else None,
        reaction_count=post.reaction_count, reacted=reacted, created_at=post.created_at,
        attachments=attachments or [])


@router.get("", response_model=list[PostOut])
async def feed(subject: Subject = Depends(current_subject), session: AsyncSession = Depends(db)):
    repo = PostRepository(session)
    posts = await repo.feed(viewer_user_id=subject.user_id)
    post_ids = [p.id for p in posts]
    reacted = await repo.reacted_ids(subject.user_id, post_ids)
    attachments = await repo.attachments_for(post_ids)
    return [_to_out(p, p.id in reacted, attachments.get(p.id, [])) for p in posts]


@router.post("", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def create(body: PostIn, subject: Subject = Depends(current_subject),
                 session: AsyncSession = Depends(db)):
    user = await session.get(User, subject.user_id)
    name = (user.display_name if user and user.display_name else
            (user.email.split("@")[0] if user else "Operator"))
    repo = PostRepository(session)
    post = await repo.create(
        author_user_id=subject.user_id, author_name=name, tenant_id=subject.tenant_id,
        category=body.category, title=body.title, body=body.body, confidence=body.confidence)

    # Link only attachments the poster actually owns (ownership check inside).
    await link_attachments_to_post(
        session, post_id=post.id, owner_user_id=subject.user_id,
        attachment_ids=body.attachment_ids)
    attachments = (await repo.attachments_for([post.id])).get(post.id, [])

    # Best-effort AI moderation via the worker; skipped when no background worker
    # is deployed (the post stays up either way).
    if get_settings().enable_background_jobs:
        try:
            from app.workers.tasks import moderate_post
            moderate_post.delay(str(post.id))
        except Exception:
            pass

    return _to_out(post, reacted=False, attachments=attachments)


@router.post("/{post_id}/react", response_model=PostOut)
async def react(post_id: UUID, subject: Subject = Depends(current_subject),
                session: AsyncSession = Depends(db)):
    repo = PostRepository(session)
    post = await repo.get(post_id)
    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "post not found")
    now_on = await repo.toggle_reaction(post=post, user_id=subject.user_id)
    attachments = (await repo.attachments_for([post.id])).get(post.id, [])
    return _to_out(post, reacted=now_on, attachments=attachments)
