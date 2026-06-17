#!/bin/sh
# =============================================================================
# Xcode Cloud — post-clone build step for the LifeIQ Capacitor app.
#
# LifeIQ is a Next.js web app wrapped with Capacitor. Xcode Cloud knows how to
# build the iOS project, but NOT the website inside it. The web build output
# (ios/App/App/public) is gitignored, so we must regenerate it here BEFORE
# Xcode Cloud compiles the iOS app — otherwise the app ships empty.
#
# This file MUST live at: <repo>/frontend/ios/App/ci_scripts/ci_post_clone.sh
# (same folder level as App.xcodeproj). Xcode Cloud runs it automatically.
# =============================================================================
set -e

echo "==> [1/5] Installing Node (LTS)"
brew install node@20
brew link --overwrite --force node@20

# Xcode Cloud clones the repo; locate its root reliably.
REPO_ROOT="${CI_PRIMARY_REPOSITORY_PATH:-$CI_WORKSPACE}"
echo "==> Repo root: $REPO_ROOT"
cd "$REPO_ROOT/frontend"

# The backend URL normally lives in the gitignored .env.production. Recreate it
# so the cloud build points at the live backend (overridable via an Xcode Cloud
# environment variable named NEXT_PUBLIC_API_BASE).
echo "==> [2/5] Writing production env (backend URL)"
echo "NEXT_PUBLIC_API_BASE=${NEXT_PUBLIC_API_BASE:-https://pulseos-api-ghov.onrender.com}" > .env.production

echo "==> [3/5] Installing web dependencies (npm ci)"
npm ci

echo "==> [4/5] Building the web app (next build → static export)"
npm run build

echo "==> [5/5] Syncing web assets into the iOS project (cap sync ios)"
npx cap sync ios

echo "==> Post-clone complete — iOS build can now proceed."
