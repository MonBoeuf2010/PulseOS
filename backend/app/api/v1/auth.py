"""Auth endpoints: login, refresh, MFA, passkeys (Phase 3). Core flows scaffolded."""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr

router = APIRouter()


class LoginIn(BaseModel):
    method: str = "password"
    email: EmailStr | None = None
    password: str | None = None
    provider: str | None = None
    code: str | None = None


class TokenPair(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 900
    mfa_required: bool = False


@router.post("/login", response_model=TokenPair)
async def login(body: LoginIn):
    # SCAFFOLD: verify credential (Argon2id) / OAuth code → issue access+refresh,
    # create session row, set rotating refresh cookie, return mfa_required if step-up needed.
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "wire to AuthService")


@router.post("/refresh", response_model=TokenPair)
async def refresh():
    # SCAFFOLD: rotating refresh-token verification + reuse detection → new access token.
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED, "wire to AuthService")


@router.post("/passkey/login/options")
async def passkey_options():
    # SCAFFOLD: WebAuthn assertion challenge.
    return {"challenge": "...", "rpId": "pulseos.com"}
