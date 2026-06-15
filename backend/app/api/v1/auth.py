"""Auth endpoints: register, login, refresh, logout, passkeys (Phase 3).

Password flows are wired to AuthService. Refresh tokens are returned in the body
for API clients and SHOULD additionally be set as a Secure, HttpOnly, SameSite=Strict
cookie by the edge for browser clients.
"""
from fastapi import APIRouter, Header, Request, Response, status

from app.core.ratelimit import AUTH_LIMIT, limiter
from app.schemas import LoginIn, RefreshIn, RegisterIn, TokenPair
from app.services.auth_service import AuthService

router = APIRouter()
_auth = AuthService()


def _set_refresh_cookie(response: Response, token: str | None, max_age: int) -> None:
    if token:
        response.set_cookie("pulse_rt", token, max_age=max_age, httponly=True,
                            secure=True, samesite="strict", path="/v1/auth")


@router.post("/register", response_model=TokenPair, status_code=status.HTTP_201_CREATED)
@limiter.limit(AUTH_LIMIT)
async def register(request: Request, body: RegisterIn, response: Response,
                   user_agent: str | None = Header(default=None)):
    tokens = await _auth.register(email=body.email, password=body.password,
                                  display_name=body.display_name,
                                  tenant_name=body.tenant_name, user_agent=user_agent)
    _set_refresh_cookie(response, tokens.refresh_token, tokens.expires_in)
    return tokens


@router.post("/login", response_model=TokenPair)
@limiter.limit(AUTH_LIMIT)
async def login(request: Request, body: LoginIn, response: Response,
                user_agent: str | None = Header(default=None)):
    if body.method != "password" or not body.email or not body.password:
        # OAuth / passkey methods are handled by their dedicated routes (R2+).
        from fastapi import HTTPException
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "unsupported login method")
    tokens = await _auth.login(email=body.email, password=body.password, user_agent=user_agent)
    _set_refresh_cookie(response, tokens.refresh_token, tokens.expires_in)
    return tokens


@router.post("/refresh", response_model=TokenPair)
async def refresh(response: Response, request: Request, body: RefreshIn | None = None):
    # Prefer the HttpOnly cookie; fall back to a body token for non-browser clients.
    token = request.cookies.get("pulse_rt") or (body.refresh_token if body else None)
    if not token:
        from fastapi import HTTPException
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "missing refresh token")
    tokens = await _auth.refresh(refresh_token=token)
    _set_refresh_cookie(response, tokens.refresh_token, tokens.expires_in)
    return tokens


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(response: Response, request: Request, body: RefreshIn | None = None):
    token = request.cookies.get("pulse_rt") or (body.refresh_token if body else None)
    if token:
        await _auth.logout(refresh_token=token)
    response.delete_cookie("pulse_rt", path="/v1/auth")


@router.post("/passkey/login/options")
async def passkey_options():
    # SCAFFOLD: WebAuthn assertion challenge (R2 — webauthn dep already declared).
    return {"challenge": "...", "rpId": "lifeiq.com"}
