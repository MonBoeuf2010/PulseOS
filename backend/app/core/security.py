"""AuthN/AuthZ primitives: password hashing (Argon2id), JWT issuance/verification,
and the RBAC/ABAC policy decision point. See docs/phase-3/security-architecture.md."""
from __future__ import annotations

import time
from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import get_settings

settings = get_settings()
_ph = PasswordHasher()  # Argon2id, memory-hard


# ---------- Passwords ----------
def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(password: str, hashed: str) -> bool:
    try:
        return _ph.verify(hashed, password)
    except VerifyMismatchError:
        return False


# ---------- JWT ----------
def issue_access_token(*, user_id: UUID, tenant_id: UUID, roles: list[str],
                       scopes: list[str], amr: list[str], session_id: UUID) -> str:
    now = int(time.time())
    payload = {
        "sub": str(user_id), "tid": str(tenant_id), "roles": roles, "scopes": scopes,
        "amr": amr, "sid": str(session_id), "iat": now,
        "exp": now + settings.access_token_ttl_seconds, "iss": "lifeiq",
    }
    return jwt.encode(payload, settings.jwt_private_key_pem or settings.secret_key,
                      algorithm=settings.jwt_alg if settings.jwt_private_key_pem else "HS256")


def verify_access_token(token: str) -> dict:
    key = settings.jwt_public_key_pem or settings.secret_key
    alg = settings.jwt_alg if settings.jwt_public_key_pem else "HS256"
    return jwt.decode(token, key, algorithms=[alg], issuer="lifeiq")


# ---------- RBAC ----------
class Role(StrEnum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


# Permission sets per role (additive). Deny-by-default everywhere else.
ROLE_PERMISSIONS: dict[str, set[str]] = {
    Role.OWNER: {"*"},
    Role.ADMIN: {"briefing:*", "member:invite", "moderation:decide", "audit:read",
                 "meeting:*", "billing:manage", "company:manage"},
    Role.MEMBER: {"briefing:read", "opportunity:*", "memory:*", "report:create",
                  "meeting:create", "search:read"},
    Role.VIEWER: {"briefing:read", "search:read"},
}


def role_permits(roles: list[str], permission: str) -> bool:
    granted: set[str] = set()
    for r in roles:
        granted |= ROLE_PERMISSIONS.get(r, set())
    if "*" in granted or permission in granted:
        return True
    # wildcard family match e.g. "briefing:*" permits "briefing:read"
    family = permission.split(":")[0] + ":*"
    return family in granted


# ---------- ABAC ----------
@dataclass(frozen=True)
class Subject:
    user_id: UUID
    tenant_id: UUID
    roles: list[str]
    attributes: dict           # dept, clearance, mfa_level...
    mfa_level: int = 0


@dataclass(frozen=True)
class Resource:
    type: str
    tenant_id: UUID
    owner_id: UUID | None = None
    visibility: str = "tenant"
    access_policy: dict | None = None
    regulated: bool = False


def abac_permit(subject: Subject, action: str, resource: Resource, env: dict | None = None) -> bool:
    """Centralized policy decision point. Real impl delegates to OPA/Cedar; this is the
    reference policy enforcing tenancy + meeting participant scoping + MFA step-up."""
    env = env or {}
    # 1. Hard tenancy boundary (defense-in-depth with RLS).
    if subject.tenant_id != resource.tenant_id and resource.visibility != "public":
        return False
    # 2. Meeting / data-room participant scoping.
    if resource.type == "meeting" and resource.access_policy:
        participants = set(resource.access_policy.get("participants", []))
        if str(subject.user_id) not in participants:
            return False
        if subject.mfa_level < resource.access_policy.get("required_mfa", 0):
            return False
    # 3. High-risk actions require step-up MFA.
    if action in {"data:export", "data:delete", "billing:manage"} and subject.mfa_level < 1:
        return False
    # 4. Fall through to RBAC for coarse permission.
    return role_permits(subject.roles, action)
