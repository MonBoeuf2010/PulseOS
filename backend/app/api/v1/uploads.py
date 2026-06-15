"""File uploads & attachments — privacy-first design.

Privacy guidelines baked in (GDPR-aligned, matches your docs/phase-3):
1. EXPLICIT CONSENT: files only enter the system when the user actively picks
   one in the browser file dialog — the app never scans or reads their device.
2. OWNERSHIP: every attachment row stores owner_user_id; only the owner can
   delete it, and it's only publicly readable once attached to a public post.
3. MINIMIZATION: strict allow-list of content types + 10 MB cap. Filenames are
   replaced with a UUID on disk so no personal info leaks via the file name.
4. ERASURE: deleting an attachment removes the DB row AND the bytes (GDPR
   right-to-erasure). Your retention_sweep task can also call purge logic.

Storage: local disk in dev (UPLOAD_DIR). In production swap `_save_bytes` /
`_delete_bytes` for S3 with presigned URLs — the API contract stays identical.

Wiring (3 lines):
  - models/__init__.py: add the Attachment model below + "Attachment" to __all__
  - api/v1/router.py:   api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
  - schemas: add attachment_ids: list[UUID] = [] to PostIn, and
             attachments: list[dict] = [] to PostOut (id, content_type, url)
"""
from __future__ import annotations

import os
import uuid as uuid_lib
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_subject, db
from app.core.db import tenant_session
from app.core.security import Subject, verify_access_token

router = APIRouter()

UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "/tmp/lifeiq-uploads"))
MAX_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_TYPES = {
    "image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp",
    "image/gif": ".gif", "application/pdf": ".pdf", "text/csv": ".csv",
    "text/plain": ".txt",
}


# ---------------------------------------------------------------- model
# Add this class to backend/app/models/__init__.py:
#
# class Attachment(Base):
#     """A file a user explicitly uploaded; may be linked to a feed post."""
#     __tablename__ = "attachments"
#     id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     owner_user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
#     post_id: Mapped[uuid.UUID | None] = mapped_column(
#         ForeignKey("posts.id", ondelete="CASCADE"), nullable=True, index=True)
#     content_type: Mapped[str] = mapped_column(String)
#     original_name: Mapped[str] = mapped_column(String)   # shown in UI only
#     storage_key: Mapped[str] = mapped_column(String)     # uuid-based, no PII
#     size_bytes: Mapped[int] = mapped_column(Integer)
#     created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


def _save_bytes(storage_key: str, data: bytes) -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    (UPLOAD_DIR / storage_key).write_bytes(data)


def _delete_bytes(storage_key: str) -> None:
    try:
        (UPLOAD_DIR / storage_key).unlink(missing_ok=True)
    except OSError:
        pass


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload(file: UploadFile = File(...),
                 subject: Subject = Depends(current_subject),
                 session: AsyncSession = Depends(db)):
    from app.models import Attachment

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                            f"type {file.content_type} not allowed")
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "max 10 MB")

    storage_key = f"{uuid_lib.uuid4()}{ALLOWED_TYPES[file.content_type]}"
    _save_bytes(storage_key, data)

    att = Attachment(owner_user_id=subject.user_id, content_type=file.content_type,
                     original_name=file.filename or "file", storage_key=storage_key,
                     size_bytes=len(data))
    session.add(att)
    await session.flush()
    return {"id": str(att.id), "content_type": att.content_type,
            "original_name": att.original_name, "size_bytes": att.size_bytes,
            "url": f"/v1/uploads/{att.id}"}


def _optional_user_id(request: Request) -> UUID | None:
    """Best-effort identify the caller from a Bearer header or ?token= query param.

    Used only to authorize reads of PRIVATE (not-yet-posted) files. Returns None
    if absent/invalid — callers then treat the request as anonymous.
    """
    raw = request.headers.get("authorization", "")
    token = raw[7:].strip() if raw.lower().startswith("bearer ") else request.query_params.get("token")
    if not token:
        return None
    try:
        return UUID(verify_access_token(token)["sub"])
    except Exception:
        return None


@router.get("/{attachment_id}")
async def download(attachment_id: UUID, request: Request):
    """Serve a file.

    - Attached to a feed post → public (the feed is a public surface), so plain
      <img src> works without an auth header.
    - Not yet attached (private draft) → only the owner may read it.
    """
    from app.models import Attachment
    async with tenant_session(None) as session:
        att = await session.get(Attachment, attachment_id)
        if att is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "not found")
        if att.post_id is None:
            uid = _optional_user_id(request)
            if uid is None or uid != att.owner_user_id:
                raise HTTPException(status.HTTP_403_FORBIDDEN, "not yours")
        path = UPLOAD_DIR / att.storage_key
        if not path.exists():
            raise HTTPException(status.HTTP_410_GONE, "file purged")
        return FileResponse(path, media_type=att.content_type, filename=att.original_name)


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(attachment_id: UUID,
                 subject: Subject = Depends(current_subject),
                 session: AsyncSession = Depends(db)):
    """Right to erasure: removes the row AND the bytes."""
    from app.models import Attachment
    att = await session.get(Attachment, attachment_id)
    if att is None:
        return
    if att.owner_user_id != subject.user_id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "not yours")
    _delete_bytes(att.storage_key)
    await session.delete(att)


async def link_attachments_to_post(session: AsyncSession, *, post_id: UUID,
                                   owner_user_id: UUID,
                                   attachment_ids: list[UUID]) -> None:
    """Call from the feed `create` endpoint after creating a Post.

    Only links attachments the poster actually owns — a user can never publish
    someone else's file by guessing IDs.
    """
    if not attachment_ids:
        return
    from app.models import Attachment
    res = await session.execute(select(Attachment).where(
        Attachment.id.in_(attachment_ids),
        Attachment.owner_user_id == owner_user_id))
    for att in res.scalars().all():
        att.post_id = post_id
