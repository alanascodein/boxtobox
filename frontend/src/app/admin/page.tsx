"use client";

import { useEffect, useState } from "react";
import { api, formatINR } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

type Metrics = {
  active_farmers: number; active_listings: number; buyers: number; orders: number;
  gmv: number; farmer_payouts: number; platform_fees: number; avg_logistics_cost: number;
  sold_out_listings: number; open_buyer_requests: number;
};

export default function AdminPage() {
  const { user, loading } = useAuth();
  const [m, setM] = useState<Metrics | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!loading && user?.role === "ADMIN") {
      api<Metrics>("/api/admin/metrics").then(setM).catch((e) => setError(e.message));
    }
  }, [user, loading]);

  if (!loading && user?.role !== "ADMIN") {
    return (
      <div className="mx-auto max-w-md px-4 py-24 text-center">
        <div className="text-4xl">🛡️</div>
        <h1 className="mt-3 font-display text-2xl font-bold">Admin access required</h1>
        <p className="mt-2 text-sm text-stone-500">Sign in with an administrator account (admin@farmmesh.demo / admin1234).</p>
        <a href="/login" className="btn-primary mt-6">Sign in</a>
      </div>
    );
  }

  if (error) return <div className="p-10 text-center text-red-600">{error}</div>;

  if (!m) {
    return <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6"><div className="grid gap-4 sm:grid-cols-3">{Array.from({ length: 6 }).map((_, i) => <div key={i} className="card h-28 animate-pulse-soft bg-stone-100/50" />)}</div></div>;
  }

  const cards = [
    ["Active farmers", m.active_farmers, "🌾"],
    ["Buyers", m.buyers, "🛒"],
    ["Active listings", m.active_listings, "🧺"],
    ["Total orders", m.orders, "📦"],
    ["GMV", formatINR(m.gmv), "💹"],
    ["Farmer payouts", formatINR(m.farmer_payouts), "💰"],
    ["Platform fees", formatINR(m.platform_fees), "🏛️"],
    ["Avg logistics/order", formatINR(m.avg_logistics_cost), "🚚"],
  ] as const;

  return (
    <div className="mx-auto max-w-7xl animate-fadeUp px-4 py-10 sm:px-6">
      <h1 className="font-display text-3xl font-bold tracking-tight">Platform Admin</h1>
      <p className="mt-1 text-stone-500">Marketplace health, GMV and farmer economics at a glance.</p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {cards.map(([label, value, emoji]) => (
          <div key={label} className="card p-5">
            <div className="flex items-center justify-between">
              <span className="text-sm text-stone-500">{label}</span>
              <span className="text-xl">{emoji}</span>
            </div>
            <div className="mt-2 font-display text-3xl font-bold">{value}</div>
          </div>
        ))}
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-2">
        <div className="card p-6">
          <h2 className="font-display text-lg font-bold">Liquidity signals</h2>
          <div className="mt-4 space-y-3 text-sm">
            <div className="flex items-center justify-between rounded-xl bg-stone-50 px-4 py-3">
              <span>Open buyer requests</span><b>{m.open_buyer_requests}</b>
            </div>
            <div className="flex items-center justify-between rounded-xl bg-stone-50 px-4 py-3">
              <span>Sold-out listings (re-list opportunity)</span><b>{m.sold_out_listings}</b>
            </div>
          </div>
        </div>
        <div className="card p-6">
          <h2 className="font-display text-lg font-bold">North star</h2>
          <p className="mt-2 text-sm text-stone-500">Farmer net income generated through successful marketplace transactions:</p>
          <div className="mt-3 font-display text-4xl font-bold text-brand-700">{formatINR(m.farmer_payouts)}</div>
        </div>
      </div>
    </div>
  );
}
