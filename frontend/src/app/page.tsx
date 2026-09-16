"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

const FEATURES = [
  {
    emoji: "📸",
    title: "Photo → Live Listing",
    body: "A farmer photographs the harvest and speaks the quantity. AI identifies the crop, grades quality and drafts the listing — in under a minute.",
    tag: "For farmers",
  },
  {
    emoji: "🎯",
    title: "Buyer Matching",
    body: "Every listing is scored against real purchase requests — crop, quantity, price, distance and delivery window — so the right buyer sees it first.",
    tag: "For farmers",
  },
  {
    emoji: "🤝",
    title: "Supply Aggregation",
    body: "Small lots from nearby farms are combined into one deliverable order, with pickup routes and net payout calculated before anyone commits.",
    tag: "For everyone",
  },
  {
    emoji: "📊",
    title: "Market Intelligence",
    body: "Demand outlook, price trends and surplus-risk alerts per crop, per locality — so farmers decide what to grow and when to sell.",
    tag: "For farmers",
  },
  {
    emoji: "🛒",
    title: "Honest Marketplace",
    body: "Buyers browse a clean, fast marketplace of farm-fresh produce with lot traceability and farmer reputation — no AI hoops required.",
    tag: "For buyers",
  },
  {
    emoji: "💰",
    title: "Net Earnings Focus",
    body: "We optimise what the farmer actually earns — gross minus logistics minus fees — not just the headline selling price.",
    tag: "For farmers",
  },
];

export default function LandingPage() {
  const { user } = useAuth();
  const ctaHref = user ? (user.role === "VENDOR" ? "/vendor" : "/marketplace") : "/signup";

  return (
    <div className="overflow-hidden">
      {/* Hero */}
      <section className="relative mx-auto max-w-7xl px-4 pb-16 pt-14 sm:px-6 lg:pt-20">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <div className="animate-fadeUp">
            <div className="badge mb-5 bg-brand-100 text-brand-800">🇮🇳 Built for India's small farms</div>
            <h1 className="font-display text-4xl font-extrabold leading-[1.08] tracking-tight text-stone-900 sm:text-5xl lg:text-6xl">
              The marketplace that gives small farms
              <span className="bg-gradient-to-r from-brand-600 to-brand-400 bg-clip-text text-transparent"> an AI trading desk</span>
            </h1>
            <p className="mt-6 max-w-xl text-lg leading-relaxed text-stone-600">
              Everyone gets a clean marketplace for farm-fresh produce. Farmers get an AI workspace that identifies
              harvests, prices them, finds buyers, aggregates supply and plans routes — to maximise what they
              actually earn.
            </p>
            <div className="mt-8 flex flex-wrap items-center gap-4">
              <Link href={ctaHref} className="btn-primary !px-7 !py-3.5 text-base">
                {user ? "Open my FarmMesh" : "Create free account"} →
              </Link>
              <Link href="/marketplace" className="btn-secondary !px-7 !py-3.5 text-base">
                Browse the marketplace
              </Link>
            </div>
            <div className="mt-10 flex flex-wrap gap-x-8 gap-y-3 text-sm text-stone-500">
              <span>✓ Free for farmers</span>
              <span>✓ Kochi &amp; Ernakulam launch</span>
              <span>✓ English · Malayalam ready</span>
            </div>
          </div>

          {/* Demo card */}
          <div className="relative animate-fadeUp [animation-delay:120ms]">
            <div className="absolute -inset-6 -z-10 rounded-[2.5rem] bg-gradient-to-br from-brand-100 via-transparent to-amber-100 blur-2xl" />
            <div className="card space-y-4 p-6">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold uppercase tracking-wider text-stone-400">AI Harvest analysis</span>
                <span className="badge bg-brand-100 text-brand-700">Live demo</span>
              </div>
              <div className="flex items-center gap-4 rounded-xl bg-brand-50 p-4">
                <span className="grid h-14 w-14 shrink-0 place-items-center rounded-xl bg-white text-3xl shadow-card">🌶️</span>
                <div>
                  <div className="font-semibold">Green Chilli identified</div>
                  <div className="text-sm text-stone-500">Grade A · Confidence 94%</div>
                </div>
              </div>
              <div className="rounded-xl border border-stone-100 bg-stone-50 p-4">
                <div className="text-sm text-stone-500">Suggested price range</div>
                <div className="font-display text-2xl font-bold text-stone-900">₹58 – ₹68<span className="text-sm font-medium text-stone-400">/kg</span></div>
                <div className="mt-1 text-xs text-stone-500">Local demand above average · Recent prices trending up</div>
              </div>
              <div className="grid grid-cols-3 gap-2 text-center">
                <div className="rounded-xl border border-stone-100 p-3">
                  <div className="text-lg font-bold">3</div>
                  <div className="text-[11px] text-stone-500">buyers matching</div>
                </div>
                <div className="rounded-xl border border-stone-100 p-3">
                  <div className="text-lg font-bold">2.8km</div>
                  <div className="text-[11px] text-stone-500">nearest buyer</div>
                </div>
                <div className="rounded-xl border border-stone-100 p-3">
                  <div className="text-lg font-bold">₹2,150</div>
                  <div className="text-[11px] text-stone-500">net potential</div>
                </div>
              </div>
              <div className="rounded-xl bg-stone-900 p-4 text-sm text-stone-200">
                <span className="mr-2">🤖</span>
                <em>&ldquo;Based on upcoming demand, consider increasing chilli allocation by 15% next cycle.&rdquo;</em>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Problem strip */}
      <section className="border-y border-stone-200 bg-white/60 py-14">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <div className="grid gap-8 text-center sm:grid-cols-3">
            {[
              ["20–35 kg", "typical small-lot harvest — too small for wholesale channels"],
              ["4–7 days", "of shelf life before perishability destroys value"],
              ["₹ per kg lost", "to intermediaries, transport friction and weak price discovery"],
            ].map(([big, small]) => (
              <div key={big}>
                <div className="font-display text-3xl font-extrabold text-brand-700">{big}</div>
                <div className="mx-auto mt-2 max-w-xs text-sm text-stone-500">{small}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="font-display text-3xl font-bold tracking-tight sm:text-4xl">Two experiences. One platform.</h2>
          <p className="mt-4 text-stone-600">
            Buyers never touch the AI layer — they simply shop. Farmers unlock an AI workspace that works around
            their marketplace activity.
          </p>
        </div>
        <div className="mt-12 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((f) => (
            <div key={f.title} className="card group p-6 transition hover:-translate-y-1 hover:shadow-lift">
              <div className="flex items-start justify-between">
                <span className="grid h-12 w-12 place-items-center rounded-xl bg-brand-50 text-2xl transition group-hover:scale-110">
                  {f.emoji}
                </span>
                <span className={`badge ${f.tag === "For buyers" ? "bg-amber-100 text-amber-800" : "bg-brand-100 text-brand-700"}`}>{f.tag}</span>
              </div>
              <h3 className="mt-4 font-display text-lg font-bold">{f.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-stone-600">{f.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="bg-stone-900 py-20 text-white">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <div className="mx-auto max-w-2xl text-center">
            <div className="badge bg-brand-500/20 text-brand-300">The AI flywheel</div>
            <h2 className="mt-4 font-display text-3xl font-bold tracking-tight sm:text-4xl">From photo to payout</h2>
          </div>
          <div className="mt-12 grid gap-5 md:grid-cols-4">
            {[
              ["1", "Capture", "Photograph the harvest, say the quantity in your language."],
              ["2", "Analyse", "AI identifies the crop, grades it and recommends a price range."],
              ["3", "Sell", "The engine matches buyers, aggregates lots and plans the pickup route."],
              ["4", "Earn", "Track net earnings — and get advice on what to grow next."],
            ].map(([n, t, b]) => (
              <div key={n} className="rounded-2xl border border-white/10 bg-white/5 p-6">
                <div className="grid h-10 w-10 place-items-center rounded-xl bg-brand-500 font-display text-lg font-bold">{n}</div>
                <h3 className="mt-4 font-display text-lg font-bold">{t}</h3>
                <p className="mt-2 text-sm leading-relaxed text-stone-300">{b}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-7xl px-4 py-20 text-center sm:px-6">
        <h2 className="font-display text-3xl font-bold tracking-tight sm:text-4xl">Ready to see it work?</h2>
        <p className="mx-auto mt-3 max-w-xl text-stone-600">
          Sign up as a buyer to shop, or as a farmer/vendor to unlock the full AI workspace.
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-4">
          <Link href="/signup?role=vendor" className="btn-primary !px-7 !py-3.5 text-base">I'm a farmer/vendor</Link>
          <Link href="/signup?role=buyer" className="btn-secondary !px-7 !py-3.5 text-base">I'm buying produce</Link>
        </div>
      </section>

      <footer className="border-t border-stone-200 py-8">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-3 px-4 text-sm text-stone-500 sm:flex-row sm:px-6">
          <span>🌱 FarmMesh AI — AI commerce infrastructure for small farms</span>
          <span>Kochi · Ernakulam · Demo build</span>
        </div>
      </footer>
    </div>
  );
}
