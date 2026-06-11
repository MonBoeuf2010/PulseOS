# PulseOS — Launch Playbook

Everything is built and verified. This is the **exact, in-order** checklist to go
live. The only thing that genuinely requires *you* (and can't be automated) is
creating accounts and pasting keys: **a Stripe payout account**, a domain, an
Anthropic key, an AdSense account, and an Apple Developer account.

Legend: 🟢 = you do it (account/keys), ⚙️ = a command to run.

---

## Part A — Deploy the backend (so the web + iOS app have something to talk to)

You need one small Linux server (Hetzner/DigitalOcean, ~$12–20/mo) and a domain.

1. 🟢 **Buy a domain** (e.g. `pulseos.app`). In its DNS, add an **A record**
   `api` → your server's IP. So `api.pulseos.app` points at the box.
2. 🟢 **Create the server** (Ubuntu 22.04+, 2 GB RAM min). SSH in.
3. ⚙️ **Install Docker:** `curl -fsSL https://get.docker.com | sh`
4. ⚙️ **Get the code:** `git clone https://github.com/MonBoeuf2010/PulseOS.git && cd PulseOS/infra`
5. ⚙️ **Make the env file:** `cp .env.example .env` then edit `.env`:
   - `ENV=production`
   - `SECRET_KEY=` → run `openssl rand -hex 32` and paste it
   - `POSTGRES_PASSWORD=` and `RABBITMQ_PASSWORD=` → strong random values
   - `DATABASE_URL=postgresql+asyncpg://pulse:<POSTGRES_PASSWORD>@db:5432/pulseos`
   - `ANTHROPIC_API_KEY=` → from console.anthropic.com (this powers the AI)
   - Stripe + AdSense keys come in Parts C and D — leave blank for now.
6. ⚙️ **Launch everything (DB, API, workers, TLS):**
   ```
   API_DOMAIN=api.pulseos.app docker compose -f docker-compose.prod.yml --env-file .env up -d --build
   ```
   Caddy fetches a real HTTPS certificate automatically. The API runs its DB
   migrations on boot.
7. ✅ **Verify:** open `https://api.pulseos.app/health` → `{"status":"ok"}`.

> Migrations, the daily AI briefing scheduler, post moderation, and hourly RSS
> ingestion all start automatically (the `worker` + `beat` containers).

---

## Part B — Deploy the web app (Vercel, free, 5 minutes)

The web app is the product *and* the basis for the iOS app, so deploy it first.

1. 🟢 Go to **vercel.com**, "Add New Project", import the GitHub repo.
2. Set **Root Directory** = `frontend`.
3. Add environment variables:
   - `NEXT_PUBLIC_API_BASE=https://api.pulseos.app`  ← API origin, **no** `/v1`
   - `NEXT_PUBLIC_ADSENSE_CLIENT=` (fill in Part D)
4. Deploy. You get a URL like `pulseos.vercel.app` (point your root domain at it
   later). Put this URL in the backend `.env` as `FRONTEND_BASE_URL=` and
   `CORS_ORIGINS` (so Stripe redirects + browser calls work), then
   `docker compose ... up -d` again.

---

## Part C — Turn on payments (this is your "payment recipient")

1. 🟢 Create a **Stripe account** (stripe.com) and complete **payout/bank setup**
   in Settings → Payouts. *(This is the recipient you mentioned — Stripe pays
   your bank.)*
2. 🟢 **Products → add product:**
   - "PulseOS Basic" → recurring **$5/month** → copy the **price ID** (`price_…`).
   - "PulseOS Pro" → recurring **$15/month**, and add a yearly price too → copy both IDs.
3. 🟢 **Developers → API keys** → copy the **Secret key** (`sk_live_…`).
4. 🟢 **Developers → Webhooks → Add endpoint:**
   `https://api.pulseos.app/v1/billing/webhook` — select events
   `checkout.session.completed`, `customer.subscription.updated`,
   `customer.subscription.deleted` → copy the **signing secret** (`whsec_…`).
5. ⚙️ Put these in the backend `.env`:
   ```
   STRIPE_SECRET_KEY=sk_live_...
   STRIPE_WEBHOOK_SECRET=whsec_...
   STRIPE_PRICE_BASIC=price_...
   STRIPE_PRICE_MONTHLY=price_...   # Pro monthly
   STRIPE_PRICE_YEARLY=price_...    # Pro yearly
   ```
   then `docker compose ... up -d` again. The "Upgrade" page now opens real
   Stripe Checkout; the webhook flips users to Pro automatically.

---

## Part D — Turn on ad revenue (Basic tier is ad-supported)

1. 🟢 Create a **Google AdSense** account (adsense.google.com), add your web
   domain, and wait for approval (can take days — start early).
2. 🟢 Copy your **publisher ID** (`ca-pub-…`).
3. Set `NEXT_PUBLIC_ADSENSE_CLIENT=ca-pub-...` in Vercel and redeploy.
   - Ads show only to **free + Basic** users; **Pro is ad-free** automatically.
   - Until AdSense is approved, a tasteful "Go ad-free with Pro" house upsell
     shows in the ad slots, so nothing looks broken.

---

## Part E — Ship the iOS app (Apple Developer)

The fastest App-Store-legitimate path is to wrap the existing web app in a
**Capacitor** native shell and add a couple of native touches so it isn't a
"thin wrapper" (Apple guideline 4.2). Plan ~1–2 days.

### E1. Enroll (do this first — approval takes 24–48h)
1. 🟢 Go to **developer.apple.com/programs**, enroll in the **Apple Developer
   Program** ($99/year). You need an Apple ID and, for a company, a D-U-N-S number.
2. 🟢 Install **Xcode** from the Mac App Store (you're on macOS — good).

### E2. Create the native shell (Capacitor wraps your web app)
Run these in the repo (`frontend/` is the web app):
```
cd frontend
npm i @capacitor/core @capacitor/cli @capacitor/ios
npx cap init "PulseOS" "app.pulseos.mobile" --web-dir=public
npx cap add ios
```
Point the shell at your live web app — in `capacitor.config.ts` set:
```
server: { url: "https://pulseos.vercel.app", cleartext: false }
```
(This loads your deployed web UI inside the native app.)

### E3. Make it pass review (avoid the "just a website" rejection)
- Add **native push notifications** (`@capacitor/push-notifications`) and wire
  them to the daily briefing — this is a real native feature reviewers like.
- Add a proper **app icon + splash screen** (`npx @capacitor/assets generate`).
- Add **Sign in with Apple** if you offer social login (required when you have
  third-party login; you currently use email/password, so this is optional).
- **In-app purchases:** ⚠️ Apple requires digital subscriptions to use **Apple
  IAP** (StoreKit), *not* Stripe, inside the iOS app (15–30% fee). **The backend
  is already wired for this** via a RevenueCat webhook (`/v1/iap/webhook`) — the
  same `Subscription` row flips to ad-free Pro for both Stripe (web) and IAP (iOS).
  To turn it on:
  1. 🟢 Create a **RevenueCat** account (free), add your App Store app + the IAP
     subscription products, and copy the API key.
  2. In the iOS app add the RevenueCat SDK and call `Purchases.logIn(<your user
     UUID>)` — **use the same user UUID as the backend** (the app_user_id the
     webhook reads; one id everywhere, no guessing).
  3. 🟢 RevenueCat → Integrations → Webhooks: URL `https://<api-domain>/v1/iap/webhook`,
     set the Authorization header to a secret and put the same value in
     `REVENUECAT_WEBHOOK_AUTH` in the backend `.env`.
  - Recommended sequencing: launch **web + Stripe today**; add the iOS IAP flow
    (steps above) when you submit the app — no backend changes needed.

### E4. Build, test, submit
1. ⚙️ `npx cap open ios` → opens Xcode.
2. In Xcode: set your **Team** (your Apple Developer account), a unique **Bundle
   ID** (`app.pulseos.mobile`), and bump the version.
3. 🟢 In **App Store Connect** (appstoreconnect.apple.com): create the app
   record, fill in name, description, screenshots (use the iOS Simulator),
   privacy policy URL, and the **App Privacy** questionnaire (declare: account
   email, usage data; no tracking unless AdSense → declare ads).
4. ⚙️ In Xcode: **Product → Archive → Distribute App → App Store Connect**.
5. 🟢 Test via **TestFlight** (Apple emails you a link). Then **Submit for
   Review**. First review is typically 1–3 days.

### E5. Common rejection triggers (pre-empt them)
- "App is a web wrapper" → solved by E3 (push + native polish).
- "Purchases bypass IAP" → don't sell or link to web purchases *inside* the iOS
  app (see E3).
- "Privacy questionnaire mismatch" → declare AdSense ads + email collection.
- Provide a **demo account** in the review notes (the reviewer must log in).

---

## One-screen summary
1. **A** — `docker compose -f infra/docker-compose.prod.yml up -d` on a VPS → API live with HTTPS.
2. **B** — Import `frontend/` to Vercel, set `NEXT_PUBLIC_API_BASE` → web live.
3. **C** — Stripe: products + keys + webhook → payments live, money to your bank.
4. **D** — AdSense publisher ID → Basic-tier ad revenue live.
5. **E** — Apple Developer ($99) → Capacitor shell → push + icon → TestFlight → submit.

Web + payments can be live **today**. iOS follows once Apple approves (~a few days).
