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


app = FastAPI(title="LifeIQ API", version="1.0.0", lifespan=lifespan,
              docs_url="/docs", openapi_url="/openapi.json")

# Rate limiting: register the limiter + 429 handler, and the middleware that
# applies per-route @limiter.limit() decorators (Step 5.3).
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.mount("/metrics", make_asgi_app())          # Prometheus
app.include_router(api_router, prefix="/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.env}
