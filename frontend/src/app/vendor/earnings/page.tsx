"use client";

import { useEffect, useState } from "react";
import { api, formatINR, timeAgo } from "@/lib/api";

type Earnings = {
  gross: number; platform_fee: number; logistics: number; net: number; order_count: number;
  today_net: number; fulfilment_rate: number;
  recent: { id: string; crop: string; quantity_kg: number; unit_price: number; farmer_payout: number; status: string; buyer: string; created_at: string }[];
};

const EMOJI: Record<string, string> = { tomato: "🍅", green_chilli: "🌶️", beans: "🫛", cucumber: "🥒", banana: "🍌", spinach: "🥬" };
const STATUS_STYLES: Record<string, string> = {
  CONFIRMED: "bg-blue-100 text-blue-700", IN_TRANSIT: "bg-amber-100 text-amber-700",
  DELIVERED: "bg-brand-100 text-brand-700", CANCELLED: "bg-red-100 text-red-600",
};

export default function EarningsPage() {
  const [e, setE] = useState<Earnings | null>(null);

  useEffect(() => {
    api<Earnings>("/api/vendor/earnings").then(setE);
  }, []);

  if (!e) return <div className="mt-8 grid gap-4 sm:grid-cols-3">{Array.from({ length: 3 }).map((_, i) => <div key={i} className="card h-28 animate-pulse-soft bg-stone-100/50" />)}</div>;

  const bars = [
    { label: "Gross revenue", value: e.gross, color: "bg-stone-300" },
    { label: "Platform fee", value: -e.platform_fee, color: "bg-amber-400" },
    { label: "Logistics", value: -e.logistics, color: "bg-orange-400" },
    { label: "Net earnings", value: e.net, color: "bg-brand-500" },
  ];
  const maxAbs = Math.max(...bars.map((b) => Math.abs(b.value)), 1);

  return (
    <div className="animate-fadeUp">
      <h1 className="font-display text-3xl font-bold tracking-tight">Earnings</h1>
      <p className="mt-1 text-stone-500">What you actually earn — gross minus fees minus logistics.</p>

      <div className="mt-8 grid gap-4 sm:grid-cols-3">
        <div className="card p-5">
          <div className="text-sm text-stone-500">Net earnings (all time)</div>
          <div className="mt-1 font-display text-3xl font-bold text-brand-700">{formatINR(e.net)}</div>
          <div className="text-xs text-stone-400">across {e.order_count} orders</div>
        </div>
        <div className="card p-5">
          <div className="text-sm text-stone-500">Today's net</div>
          <div className="mt-1 font-display text-3xl font-bold">{formatINR(e.today_net)}</div>
          <div className="text-xs text-stone-400">from orders placed today</div>
        </div>
        <div className="card p-5">
          <div className="text-sm text-stone-500">Fulfilment rate</div>
          <div className="mt-1 font-display text-3xl font-bold text-amber-600">{e.fulfilment_rate}%</div>
          <div className="text-xs text-stone-400">orders delivered successfully</div>
        </div>
      </div>

      {/* Breakdown */}
      <div className="card mt-6 p-6">
        <h2 className="font-display text-lg font-bold">Where the money goes</h2>
        <div className="mt-5 space-y-4">
          {bars.map((b) => (
            <div key={b.label}>
              <div className="mb-1 flex justify-between text-sm">
                <span className="text-stone-600">{b.label}</span>
                <span className="font-semibold">{b.value < 0 ? "−" : ""}{formatINR(Math.abs(b.value))}</span>
              </div>
              <div className="h-2.5 overflow-hidden rounded-full bg-stone-100">
                <div className={`h-full rounded-full ${b.color} transition-all`} style={{ width: `${(Math.abs(b.value) / maxAbs) * 100}%` }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent orders */}
      <div className="card mt-6 p-6">
        <h2 className="font-display text-lg font-bold">Recent orders</h2>
        {e.recent.length === 0 ? (
          <p className="mt-4 text-sm text-stone-500">No orders yet — publish listings to start selling.</p>
        ) : (
          <div className="mt-4 divide-y divide-stone-100">
            {e.recent.map((o) => (
              <div key={o.id} className="flex flex-wrap items-center gap-4 py-3.5">
                <span className="grid h-10 w-10 place-items-center rounded-xl bg-stone-50 text-xl">{EMOJI[o.crop] || "🌱"}</span>
                <div className="min-w-0 flex-1">
                  <div className="font-medium capitalize">{o.crop.replace("_", " ")} · {o.quantity_kg} kg @ {formatINR(o.unit_price)}</div>
                  <div className="text-xs text-stone-500">→ {o.buyer} · {timeAgo(o.created_at)}</div>
                </div>
                <span className={`badge ${STATUS_STYLES[o.status]}`}>{o.status.toLowerCase().replace("_", " ")}</span>
                <div className="w-24 text-right font-display font-bold text-brand-700">+{formatINR(o.farmer_payout)}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
