"""Community feed endpoints — users publish intelligence calls others can react to."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_subject, db
from app.core.security import Subject
from app.models import User
from app.repositories.posts import PostRepository
from app.schemas import PostIn, PostOut

router = APIRouter()


def _to_out(post, reacted: bool) -> PostOut:
    return PostOut(
        id=post.id, author_name=post.author_name, category=post.category, title=post.title,
        body=post.body, confidence=float(post.confidence) if post.confidence is not None else None,
        reaction_count=post.reaction_count, reacted=reacted, created_at=post.created_at)


@router.get("", response_model=list[PostOut])
async def feed(subject: Subject = Depends(current_subject), session: AsyncSession = Depends(db)):
    repo = PostRepository(session)
    posts = await repo.feed()
    reacted = await repo.reacted_ids(subject.user_id, [p.id for p in posts])
    return [_to_out(p, p.id in reacted) for p in posts]


@router.post("", response_model=PostOut, status_code=status.HTTP_201_CREATED)
async def create(body: PostIn, subject: Subject = Depends(current_subject),
                 session: AsyncSession = Depends(db)):
    user = await session.get(User, subject.user_id)
    name = (user.display_name if user and user.display_name else
            (user.email.split("@")[0] if user else "Operator"))
    post = await PostRepository(session).create(
        author_user_id=subject.user_id, author_name=name, tenant_id=subject.tenant_id,
        category=body.category, title=body.title, body=body.body, confidence=body.confidence)
    return _to_out(post, reacted=False)


@router.post("/{post_id}/react", response_model=PostOut)
async def react(post_id: UUID, subject: Subject = Depends(current_subject),
                session: AsyncSession = Depends(db)):
    repo = PostRepository(session)
    post = await repo.get(post_id)
    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "post not found")
    now_on = await repo.toggle_reaction(post=post, user_id=subject.user_id)
    return _to_out(post, reacted=now_on)
