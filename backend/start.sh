#!/bin/sh
# Production start-up for Render (and any container host).
# Kept as a script so the run command is a single, unambiguous token
# (/app/start.sh) that no shell can mis-parse — the `&&` and ${PORT}
# expansion live safely inside this file instead of in a quoted one-liner.
set -e

echo "==> Applying database migrations (alembic upgrade head)"
python -m alembic upgrade head

echo "==> Starting API server on port ${PORT:-8000}"
exec python -m uvicorn app.main:app \
  --host 0.0.0.0 \
  --port "${PORT:-8000}" \
  --proxy-headers
