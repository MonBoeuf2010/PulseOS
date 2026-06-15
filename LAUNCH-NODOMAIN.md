# 🚀 Launch LifeIQ — the simple, 100% free guide

Read this top to bottom and do exactly what it says. Every click is spelled out.
Don't skip steps. If something doesn't match perfectly, read the **❓ If you get
stuck** notes at the bottom.

## What you're about to build
- A **backend** (the brain) running free on the internet at a web address like
  `https://pulseos-api.onrender.com`.
- The **iPhone app** that talks to it. The app already has the screens built in —
  it just needs the backend to be live.

## What it costs
- **$0 / month** for hosting. Forever. (We use free plans that don't expire.)
- **$99 / year** to Apple — the *only* unavoidable cost, and only if you want the
  app on your iPhone / the App Store. Apple charges this; nobody can remove it.

## The 4 free accounts you'll make (write down each email/password)
1. **GitHub** — you already have this (your code lives there). ✅
2. **Neon** — the database (stores users, briefings, chats). Free forever.
3. **Render** — runs the backend. Free forever.
4. **Apple Developer** — to put the app on an iPhone. $99/yr.

You'll also paste in your **Anthropic API key** (your AI key, starts with
`sk-ant-`). Get it from **console.anthropic.com → Settings → API Keys** if you
don't have one yet.

Total time: about **30–45 minutes**, most of it waiting for things to build.

---

# PART 1 — Make the database (Neon) · ~5 min

The database is just a place to store data. Neon gives one away free.

1. Open a browser tab → go to **https://neon.tech**.
2. Click **Sign up** (top-right). Choose **Continue with GitHub**. A box pops up
   asking to authorize — click **Authorize**.
3. Neon asks a couple of setup questions and **creates a project for you
   automatically**. If it asks you to name it, type `pulseos` and accept the
   default region and Postgres version. Click **Create**.
4. You'll land on the project **Dashboard**. Look for a box titled
   **Connection string** (sometimes under a **Connect** button).
5. **Important:** if there's a toggle labelled **Connection pooling**, leave it
   **OFF** (un-checked). (It still works if it's on — but off is simplest.)
6. Click the **copy icon** next to the connection string. You just copied
   something that looks like this (yours will differ):
   ```
   postgresql://neondb_owner:AbC123xyz@ep-cool-bird-12345.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
7. **Paste it somewhere safe for a minute** (a Notes window). You'll need it in
   Part 2. ✅ **Part 1 done.**

> You do **not** need to create tables or run anything here. The backend builds
> the database automatically the first time it starts.

---

# PART 2 — Put the backend online (Render) · ~10 min + waiting

1. New browser tab → **https://render.com**.
2. Click **Get Started** / **Sign in** → **GitHub** → **Authorize**.
3. In the Render dashboard, click the **New +** button (top-right) → choose
   **Blueprint**.
4. Render shows your GitHub repositories. Find **`PulseOS`** and click
   **Connect** next to it.
   - If you don't see it: click **"Configure account / Configure GitHub"**, allow
     Render to access the `PulseOS` repo, come back, and it'll appear.
5. Render reads the `render.yaml` file in your repo and shows **one service to
   create: `pulseos-api`**. Below it, it asks you to fill in two values (they're
   marked as needing input):
   - **`DATABASE_URL`** → paste the Neon connection string you copied in Part 1.
   - **`ANTHROPIC_API_KEY`** → paste your `sk-ant-...` key.
6. Click **Apply** (or **Create Services**).
7. Now **wait**. Render downloads, builds, and starts your backend. This takes
   about **5–8 minutes**. You'll see logs scrolling. It's done when the service
   status turns **Live** (green).
8. **Check it worked:** at the top of the `pulseos-api` page is its web address,
   `https://pulseos-api.onrender.com` (or similar). Click it, then add `/health`
   to the end in your browser:
   ```
   https://pulseos-api.onrender.com/health
   ```
   You should see:
   ```json
   {"status":"ok","env":"production"}
   ```
   🎉 **Your backend is live on the internet, for free.** ✅ **Part 2 done.**

> **Did Render give you a different web address?** (e.g. it added random letters
> because `pulseos-api` was taken.) Copy your real address, then do the small fix
> in **❓ If you get stuck → "My Render URL is different"** before Part 3.

> **First click is slow?** Free backends "sleep" after 15 minutes of no use and
> take ~30 seconds to wake up. Normal. Only the first request after a nap is slow.

---

# PART 3 — Put the app on your iPhone (Apple) · the $99 part

You do this on your Mac (the code is already on it at `~/PulseOS`).

## 3A — One-time Apple setup
1. Go to **https://developer.apple.com/programs** → **Enroll**. Sign in with your
   Apple ID and pay the **$99/year**. Choose **Individual** — it's the fastest
   (no company paperwork). Apple may take a few hours to approve. ☕
2. Install **Xcode** from the **Mac App Store** (it's big — let it download).
3. Open Xcode once. Top menu: **Xcode → Settings → Accounts → the “+” button →
   Apple ID** → sign in with the same Apple ID.

## 3B — Open the app project
1. Open the **Terminal** app on your Mac.
2. Copy-paste these two lines, pressing Return after each:
   ```
   cd ~/PulseOS/frontend
   npx cap open ios
   ```
   This opens your app in Xcode. (First time it may ask to install tools — say
   yes.)

## 3C — Tell Xcode it's your app
1. In Xcode's left sidebar, click the blue **App** icon at the very top.
2. Click the **Signing & Capabilities** tab.
3. **Team**: pick your name / Apple Developer account from the dropdown.
4. **Bundle Identifier**: it's `com.abcquickapps.lifeiq`. If Xcode shows a red
   error saying it's already taken, change it to something unique like
   `com.YOURNAME.lifeiq` (lowercase, no spaces).
5. Make sure **"Automatically manage signing"** is checked. Xcode handles the
   rest.

## 3D — Run it on your iPhone
1. Plug your iPhone into the Mac with a cable. Unlock the phone. If it asks
   **"Trust this computer?"** tap **Trust**.
2. At the top of Xcode, where it shows a device name, pick **your iPhone**.
3. Click the **▶︎ (Play)** button. Xcode builds and installs the app.
4. First time only: on your iPhone go to **Settings → General → VPN & Device
   Management → (your Apple ID) → Trust**. Then tap the app icon again.
5. The app opens → tap **"No account? Create one"** → make an account → you're in.
   Try the AI chat. (If the very first thing is slow, that's the backend waking
   up — wait ~30s.) 🎉 **The app works on your phone.**

**If your goal was "use it on my own iPhone," you're done here.** ✅

## 3E — (Optional) Share it / put it on the App Store
1. In Xcode, change the device selector (top) to **"Any iOS Device (arm64)"**.
2. Menu: **Product → Archive**. Wait for it to finish; a window opens.
3. Click **Distribute App → App Store Connect → Upload**. Follow the prompts.
4. Go to **https://appstoreconnect.apple.com → My Apps → “+” → New App**. Fill in:
   app name (**LifeIQ**), language, the same Bundle ID, and an SKU (any text like
   `lifeiq01`).
5. Under the **TestFlight** tab, after Apple finishes processing (a few minutes),
   add yourself as an **Internal Tester**. Install the **TestFlight** app on your
   iPhone from the App Store to test it like a real download.
6. To go fully public: fill in description + screenshots + the **App Privacy**
   questions (say you collect *email* and *usage data*; no tracking), add a
   **demo account** in the review notes (make one in the app and write the
   email/password so Apple's reviewer can log in), then **Submit for Review**.
   Apple usually replies in 1–3 days.

---

# ❓ If you get stuck

**"My Render URL is different from `pulseos-api.onrender.com`."**
The app was built pointing at the default address. Point it at yours:
1. Terminal:
   ```
   cd ~/PulseOS/frontend
   open -e .env.production
   ```
2. Change the `NEXT_PUBLIC_API_BASE=` line to your real Render address (the part
   ending in `.onrender.com`, no slash at the end). Save and close.
3. Run:
   ```
   npm run build && npx cap sync ios
   ```
4. Go back to Xcode and Run again (Part 3D).

**`/health` doesn't load / shows an error.**
- Wait a minute and refresh — the backend may still be starting or waking up.
- In Render, open `pulseos-api` → **Logs**. If you see a database error, your
  `DATABASE_URL` is probably wrong: re-copy it from Neon (Part 1) and update it in
  Render under the service's **Environment** tab, then click **Manual Deploy →
  Deploy latest commit**.

**The app opens but login/AI says "network error."**
- The backend is asleep (wait 30s and retry), or the app's address doesn't match
  your live Render address — see "My Render URL is different" above.

**AI answers feel generic / robotic.**
- Your `ANTHROPIC_API_KEY` isn't set. In Render → `pulseos-api` → **Environment**
  → add/fix `ANTHROPIC_API_KEY` → **Manual Deploy**.

**Will the free database fill up?**
- Neon's free tier is generous (plenty for personal use and a launch). If you
  ever outgrow it, Neon shows an upgrade button — but you won't need it early on.

---

## The whole thing in 6 lines
1. **Neon** → sign up → copy the connection string.
2. **Render** → New → Blueprint → pick `PulseOS` → paste the Neon string + your
   `sk-ant-` key → Apply → check `/health`.
3. **Apple Developer** → enroll ($99) → install Xcode.
4. Terminal: `cd ~/PulseOS/frontend && npx cap open ios`.
5. Xcode → set Team + Bundle ID → plug in iPhone → press ▶︎.
6. Create an account in the app. Done. **No domain, $0 hosting.**
