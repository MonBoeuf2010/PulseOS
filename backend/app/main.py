"""PulseOS API entrypoint (modular monolith; modules = future services, Phase 2.5)."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.core.config import get_settings
from app.api.v1.router import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup: warm caches, verify migrations, connect brokers (SCAFFOLD)
    yield
    # shutdown: drain connections


app = FastAPI(title="PulseOS API", version="1.0.0", lifespan=lifespan,
              docs_url="/docs", openapi_url="/openapi.json")

app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.mount("/metrics", make_asgi_app())          # Prometheus
app.include_router(api_router, prefix="/v1")


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.env}
