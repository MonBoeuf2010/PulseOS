"""Data access for identity: users, tenants, memberships, sessions.

Identity tables are NOT tenant-scoped by RLS (a user can belong to many tenants),
so these queries run on a session opened without a tenant context.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Membership, Session, Tenant, User


def _sha256(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> User | None:
        res = await self.session.execute(select(User).where(User.email == email.lower()))
        return res.scalar_one_or_none()

    async def get(self, user_id: UUID) -> User | None:
        return await self.session.get(User, user_id)

    async def create_user_with_tenant(
        self, *, email: str, password_hash: str, display_name: str | None,
        tenant_name: str | None,
    ) -> tuple[User, Tenant, Membership]:
        """Register flow: every new user gets a personal tenant they own."""
        user = User(email=email.lower(), display_name=display_name,
                    password_hash=password_hash, status="active", email_verified=False)
        tenant = Tenant(type="personal", name=tenant_name or (display_name or email.split("@")[0]),
                        plan="free")
        self.session.add_all([user, tenant])
        await self.session.flush()  # assign PKs
        membership = Membership(tenant_id=tenant.id, user_id=user.id, role="owner")
        self.session.add(membership)
        await self.session.flush()
        return user, tenant, membership

    async def memberships(self, user_id: UUID) -> list[Membership]:
        res = await self.session.execute(select(Membership).where(Membership.user_id == user_id))
        return list(res.scalars().all())

    async def roles_for(self, user_id: UUID, tenant_id: UUID) -> list[str]:
        res = await self.session.execute(
            select(Membership.role).where(
                Membership.user_id == user_id, Membership.tenant_id == tenant_id))
        return [r for r in res.scalars().all()]


class SessionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, *, user_id: UUID, tenant_id: UUID, refresh_token: str,
                     amr: list[str], ttl_seconds: int, user_agent: str | None = None) -> Session:
        row = Session(
            user_id=user_id, tenant_id=tenant_id, refresh_hash=_sha256(refresh_token),
            amr=amr, user_agent=user_agent,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds))
        self.session.add(row)
        await self.session.flush()
        return row

    async def get_active_by_refresh(self, refresh_token: str) -> Session | None:
        res = await self.session.execute(
            select(Session).where(
                Session.refresh_hash == _sha256(refresh_token),
                Session.revoked.is_(False),
                Session.expires_at > datetime.now(timezone.utc)))
        return res.scalar_one_or_none()

    async def rotate(self, sess: Session, new_refresh_token: str) -> None:
        """Refresh-token rotation: bind the new token to the same session row."""
        sess.refresh_hash = _sha256(new_refresh_token)

    async def revoke(self, sess: Session) -> None:
        sess.revoked = True

    async def revoke_all_for_user(self, user_id: UUID) -> None:
        """Reuse detection → nuke every live session for the user (Phase 3)."""
        res = await self.session.execute(
            select(Session).where(Session.user_id == user_id, Session.revoked.is_(False)))
        for s in res.scalars().all():
            s.revoked = True
