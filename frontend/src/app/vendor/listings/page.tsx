"use client";

import { useEffect, useState } from "react";
import { api, formatINR, timeAgo } from "@/lib/api";

type Listing = {
  id: string; crop: string; title: string; quantity_kg: number; quantity_available_kg: number;
  price_per_kg: number; quality_grade: string; status: string; lot_id: string; created_at: string;
};

type Match = {
  request_id: string; buyer_name: string; buyer_type: string; quantity_kg: number;
  max_price: number; distance_km: number; delivery_window: string; match_pct: number;
};

const EMOJI: Record<string, string> = { tomato: "🍅", green_chilli: "🌶️", beans: "🫛", cucumber: "🥒", banana: "🍌", spinach: "🥬" };

export default function VendorListingsPage() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [matches, setMatches] = useState<{ listing: Listing; rows: Match[] } | null>(null);
  const [loadingMatches, setLoadingMatches] = useState(false);

  useEffect(() => {
    api<Listing[]>("/api/listings/mine").then((l) => { setListings(l); setLoaded(true); });
  }, []);

  async function showMatches(l: Listing) {
    setLoadingMatches(true);
    try {
      const rows = await api<Match[]>(`/api/vendor/ai/match/${l.id}`);
      setMatches({ listing: l, rows });
    } finally {
      setLoadingMatches(false);
    }
  }

  return (
    <div className="animate-fadeUp">
      <h1 className="font-display text-3xl font-bold tracking-tight">My Listings</h1>
      <p className="mt-1 text-stone-500">Manage live produce and see AI buyer matches per lot.</p>

      {!loaded ? (
        <div className="mt-8 space-y-3">{Array.from({ length: 3 }).map((_, i) => <div key={i} className="card h-24 animate-pulse-soft bg-stone-100/50" />)}</div>
      ) : listings.length === 0 ? (
        <div className="card mt-8 p-14 text-center">
          <div className="text-4xl">🧺</div>
          <h3 className="mt-3 font-display text-lg font-bold">No listings yet</h3>
          <a href="/vendor/sell" className="btn-primary mt-5">Sell your first harvest</a>
        </div>
      ) : (
        <div className="mt-8 space-y-4">
          {listings.map((l) => {
            const soldPct = l.quantity_kg > 0 ? ((l.quantity_kg - l.quantity_available_kg) / l.quantity_kg) * 100 : 0;
            return (
              <div key={l.id} className="card flex flex-wrap items-center gap-5 p-5">
                <span className="grid h-14 w-14 shrink-0 place-items-center rounded-xl bg-stone-50 text-3xl">{EMOJI[l.crop] || "🌱"}</span>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="truncate font-semibold">{l.title}</h3>
                    <span className={`badge ${l.status === "ACTIVE" ? "bg-brand-100 text-brand-700" : "bg-stone-100 text-stone-500"}`}>{l.status.toLowerCase()}</span>
                  </div>
                  <div className="mt-0.5 text-sm text-stone-500">
                    {formatINR(l.price_per_kg)}/kg · {l.quantity_available_kg.toFixed(0)} of {l.quantity_kg.toFixed(0)} kg left · {l.lot_id} · {timeAgo(l.created_at)}
                  </div>
                  <div className="mt-2 h-1.5 w-full max-w-xs overflow-hidden rounded-full bg-stone-100">
                    <div className="h-full rounded-full bg-brand-500 transition-all" style={{ width: `${soldPct}%` }} />
                  </div>
                </div>
                <button className="btn-secondary" onClick={() => showMatches(l)} disabled={loadingMatches}>
                  🎯 Find buyers
                </button>
              </div>
            );
          })}
        </div>
      )}

      {/* Matches drawer */}
      {matches && (
        <div className="fixed inset-0 z-50 flex justify-end bg-stone-900/40 backdrop-blur-sm" onClick={() => setMatches(null)}>
          <div className="h-full w-full max-w-lg overflow-y-auto bg-white p-6 shadow-lift" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-xs font-semibold uppercase tracking-wide text-stone-400">AI buyer matching</div>
                <h2 className="font-display text-xl font-bold">{matches.listing.title}</h2>
              </div>
              <button onClick={() => setMatches(null)} className="btn-ghost">✕</button>
            </div>
            {matches.rows.length === 0 ? (
              <div className="mt-10 rounded-2xl bg-stone-50 p-8 text-center text-sm text-stone-500">
                No nearby buyers currently match. Your listing stays public — new requests trigger re-matching.
              </div>
            ) : (
              <div className="mt-6 space-y-3">
                {matches.rows.map((m) => (
                  <div key={m.request_id} className="rounded-2xl border border-stone-200 p-4 transition hover:border-brand-300 hover:bg-brand-50/40">
                    <div className="flex items-center justify-between">
                      <div className="font-semibold">{m.buyer_name}</div>
                      <span className={`badge ${m.match_pct >= 80 ? "bg-brand-100 text-brand-700" : "bg-amber-100 text-amber-700"}`}>{m.match_pct}% match</span>
                    </div>
                    <div className="mt-2 grid grid-cols-2 gap-2 text-sm text-stone-600">
                      <span>📦 needs up to {m.quantity_kg} kg</span>
                      <span>💰 max {formatINR(m.max_price)}/kg</span>
                      <span>📍 {m.distance_km} km away</span>
                      <span>🕒 {m.delivery_window.replace("_", " ")}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
