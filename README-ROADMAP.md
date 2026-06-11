# PulseOS — Launch Roadmap (what's missing, why, and in what order)

Your repo already works end-to-end in dev: auth, the 7-agent council, AI chat,
briefings, a basic feed, posting, search. What's below is ONLY what's missing
to make it a real, automated, paid product — in the order you should do it.

---

## Step 1 — Feed ranking algorithm  (≈30 min)  → `PATCH-1-feed-ranking.md`
**What:** Replace newest-first with score = (engagement + quality) / time-decay,
personalized per viewer. Code: `backend/app/feed/ranking.py`.
**Why first:** It's the cheapest change with the biggest user-facing effect —
the feed instantly feels alive instead of being a chronological dump.

## Step 2 — Full automation  (≈1 hour)  → `PATCH-2-automation.md`
**What:** (a) fill in `schedule_briefings` so the AI council runs for every
user daily at 06:00 with zero clicks; (b) AI moderation agent screens every
new post; (c) an RSS connector so briefings use REAL signals, not seed data.
**Why:** This is the "automated by agents" part of your vision. Right now the
beat schedule fires into an empty stub — agents only run when a user clicks.
After this patch the product produces value while everyone sleeps.

## Step 3 — File uploads with privacy  (≈1–2 hours)  → `backend/app/api/v1/uploads.py`
**What:** Users attach files (images, PDFs, CSVs) to posts. Privacy by design:
explicit file-picker consent only (the app never reads their device), strict
type/size allow-list, UUID filenames (no PII leakage), owner-only deletion,
true erasure (bytes + DB row), ownership check before a file can be published.
**Why:** This is your "access to their files to post" requirement, done the
GDPR-compliant way. Frontend side: a simple `<input type="file">` that POSTs
to `/api/v1/uploads`, then includes the returned IDs in the post payload.

## Step 4 — Stripe subscriptions  (≈half a day)  → `backend/app/api/v1/billing.py`
**What:** Checkout (Stripe-hosted payment page), webhook (the source of truth
that flips a user to premium), customer portal (cancel/update card with zero
UI work), and a one-line `require_premium` dependency to paywall any endpoint.
**Why this design:** card data never touches your server → no PCI burden, and
the signed webhook means nobody can fake being premium. The file's header has
the exact Stripe Dashboard setup checklist (products, prices, webhook secret).
**What to paywall:** council deep-dives, unlimited chat, attachments > N/month
— mirror your DreamDecode model: generous free tier, premium = the AI depth.

## Step 5 — Production hardening (before real users, ≈1 day)
These aren't features but launch blockers:
1. **Alembic migrations** — dev uses `create_all`, which can't evolve a live
   DB. `pip install alembic`, `alembic init`, autogenerate from your models.
   Why: the day you add a column with paying users, you need migrations.
2. **Postgres RLS or enforced tenant filters** — the feed is intentionally
   cross-tenant; everything else must stay tenant-scoped at the DB level.
3. **Rate limiting** (slowapi or nginx) on /auth and /chat — bots will find
   you within days of launch; AI endpoints burn real money per call.
4. **Anthropic spend cap + per-user daily caps** — you already did exactly
   this pattern for DreamDecode's Edge Functions; replicate it here so one
   abusive user can't drain your API budget.
5. **Deploy:** the docker-compose already defines the stack. Cheapest path:
   one VPS (Hetzner/DO ~$20/mo) running compose + Caddy for TLS; managed
   Postgres when revenue justifies it.

## Step 6 — Later (deliberately NOT now)
- OpenSearch hybrid/vector search (Postgres lexical fallback is fine < 50K users)
- WebAuthn passkeys (password + refresh rotation is adequate at launch)
- Offline calibration fitting (needs months of outcome data first)

---

### The one-sentence version
Ranking makes it feel good → automation makes it valuable without you →
uploads make posting rich and private → Stripe makes it a business →
hardening keeps it alive. Each patch file tells you exactly which lines to
add and where.
