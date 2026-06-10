"""Aggregate v1 routers. Each maps to a service boundary (Phase 2.5)."""
from fastapi import APIRouter

from app.api.v1 import auth, briefings, council, opportunities, memory, search

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(briefings.router, tags=["briefings"])
api_router.include_router(council.router, prefix="/council", tags=["council"])
api_router.include_router(opportunities.router, prefix="/opportunities", tags=["opportunities"])
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
# R2+: community, follows, companies, meetings, billing, admin, privacy (same pattern).
