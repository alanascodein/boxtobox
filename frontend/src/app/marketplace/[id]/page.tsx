"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api, formatINR, timeAgo } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import type { Listing } from "../page";

const EMOJI: Record<string, string> = {
  tomato: "🍅", green_chilli: "🌶️", beans: "🫛", cucumber: "🥒", banana: "🍌", spinach: "🥬",
};

export default function ListingDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const router = useRouter();
  const [listing, setListing] = useState<Listing | null>(null);
  const [qty, setQty] = useState("10");
  const [loc, setLoc] = useState("Kochi");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api<Listing>(`/api/market/listings/${id}`).then((l) => {
      setListing(l);
      setQty(String(Math.min(10, l.quantity_available_kg)));
    });
  }, [id]);

  async function placeOrder() {
    setError("");
    setMsg("");
    if (!user) {
      router.push("/login");
      return;
    }
    setBusy(true);
    try {
      const o = await api<{ id: string }>("/api/orders", {
        method: "POST",
        body: JSON.stringify({ listing_id: id, quantity_kg: Number(qty), delivery_location: loc }),
      });
      setMsg(`Order ${o.id.toUpperCase()} confirmed! Track it in My Orders.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Order failed");
    } finally {
      setBusy(false);
    }
  }

  if (!listing) return <div className="p-10 text-center text-stone-400">Loading…</div>;

  const gross = Number(qty || 0) * listing.price_per_kg;

  return (
    <div className="mx-auto max-w-5xl px-4 py-10 sm:px-6">
      <Link href="/marketplace" className="btn-ghost mb-4">← Back to marketplace</Link>
      <div className="grid gap-8 lg:grid-cols-2">
        {/* Left: product */}
        <div>
          <div className="card grid h-72 place-items-center bg-gradient-to-br from-brand-50 to-amber-50 text-8xl">
            {EMOJI[listing.crop] || "🌱"}
          </div>
          <div className="card mt-5 p-6">
            <h2 className="font-display text-lg font-bold">Traceability</h2>
            <div className="mt-4 space-y-3 text-sm">
              {[
                ["Lot ID", listing.lot_id, "🌿"],
                ["Harvest date", new Date(listing.harvest_date).toLocaleDateString("en-IN", { day: "numeric", month: "short" }), "🗓️"],
                ["Farm", `${listing.farm_name} — ${listing.location}, ${listing.district}`, "📍"],
                ["Grading", `Visual grade ${listing.quality_grade} — subject to buyer verification on delivery`, "🔍"],
              ].map(([k, v, e]) => (
                <div key={k} className="flex items-start gap-3 rounded-xl bg-stone-50 p-3">
                  <span>{e}</span>
                  <div>
                    <div className="text-xs font-semibold uppercase tracking-wide text-stone-400">{k}</div>
                    <div className="font-medium">{v}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right: buy box */}
        <div>
          <div className="flex items-center gap-2 text-sm text-stone-500">
            <span className="badge bg-brand-100 text-brand-700">Grade {listing.quality_grade}</span>
            <span>Listed {timeAgo(listing.created_at)}</span>
          </div>
          <h1 className="mt-2 font-display text-3xl font-bold tracking-tight">{listing.title}</h1>
          <div className="mt-1 text-stone-500">
            by <span className="font-semibold text-stone-700">{listing.farm_name}</span> · ★ {listing.reputation_score.toFixed(1)}
          </div>
          <p className="mt-4 leading-relaxed text-stone-600">{listing.description}</p>

          <div className="card mt-6 p-6">
            <div className="flex items-end justify-between">
              <div>
                <div className="font-display text-3xl font-bold text-brand-700">{formatINR(listing.price_per_kg)}<span className="text-base font-medium text-stone-400">/kg</span></div>
                <div className="text-sm text-stone-500">{listing.quantity_available_kg.toFixed(0)} kg available</div>
              </div>
            </div>

            <div className="mt-5 grid gap-4 sm:grid-cols-2">
              <div>
                <label className="label">Quantity (kg)</label>
                <input type="number" min="1" max={listing.quantity_available_kg} className="input" value={qty} onChange={(e) => setQty(e.target.value)} />
              </div>
              <div>
                <label className="label">Deliver to</label>
                <select className="input" value={loc} onChange={(e) => setLoc(e.target.value)}>
                  {["Kochi", "Ernakulam", "Aluva", "Tripunithura", "Kakkanad", "Mattancherry", "Paravur", "Vyttila"].map((l) => <option key={l}>{l}</option>)}
                </select>
              </div>
            </div>

            <div className="mt-5 space-y-1.5 rounded-xl bg-stone-50 p-4 text-sm">
              <div className="flex justify-between"><span className="text-stone-500">Produce ({qty} kg × {formatINR(listing.price_per_kg)})</span><span className="font-medium">{formatINR(gross)}</span></div>
              <div className="flex justify-between"><span className="text-stone-500">Delivery (est.)</span><span className="font-medium">Calculated at {loc}</span></div>
              <div className="flex justify-between border-t border-stone-200 pt-1.5 text-base font-bold"><span>Total</span><span>≈ {formatINR(gross)}</span></div>
            </div>

            {msg && <div className="mt-4 rounded-xl bg-brand-50 px-4 py-3 text-sm font-medium text-brand-800">{msg}</div>}
            {error && <div className="mt-4 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
            {listing.status !== "ACTIVE" || listing.quantity_available_kg <= 0 ? (
              <button className="btn-primary mt-5 w-full" disabled>Sold out</button>
            ) : (
              <button className="btn-primary mt-5 w-full" onClick={placeOrder} disabled={busy || !Number(qty)}>
                {busy ? "Placing order…" : user ? "Place order" : "Sign in to order"}
              </button>
            )}
            <p className="mt-3 text-center text-xs text-stone-400">Simulated payment · no real money moves in this demo</p>
          </div>
        </div>
      </div>
    </div>
  );
}
