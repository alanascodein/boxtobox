"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { api, formatINR } from "@/lib/api";

type Dash = {
  farmer_name: string; farm_name: string; today_harvest_kg: number; active_listings: number;
  available_kg: number; potential_earnings: { min: number; max: number };
  buyer_opportunities: number; reputation: number;
};

export default function VendorDashboard() {
  const [d, setD] = useState<Dash | null>(null);

  useEffect(() => {
    api<Dash>("/api/vendor/dashboard").then(setD);
  }, []);

  if (!d) {
    return (
      <div className="grid gap-4 sm:grid-cols-2">
        {Array.from({ length: 4 }).map((_, i) => <div key={i} className="card h-28 animate-pulse-soft bg-stone-100/50" />)}
      </div>
    );
  }

  const hour = new Date().getHours();
  const greeting = hour < 12 ? "Good morning" : hour < 17 ? "Good afternoon" : "Good evening";

  return (
    <div className="animate-fadeUp">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl font-bold tracking-tight">{greeting}, {d.farmer_name.split(" ")[0]} 👋</h1>
          <p className="mt-1 text-stone-500">Here's what's happening at {d.farm_name} today.</p>
        </div>
        <Link href="/vendor/sell" className="btn-primary">📸 Sell a harvest</Link>
      </div>

      {/* Stat cards */}
      <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="card p-5">
          <div className="text-sm text-stone-500">Today's harvest listed</div>
          <div className="mt-1 font-display text-3xl font-bold">{d.today_harvest_kg.toFixed(0)}<span className="text-base font-medium text-stone-400"> kg</span></div>
        </div>
        <div className="card p-5">
          <div className="text-sm text-stone-500">Potential earnings</div>
          <div className="mt-1 font-display text-3xl font-bold text-brand-700">{formatINR(d.potential_earnings.min)}</div>
          <div className="text-xs text-stone-400">up to {formatINR(d.potential_earnings.max)}</div>
        </div>
        <div className="card p-5">
          <div className="text-sm text-stone-500">Buyer opportunities</div>
          <div className="mt-1 font-display text-3xl font-bold">{d.buyer_opportunities}</div>
          <div className="text-xs text-stone-400">across your active listings</div>
        </div>
        <div className="card p-5">
          <div className="text-sm text-stone-500">Reputation</div>
          <div className="mt-1 font-display text-3xl font-bold text-amber-600">★ {d.reputation.toFixed(1)}</div>
          <div className="text-xs text-stone-400">{d.active_listings} active listings · {d.available_kg.toFixed(0)} kg live</div>
        </div>
      </div>

      {/* Quick actions */}
      <div className="mt-8 grid gap-4 md:grid-cols-3">
        <Link href="/vendor/sell" className="card group p-6 transition hover:-translate-y-1 hover:shadow-lift">
          <span className="grid h-12 w-12 place-items-center rounded-xl bg-brand-50 text-2xl transition group-hover:scale-110">📸</span>
          <h3 className="mt-4 font-display font-bold">Sell in 60 seconds</h3>
          <p className="mt-1 text-sm text-stone-500">Photo → AI grade → price → live listing.</p>
        </Link>
        <Link href="/vendor/market-intel" className="card group p-6 transition hover:-translate-y-1 hover:shadow-lift">
          <span className="grid h-12 w-12 place-items-center rounded-xl bg-blue-50 text-2xl transition group-hover:scale-110">📊</span>
          <h3 className="mt-4 font-display font-bold">Market intelligence</h3>
          <p className="mt-1 text-sm text-stone-500">Demand outlook &amp; surplus-risk per crop.</p>
        </Link>
        <Link href="/vendor/farm-plan" className="card group p-6 transition hover:-translate-y-1 hover:shadow-lift">
          <span className="grid h-12 w-12 place-items-center rounded-xl bg-amber-50 text-2xl transition group-hover:scale-110">🌾</span>
          <h3 className="mt-4 font-display font-bold">What to grow next</h3>
          <p className="mt-1 text-sm text-stone-500">AI crop plan ranked by profit × sale probability.</p>
        </Link>
      </div>
    </div>
  );
}
