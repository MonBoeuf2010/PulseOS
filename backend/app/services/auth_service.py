"""AuthService — registration, password login, and rotating-refresh sessions (Phase 3).

Identity lives outside any single tenant, so we open sessions WITHOUT an RLS tenant
context (`tenant_session(None)`). Tokens: short-lived access JWT + opaque rotating
refresh token whose sha256 is stored server-side for reuse detection / revocation.
"""
from __future__ import annotations

import secrets
from uuid import UUID

from fastapi import HTTPException, status

from app.core.config import get_settings
from app.core.db import tenant_session
from app.core.security import hash_password, issue_access_token, verify_password
from app.repositories.users import SessionRepository, UserRepository
from app.schemas import TokenPair

settings = get_settings()


def _new_refresh_token() -> str:
    return secrets.token_urlsafe(48)


class AuthService:
    async def register(self, *, email: str, password: str, display_name: str | None,
                       tenant_name: str | None, user_agent: str | None = None) -> TokenPair:
        async with tenant_session(None) as session:
            users = UserRepository(session)
            if await users.get_by_email(email):
                raise HTTPException(status.HTTP_409_CONFLICT, "email already registered")
            user, tenant, membership = await users.create_user_with_tenant(
                email=email, password_hash=hash_password(password),
                display_name=display_name, tenant_name=tenant_name)
            return await self._issue(session, user_id=user.id, tenant_id=tenant.id,
                                     roles=[membership.role], amr=["pwd"], user_agent=user_agent)

    async def login(self, *, email: str, password: str,
                    user_agent: str | None = None) -> TokenPair:
        async with tenant_session(None) as session:
            users = UserRepository(session)
            user = await users.get_by_email(email)
            # Constant-ish work + uniform error to avoid user enumeration.
            if user is None or not user.password_hash or not verify_password(password, user.password_hash):
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid credentials")
            if user.status != "active":
                raise HTTPException(status.HTTP_403_FORBIDDEN, "account not active")
            memberships = await users.memberships(user.id)
            if not memberships:
                raise HTTPException(status.HTTP_403_FORBIDDEN, "no tenant membership")
            primary = memberships[0]
            return await self._issue(session, user_id=user.id, tenant_id=primary.tenant_id,
                                     roles=[primary.role], amr=["pwd"], user_agent=user_agent)

    async def refresh(self, *, refresh_token: str) -> TokenPair:
        async with tenant_session(None) as session:
            sessions = SessionRepository(session)
            sess = await sessions.get_active_by_refresh(refresh_token)
            if sess is None:
                # Token unknown/expired/already-rotated → possible reuse. Caller must re-auth.
                raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid refresh token")
            roles = await UserRepository(session).roles_for(sess.user_id, sess.tenant_id)
            new_refresh = _new_refresh_token()
            await sessions.rotate(sess, new_refresh)
            access = issue_access_token(
                user_id=sess.user_id, tenant_id=sess.tenant_id, roles=roles or ["member"],
                scopes=[], amr=list(sess.amr or []), session_id=sess.id)
            return TokenPair(access_token=access, refresh_token=new_refresh,
                             expires_in=settings.access_token_ttl_seconds,
                             tenant_id=sess.tenant_id, user_id=sess.user_id)

    async def logout(self, *, refresh_token: str) -> None:
        async with tenant_session(None) as session:
            sessions = SessionRepository(session)
            sess = await sessions.get_active_by_refresh(refresh_token)
            if sess is not None:
                await sessions.revoke(sess)

    async def _issue(self, session, *, user_id: UUID, tenant_id: UUID, roles: list[str],
                     amr: list[str], user_agent: str | None) -> TokenPair:
        sessions = SessionRepository(session)
        refresh = _new_refresh_token()
        sess = await sessions.create(
            user_id=user_id, tenant_id=tenant_id, refresh_token=refresh, amr=amr,
            ttl_seconds=settings.refresh_token_ttl_seconds, user_agent=user_agent)
        access = issue_access_token(user_id=user_id, tenant_id=tenant_id, roles=roles,
                                    scopes=[], amr=amr, session_id=sess.id)
        return TokenPair(access_token=access, refresh_token=refresh,
                         expires_in=settings.access_token_ttl_seconds,
                         tenant_id=tenant_id, user_id=user_id)
