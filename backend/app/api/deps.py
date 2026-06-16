"""Request dependencies: auth principal extraction, tenant scoping, RBAC/ABAC guards."""
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.db import get_db_for_request
from app.core.security import Subject, verify_access_token, role_permits

_bearer = HTTPBearer(auto_error=True)


async def current_subject(
    creds: HTTPAuthorizationCredentials = Depends(_bearer),
) -> Subject:
    try:
        claims = verify_access_token(creds.credentials)
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "invalid token")
    # Tenant is taken ONLY from the signed token — never from a client-supplied
    # header — so a logged-in user cannot scope their session to another tenant.
    # (Multi-tenant membership switching, if ever needed, must verify membership
    # against the memberships table before trusting any requested tenant id.)
    tenant_id = UUID(claims["tid"])
    return Subject(user_id=UUID(claims["sub"]), tenant_id=tenant_id,
                   roles=claims.get("roles", []), attributes={},
                   mfa_level=1 if "mfa" in claims.get("amr", []) else 0)


async def db(subject: Subject = Depends(current_subject)):
    async for session in get_db_for_request(subject.tenant_id):
        yield session


def require(permission: str):
    async def _guard(subject: Subject = Depends(current_subject)) -> Subject:
        if not role_permits(subject.roles, permission):
            raise HTTPException(status.HTTP_403_FORBIDDEN, f"missing permission: {permission}")
        return subject
    return _guard
