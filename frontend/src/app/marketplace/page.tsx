"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { api, formatINR } from "@/lib/api";

export type Listing = {
  id: string; crop: string; title: string; description: string;
  quantity_kg: number; quantity_available_kg: number; price_per_kg: number;
  quality_grade: string; harvest_date: string; location: string; district: string;
  lot_id: string; status: string; farm_name: string; vendor_name: string;
  reputation_score: number; created_at: string;
};

const EMOJI: Record<string, string> = {
  tomato: "🍅", green_chilli: "🌶️", beans: "🫛", cucumber: "🥒", banana: "🍌", spinach: "🥬",
};

export default function MarketplacePage() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [crop, setCrop] = useState("");
  const [grade, setGrade] = useState("");
  const [sort, setSort] = useState("newest");
  const [maxPrice, setMaxPrice] = useState("");

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (crop) params.set("crop", crop);
    if (grade) params.set("grade", grade);
    if (sort) params.set("sort", sort);
    if (maxPrice) params.set("max_price", maxPrice);
    const t = setTimeout(() => {
      api<Listing[]>(`/api/market/listings?${params}`)
        .then(setListings)
        .finally(() => setLoading(false));
    }, 250);
    return () => clearTimeout(t);
  }, [search, crop, grade, sort, maxPrice]);

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl font-bold tracking-tight">Fresh from the farm</h1>
          <p className="mt-1 text-stone-500">Direct from small farms around Kochi &amp; Ernakulam — harvested this week.</p>
        </div>
        <div className="badge bg-brand-100 text-brand-800">{loading ? "…" : `${listings.length} live listings`}</div>
      </div>

      {/* Filters */}
      <div className="card mt-6 grid gap-3 p-4 sm:grid-cols-2 lg:grid-cols-5">
        <input className="input lg:col-span-2" placeholder="Search produce, farms, locations…" value={search} onChange={(e) => setSearch(e.target.value)} />
        <select className="input" value={crop} onChange={(e) => setCrop(e.target.value)}>
          <option value="">All crops</option>
          {Object.entries(EMOJI).map(([slug, e]) => <option key={slug} value={slug}>{e} {slug.replace("_", " ")}</option>)}
        </select>
        <select className="input" value={grade} onChange={(e) => setGrade(e.target.value)}>
          <option value="">Any grade</option>
          <option value="A">Grade A</option>
          <option value="B">Grade B</option>
          <option value="C">Grade C</option>
        </select>
        <div className="flex gap-2">
          <input type="number" min="0" className="input" placeholder="Max ₹/kg" value={maxPrice} onChange={(e) => setMaxPrice(e.target.value)} />
          <select className="input !w-32" value={sort} onChange={(e) => setSort(e.target.value)}>
            <option value="newest">Newest</option>
            <option value="price_asc">Price ↑</option>
            <option value="price_desc">Price ↓</option>
          </select>
        </div>
      </div>

      {/* Grid */}
      {loading ? (
        <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="card h-72 animate-pulse-soft bg-stone-100/50" />
          ))}
        </div>
      ) : listings.length === 0 ? (
        <div className="card mt-8 p-14 text-center">
          <div className="text-4xl">🧺</div>
          <h3 className="mt-3 font-display text-lg font-bold">No listings match your filters</h3>
          <p className="mt-1 text-sm text-stone-500">Try clearing the search or widening the price range.</p>
        </div>
      ) : (
        <div className="mt-8 grid gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {listings.map((l) => (
            <Link key={l.id} href={`/marketplace/${l.id}`} className="card group flex flex-col overflow-hidden transition hover:-translate-y-1 hover:shadow-lift">
              <div className="relative grid h-36 place-items-center bg-gradient-to-br from-brand-50 to-amber-50 text-6xl transition group-hover:scale-105">
                {EMOJI[l.crop] || "🌱"}
                <span className="badge absolute left-3 top-3 bg-white/90 text-stone-700 shadow-card">Grade {l.quality_grade}</span>
                {l.quantity_available_kg < 25 && (
                  <span className="badge absolute right-3 top-3 bg-amber-500 text-white shadow-card">Only {l.quantity_available_kg.toFixed(0)} kg</span>
                )}
              </div>
              <div className="flex flex-1 flex-col p-4">
                <div className="flex items-start justify-between gap-2">
                  <h3 className="font-semibold leading-snug">{l.title}</h3>
                </div>
                <div className="mt-1 text-xs text-stone-500">📍 {l.location} · {l.farm_name}</div>
                <div className="mt-auto flex items-end justify-between pt-4">
                  <div>
                    <div className="font-display text-xl font-bold text-brand-700">{formatINR(l.price_per_kg)}<span className="text-xs font-medium text-stone-400">/kg</span></div>
                    <div className="text-xs text-stone-500">{l.quantity_available_kg.toFixed(0)} kg available</div>
                  </div>
                  <div className="flex items-center gap-0.5 text-xs font-semibold text-amber-600">
                    ★ {l.reputation_score.toFixed(1)}
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
