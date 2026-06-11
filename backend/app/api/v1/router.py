"""Aggregate v1 routers. Each maps to a service boundary (Phase 2.5)."""
from fastapi import APIRouter

from app.api.v1 import (auth, billing, briefings, chat, council, feed, iap, memory,
                        opportunities, search, uploads)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(briefings.router, tags=["briefings"])
api_router.include_router(council.router, prefix="/council", tags=["council"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(feed.router, prefix="/feed", tags=["feed"])
api_router.include_router(opportunities.router, prefix="/opportunities", tags=["opportunities"])
api_router.include_router(memory.router, prefix="/memory", tags=["memory"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(uploads.router, prefix="/uploads", tags=["uploads"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
api_router.include_router(iap.router, prefix="/iap", tags=["iap"])
# R2+: follows, companies, meetings, admin, privacy (same pattern).
