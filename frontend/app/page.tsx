"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Activity,
  ArrowRight,
  Brain,
  Check,
  MessagesSquare,
  Radar,
  Sparkles,
  Users,
} from "lucide-react";
import { getSession } from "@/lib/auth";

const CATEGORIES = [
  { label: "Markets", accent: "bg-accent-purple", text: "text-on-primary", note: "Moves before the crowd does." },
  { label: "Career", accent: "bg-accent-blue", text: "text-on-primary", note: "The next high-leverage step." },
  { label: "Economy", accent: "bg-accent-orange", text: "text-on-primary", note: "Rates, prices, runway." },
  { label: "Growth", accent: "bg-accent-green", text: "text-primary", note: "Asymmetric, reversible bets." },
];

const FEATURES = [
  { icon: Sparkles, title: "Daily Intelligence Briefing", body: "Every morning, your highest-value actions — ranked by expected value × calibrated confidence, with the evidence and the dissenting view." },
  { icon: MessagesSquare, title: "AI Analyst, on call", body: "Chat with an analyst that knows your goals and signals. Ask anything; get a specific, quantified, action-first answer." },
  { icon: Radar, title: "Opportunity Engine", body: "Time-sensitive, asymmetric upside surfaced automatically and tracked until you act." },
  { icon: Users, title: "Operator Community", body: "Publish your calls, react to others', and see what sharp operators are acting on right now." },
  { icon: Brain, title: "Transparent Memory", body: "Everything PulseOS knows about you is visible and editable. No black box." },
  { icon: Activity, title: "Strategic Council", body: "Seven AI specialists debate the high-stakes calls, then synthesize — preserving the disagreement." },
];

export default function Home() {
  const router = useRouter();
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    if (getSession()) router.replace("/dashboard");
    else setChecked(true);
  }, [router]);

  if (!checked) {
    return (
      <div className="grid min-h-screen place-items-center text-mute">
        <Activity className="h-6 w-6 animate-pulse text-ink" />
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {/* Nav */}
      <header className="mx-auto flex max-w-[1180px] items-center justify-between px-lg py-lg md:px-2xl">
        <div className="flex items-center gap-sm">
          <div className="grid h-8 w-8 place-items-center rounded-md bg-primary">
            <Activity className="h-4 w-4 text-on-primary" />
          </div>
          <span className="text-[20px] font-semibold tracking-[-0.4px] text-ink">PulseOS</span>
        </div>
        <div className="flex items-center gap-sm">
          <Link href="/login" className="btn-ghost btn-sm">
            Sign in
          </Link>
          <Link href="/login" className="btn-primary btn-sm">
            Start free
          </Link>
        </div>
      </header>

      {/* Hero */}
      <section className="mx-auto max-w-[1180px] px-lg py-3xl text-center md:px-2xl">
        <div className="mx-auto mb-lg inline-flex items-center gap-2 rounded-full border border-hairline bg-canvas px-md py-1.5 text-[12px] font-medium text-body-mid">
          <span className="h-1.5 w-1.5 rounded-full bg-accent-green" />
          Real-time intelligence, calibrated and cited
        </div>
        <h1 className="mx-auto max-w-3xl text-[44px] font-semibold leading-[1.05] tracking-[-1px] text-ink md:text-[72px]">
          The highest-value action
          <br className="hidden md:block" /> you should take right now.
        </h1>
        <p className="mx-auto mt-lg max-w-xl text-[18px] leading-relaxed text-body-mid md:text-[20px]">
          PulseOS turns global, market, and personal signals into a daily briefing of ranked,
          evidence-backed moves — and an AI analyst that helps you act on them.
        </p>
        <div className="mt-2xl flex items-center justify-center gap-md">
          <Link href="/login" className="btn-primary">
            Start free <ArrowRight className="h-4 w-4" />
          </Link>
          <Link href="/login" className="btn-secondary">
            See a live briefing
          </Link>
        </div>

        {/* Category cards — the chromatic five-stop signature */}
        <div className="mt-3xl grid grid-cols-2 gap-md md:grid-cols-4">
          {CATEGORIES.map((c) => (
            <div
              key={c.label}
              className={`flex flex-col justify-between rounded-md ${c.accent} ${c.text} p-lg text-left shadow-card`}
              style={{ minHeight: 132 }}
            >
              <span className="text-[12px] font-medium uppercase tracking-[0.6px] opacity-80">
                {c.label}
              </span>
              <span className="text-[18px] font-medium leading-tight">{c.note}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-[1180px] px-lg py-3xl md:px-2xl">
        <div className="mb-2xl max-w-2xl">
          <div className="eyebrow mb-sm">Why operators run on PulseOS</div>
          <h2 className="text-[32px] font-medium tracking-[-0.5px] text-ink md:text-[40px]">
            An intelligence team, compressed into one screen.
          </h2>
        </div>
        <div className="grid grid-cols-1 gap-md md:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map(({ icon: Icon, title, body }) => (
            <div key={title} className="card p-lg">
              <div className="mb-md grid h-9 w-9 place-items-center rounded-md bg-canvas-soft">
                <Icon className="h-4 w-4 text-ink" />
              </div>
              <h3 className="text-[16px] font-medium text-ink">{title}</h3>
              <p className="mt-1.5 text-[14px] leading-relaxed text-body-mid">{body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section className="mx-auto max-w-[1180px] px-lg py-3xl md:px-2xl">
        <div className="grid grid-cols-1 gap-md lg:grid-cols-3">
          <div className="lg:col-span-1">
            <div className="eyebrow mb-sm">Pricing</div>
            <h2 className="text-[32px] font-medium tracking-[-0.5px] text-ink">
              Try Pro free for 2 weeks. Pays for itself in a single call.
            </h2>
            <p className="mt-md text-[15px] leading-relaxed text-body-mid">
              No card to start your trial. Keep it when the briefing earns its keep.
            </p>
          </div>
          <div className="card p-3xl lg:col-span-1">
            <div className="eyebrow">Basic</div>
            <div className="mt-sm flex items-end gap-1">
              <span className="text-[40px] font-semibold tracking-[-1px] text-ink">$5</span>
              <span className="mb-2 text-[14px] text-mute">/ month</span>
            </div>
            <ul className="mt-lg space-y-sm text-[14px] text-body">
              {["Daily briefing (3 actions)", "AI analyst (basic)", "Community feed", "Ad-supported"].map((f) => (
                <li key={f} className="flex items-center gap-sm">
                  <Check className="h-4 w-4 text-signal-green" /> {f}
                </li>
              ))}
            </ul>
            <Link href="/login" className="btn-secondary mt-lg w-full">
              Choose Basic
            </Link>
          </div>
          <div className="card-dark relative p-3xl shadow-lift lg:col-span-1">
            <span className="absolute right-lg top-lg rounded-sm bg-accent-green px-sm py-xxs text-[12px] font-medium text-primary">
              Most popular
            </span>
            <div className="text-[12px] font-medium uppercase tracking-[0.6px] text-on-primary/70">
              Pro
            </div>
            <div className="mt-sm flex items-end gap-1">
              <span className="text-[40px] font-semibold tracking-[-1px] text-on-primary">$15</span>
              <span className="mb-2 text-[14px] text-on-primary/60">/ month</span>
            </div>
            <div className="mt-xs text-[13px] font-medium text-accent-green">
              2-week free trial — no ads
            </div>
            <ul className="mt-lg space-y-sm text-[14px] text-on-primary/90">
              {[
                "Unlimited briefings + full Strategic Council",
                "AI analyst with live reasoning",
                "Opportunity Engine + value tracking",
                "Priority signals & integrations",
              ].map((f) => (
                <li key={f} className="flex items-center gap-sm">
                  <Check className="h-4 w-4 text-accent-green" /> {f}
                </li>
              ))}
            </ul>
            <Link href="/login" className="btn mt-lg w-full bg-on-primary text-ink hover:bg-hairline-soft">
              Start 2-week free trial <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </section>

      <footer className="mx-auto max-w-[1180px] px-lg py-2xl text-[13px] text-mute md:px-2xl">
        © PulseOS — Real-Time Intelligence Operating System.
      </footer>
    </div>
  );
}
