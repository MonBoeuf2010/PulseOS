# LifeIQ — Launch on Apple Developer **without a domain**

This is the no-domain path: the iOS app **bundles the web UI inside the app**
(so the UI needs no website/domain), and talks to a backend hosted on a **free
Render subdomain** (`*.onrender.com` — a free URL, not a domain you buy). The
only secret you supply is your **Anthropic API key**.

Legend: 🟢 = you do it (account / paste a key / click) · ⚙️ = a command · ✅ = a check.

**What you need**
- An **Apple Developer Program** membership ($99/yr) — the one unavoidable cost.
- An **Anthropic API key** (`sk-ant-…`) from console.anthropic.com.
- A **GitHub account** (the repo `MonBoeuf2010/PulseOS` is already pushed).
- **Xcode** (Mac App Store) — you're on macOS, good.
- A **Render** account (free) — render.com, sign in with GitHub.

The repo is already prepared:
- `render.yaml` — one-click backend deploy (API + free Postgres + free Redis).
- `frontend/.env.production` — points the app at `https://pulseos-api.onrender.com`.
- The iOS bundle in `frontend/ios/` is already built against that URL.
- Bundle ID: `com.abcquickapps.lifeiq` · App name: **LifeIQ**.

---

## Part 1 — Deploy the backend to Render (free, ~10 min)

1. 🟢 Go to **render.com** → sign up / log in **with GitHub**. Authorize Render
   to see the `PulseOS` repo.
2. 🟢 Dashboard → **New +** → **Blueprint**.
3. 🟢 Pick the **`MonBoeuf2010/PulseOS`** repo. Render reads `render.yaml` and
   shows it will create: a **web service** (`pulseos-api`), a **Postgres** db
   (`pulseos-db`), and a **Redis/Key Value** (`pulseos-redis`).
4. 🟢 It will prompt for the one secret env var: **`ANTHROPIC_API_KEY`** → paste
   your `sk-ant-…` key. (Everything else is wired automatically.)
5. 🟢 Click **Apply**. First build takes ~5–8 min (Docker build + DB migrations
   run automatically on boot).
6. ✅ When `pulseos-api` is **Live**, open its URL — it'll be
   **`https://pulseos-api.onrender.com`** — and visit **`/health`**. You want:
   ```json
   {"status":"ok","env":"production"}
   ```
   Also `…/docs` shows the live API. **That's your backend — no domain, valid HTTPS.**

> **If Render gives the service a different URL** (e.g. the name `pulseos-api`
> was taken and it became `pulseos-api-x7q2.onrender.com`): copy the real URL,
> paste it into `frontend/.env.production` as `NEXT_PUBLIC_API_BASE=…` (origin
> only, no `/v1`), then rebuild the app bundle:
> ```
> cd frontend && npm run build && npx cap sync ios
> ```

> **If `type: redis` is rejected** in the blueprint preview, edit `render.yaml`:
> change the two `redis` lines to `keyvalue` (Render renamed the product) and
> re-apply. Nothing else changes.

### Free-tier facts to know
- The free web service **sleeps after ~15 min idle**; the next request wakes it
  in ~30 s. Fine for testing and launch. To kill the sleep later, change
  `plan: free` → `plan: starter` ($7/mo) in `render.yaml`.
- Free Postgres is **free for 30 days**, then needs a paid plan ($7/mo) — or
  swap in a free, non-expiring Postgres (Neon/Supabase, both support pgvector)
  by setting `DATABASE_URL` on the service by hand.
- Background jobs (scheduled daily briefings, RSS ingest, async post moderation)
  are **off** — they need an always-on worker (paid). **Everything the user
  touches works without them**: register/login, dashboard, on-demand briefings,
  AI chat, the council, the feed. Turn them on later by adding a Render
  Background Worker and setting `ENABLE_BACKGROUND_JOBS=true`.

---

## Part 2 — The iOS app is already pointed at your backend

Nothing to do here unless your Render URL differs from the default (see the box
above). The app's bundled web UI was built with
`NEXT_PUBLIC_API_BASE=https://pulseos-api.onrender.com` and synced into
`frontend/ios/`. The native shell loads that bundled UI and calls your Render API.

To re-verify at any time:
```
cd frontend
grep -rl "pulseos-api.onrender.com" ios/App/App/public/_next   # should list a file
```

---

## Part 3 — Build & ship the app (Apple Developer)

### 3.1 Enroll (do first — approval can take 24–48 h)
1. 🟢 **developer.apple.com/programs** → enroll in the **Apple Developer Program**
   ($99/yr). Personal (individual) enrollment is fastest — no D-U-N-S needed.
2. 🟢 Open **Xcode** once and sign in: **Xcode → Settings → Accounts → +** →
   add your Apple ID.

### 3.2 Open the project in Xcode
```
cd /Users/monboeuf/PulseOS/frontend
npx cap open ios
```
This opens `ios/App/App.xcworkspace` in Xcode.

### 3.3 Set signing
1. 🟢 In Xcode, select the **App** target → **Signing & Capabilities**.
2. 🟢 Set **Team** = your Apple Developer account.
3. 🟢 **Bundle Identifier** = `com.abcquickapps.lifeiq` (must be globally unique —
   if Apple says it's taken, change it here *and* in
   `frontend/capacitor.config.ts` → `appId`, then `npx cap sync ios`).
4. 🟢 Leave **Automatically manage signing** checked — Xcode creates the
   provisioning profile for you.

### 3.4 Run on your own iPhone (smoke test)
1. 🟢 Plug in your iPhone, select it as the run target, press **▶︎ Run**.
2. 🟢 First run: on the iPhone, **Settings → General → VPN & Device Management**
   → trust your developer cert.
3. ✅ The app launches → **Create account** → you land on the dashboard and the
   AI chat works (it's calling your Render backend). If the first action is slow,
   that's the free dyno waking up (~30 s) — only the first hit after idle.

### 3.5 Ship to TestFlight (and App Store)
1. 🟢 In Xcode, set the run destination to **Any iOS Device (arm64)**.
2. ⚙️ **Product → Archive**. When it finishes, the Organizer opens.
3. 🟢 **Distribute App → App Store Connect → Upload**.
4. 🟢 Go to **appstoreconnect.apple.com → My Apps → +** → **New App**:
   - Platform iOS · Name **LifeIQ** · Bundle ID `com.abcquickapps.lifeiq` ·
     pick a primary language and SKU.
5. 🟢 Your build appears under **TestFlight** in a few minutes (after Apple
   processes it). Add yourself as an **Internal Tester** → install via the
   **TestFlight** app on your iPhone. **This is the finish line for "launch it
   for me."**
6. 🟢 *(Public release)* To submit to the App Store, fill in: description,
   screenshots (capture from the iOS Simulator or your device), the **App
   Privacy** questionnaire (declare: account email + usage data; ads only if you
   later enable AdSense), and **provide a demo account** in the review notes —
   register one in the app and paste those credentials so the reviewer can log
   in. Then **Submit for Review** (typically 1–3 days).

---

## Optional hardening (only for public App Store release)

- **Avoid the "it's just a website" rejection (Guideline 4.2).** The app already
  has a native splash/icon and runs a bundled (not remote-loaded) UI, which
  helps. The strongest single addition is **native push notifications** tied to
  the daily briefing (`@capacitor/push-notifications`). Not required for
  TestFlight or to use the app yourself.
- **In-App Purchases.** Apple requires digital subscriptions sold *inside* the
  iOS app to use Apple IAP, not Stripe. The backend is already wired for this via
  a RevenueCat webhook (`/v1/iap/webhook`). To enable: create a free RevenueCat
  account + your subscription product, set `NEXT_PUBLIC_REVENUECAT_IOS_KEY` in
  `frontend/.env.production` and `REVENUECAT_WEBHOOK_AUTH` on the Render service,
  rebuild (`npm run build && npx cap sync ios`). Until then the app ships with no
  in-app purchases, which is fine for review.

---

## One-screen summary
1. **Render** → New → Blueprint → pick the repo → paste `ANTHROPIC_API_KEY` →
   Apply → check `https://pulseos-api.onrender.com/health`.
2. App is already built against that URL (rebuild only if your URL differs).
3. **Xcode**: `npx cap open ios` → set Team + Bundle ID → Run on your iPhone.
4. **Archive → Upload → TestFlight** → install on your phone. Done.

**No domain anywhere. One key (Anthropic). One bundle. $0 hosting + $99 Apple.**

---

## Troubleshooting
- **App opens but every call fails / "network error":** the Render service is
  asleep (first hit takes ~30 s) or the URL baked into the app doesn't match the
  live Render URL. Re-check Part 1's box and rebuild.
- **`/health` 404 or build failed on Render:** open the `pulseos-api` **Logs**.
  A migration failure usually means the Postgres add-on isn't attached — confirm
  all three resources were created by the Blueprint.
- **Login works but AI replies are generic/stubbed:** `ANTHROPIC_API_KEY` isn't
  set on the service (the app falls back to a deterministic offline stub). Set it
  in the service's **Environment** and redeploy.
- **CORS error in the WebView console:** the app's origin is
  `capacitor://localhost`; make sure that's still in `CORS_ORIGINS` on the
  service (it's set by `render.yaml`).
