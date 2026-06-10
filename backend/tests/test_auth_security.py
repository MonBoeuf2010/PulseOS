"""AuthN primitives + token lifecycle (no DB needed — stub key signing)."""
from uuid import uuid4

import pytest

from app.core.security import (Role, abac_permit, hash_password, issue_access_token,
                               role_permits, verify_access_token, verify_password, Subject, Resource)


def test_password_hash_roundtrip():
    h = hash_password("correct horse battery staple")
    assert h != "correct horse battery staple"
    assert verify_password("correct horse battery staple", h)
    assert not verify_password("wrong", h)


def test_access_token_roundtrip():
    uid, tid, sid = uuid4(), uuid4(), uuid4()
    tok = issue_access_token(user_id=uid, tenant_id=tid, roles=["owner"], scopes=[],
                             amr=["pwd"], session_id=sid)
    claims = verify_access_token(tok)
    assert claims["sub"] == str(uid) and claims["tid"] == str(tid)
    assert claims["roles"] == ["owner"] and claims["iss"] == "pulseos"


def test_rbac_wildcards():
    assert role_permits([Role.OWNER], "anything:at:all")
    assert role_permits([Role.MEMBER], "memory:read")        # family wildcard memory:*
    assert not role_permits([Role.VIEWER], "memory:write")   # viewer is read-only


def test_abac_blocks_cross_tenant():
    a, b = uuid4(), uuid4()
    subj = Subject(user_id=uuid4(), tenant_id=a, roles=["owner"], attributes={})
    res = Resource(type="briefing", tenant_id=b)
    assert not abac_permit(subj, "briefing:read", res)


def test_abac_requires_mfa_for_export():
    t = uuid4()
    subj = Subject(user_id=uuid4(), tenant_id=t, roles=["owner"], attributes={}, mfa_level=0)
    res = Resource(type="data", tenant_id=t)
    assert not abac_permit(subj, "data:export", res)          # step-up required
