FROM python:3.12-slim AS base
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1
WORKDIR /app

# System deps (build tools for native wheels; removed in final layer)
RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install -e .

COPY . .

# Non-root runtime user (security baseline). Pre-create the uploads dir so a
# mounted named volume inherits appuser ownership and stays writable.
RUN useradd -m -u 10001 appuser \
    && mkdir -p /data/uploads \
    && chown -R appuser /app /data/uploads
USER appuser

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:8000/health || exit 1
# In prod the schema is owned by Alembic — apply migrations, then serve.
# (--proxy-headers: trust X-Forwarded-* from the Caddy TLS terminator in front.)
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers"]
