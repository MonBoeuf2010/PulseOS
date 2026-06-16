"""LifeIQ API entrypoint (modular monolith; modules = future services, Phase 2.5)."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import get_settings
from app.core.ratelimit import limiter
from app.api.v1.router import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # In dev, create the schema on startup so the app runs without a separate
    # migration step. In prod (env != development) schema is owned by Alembic.
    if settings.env == "development":
        from app.core.bootstrap import init_db
        await init_db()
    yield
    # shutdown: drain connections (engine disposed by process exit)


# In production, hide the interactive API explorer and schema so the full API
# surface isn't published to anyone who hits the URL. Kept on in dev for convenience.
_is_prod = settings.env != "development"
app = FastAPI(title="LifeIQ API", version="1.0.0", lifespan=lifespan,
              docs_url=None if _is_prod else "/docs",
              redoc_url=None if _is_prod else "/redoc",
              openapi_url=None if _is_prod else "/openapi.json")

# Rate limiting: register the limiter + 429 handler, and the middleware that
# applies per-route @limiter.limit() decorators (Step 5.3).
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Prometheus metrics. Exposed only in dev — in production the raw /metrics
# endpoint would leak internal stats to anyone, so it's mounted behind the same
# dev gate. Wire it to an authenticated/internal route if you need prod metrics.
if not _is_prod:
    app.mount("/metrics", make_asgi_app())
app.include_router(api_router, prefix="/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.env}
