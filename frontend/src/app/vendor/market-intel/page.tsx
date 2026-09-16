"use client";

import { useEffect, useState } from "react";
import { api, formatINR } from "@/lib/api";

type Outlook = {
  crop: string; crop_name: string; emoji: string; price_avg: number; price_trend_pct: number;
  demand_7d_pct: number; surplus_risk: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"; risk_label: string; confidence: string;
};

type Sim = {
  crop: string; baseline: { price: number; net_30kg: number };
  intervention: { action: string; price: number; net_30kg: number; delta: number }; confidence: string;
};

type Agg = {
  crop: string; required_kg: number; fulfilled_kg: number; complete: boolean; farmer_count: number;
  farmers: { farm_name: string; farmer_location: string; distance_km: number; take_kg: number; price_per_kg: number }[];
  total_cost: number; avg_price: number; farmers_net_payout: number;
};

const RISK_STYLES: Record<string, string> = {
  LOW: "bg-brand-100 text-brand-700", MEDIUM: "bg-amber-100 text-amber-700",
  HIGH: "bg-orange-100 text-orange-700", CRITICAL: "bg-red-100 text-red-700",
};

const CROPS = [
  ["tomato", "🍅 Tomato"], ["green_chilli", "🌶️ Green Chilli"], ["beans", "🫛 Beans"],
  ["cucumber", "🥒 Cucumber"], ["banana", "🍌 Banana"], ["spinach", "🥬 Spinach"],
];

export default function MarketIntelPage() {
  const [outlook, setOutlook] = useState<Outlook[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [simCrop, setSimCrop] = useState("green_chilli");
  const [harvestDelta, setHarvestDelta] = useState(20);
  const [demandDelta, setDemandDelta] = useState(-15);
  const [sim, setSim] = useState<Sim | null>(null);
  const [simBusy, setSimBusy] = useState(false);
  const [agg, setAgg] = useState<Agg | null>(null);
  const [aggCrop, setAggCrop] = useState("tomato");
  const [aggQty, setAggQty] = useState("100");
  const [aggBusy, setAggBusy] = useState(false);

  useEffect(() => {
    api<Outlook[]>("/api/vendor/intelligence/outlook").then((o) => { setOutlook(o); setLoaded(true); });
  }, []);

  async function runSim() {
    setSimBusy(true);
    try {
      const s = await api<Sim>("/api/vendor/intelligence/simulate", {
        method: "POST",
        body: JSON.stringify({ crop: simCrop, harvest_delta_pct: harvestDelta, demand_delta_pct: demandDelta }),
      });
      setSim(s);
    } finally {
      setSimBusy(false);
    }
  }

  async function runAgg() {
    setAggBusy(true);
    try {
      const a = await api<Agg>("/api/vendor/ai/aggregate", {
        method: "POST",
        body: JSON.stringify({ crop: aggCrop, quantity_kg: Number(aggQty), location: "Kochi" }),
      });
      setAgg(a);
    } finally {
      setAggBusy(false);
    }
  }

  return (
    <div className="animate-fadeUp">
      <h1 className="font-display text-3xl font-bold tracking-tight">Market Intelligence</h1>
      <p className="mt-1 text-stone-500">Demand outlook, imbalance risk and what-if planning for your crops.</p>

      {/* Outlook grid */}
      {!loaded ? (
        <div className="mt-8 grid gap-4 sm:grid-cols-2">{Array.from({ length: 4 }).map((_, i) => <div key={i} className="card h-36 animate-pulse-soft bg-stone-100/50" />)}</div>
      ) : (
        <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {outlook.map((o) => (
            <div key={o.crop} className="card p-5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <span className="text-2xl">{o.emoji}</span>
                  <span className="font-semibold">{o.crop_name}</span>
                </div>
                <span className={`badge ${RISK_STYLES[o.surplus_risk]}`}>{o.surplus_risk}</span>
              </div>
              <div className="mt-4 grid grid-cols-3 gap-2 text-center">
                <div className="rounded-xl bg-stone-50 p-2.5">
                  <div className="font-display font-bold">{formatINR(o.price_avg)}</div>
                  <div className="text-[11px] text-stone-400">avg ₹/kg</div>
                </div>
                <div className="rounded-xl bg-stone-50 p-2.5">
                  <div className={`font-display font-bold ${o.price_trend_pct >= 0 ? "text-brand-600" : "text-red-500"}`}>
                    {o.price_trend_pct >= 0 ? "+" : ""}{o.price_trend_pct}%
                  </div>
                  <div className="text-[11px] text-stone-400">14d trend</div>
                </div>
                <div className="rounded-xl bg-stone-50 p-2.5">
                  <div className={`font-display font-bold ${o.demand_7d_pct >= 0 ? "text-brand-600" : "text-red-500"}`}>
                    {o.demand_7d_pct >= 0 ? "+" : ""}{o.demand_7d_pct}%
                  </div>
                  <div className="text-[11px] text-stone-400">7d demand</div>
                </div>
              </div>
              <div className="mt-3 text-xs text-stone-500">{o.risk_label} · confidence {o.confidence.toLowerCase()}</div>
            </div>
          ))}
        </div>
      )}

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        {/* What-if simulation */}
        <div className="card p-6">
          <h2 className="font-display text-lg font-bold">🔮 What-if simulation</h2>
          <p className="mt-1 text-sm text-stone-500">Compare doing nothing vs. a coordinated intervention.</p>
          <div className="mt-4 space-y-4">
            <div>
              <label className="label">Crop</label>
              <select className="input" value={simCrop} onChange={(e) => setSimCrop(e.target.value)}>
                {CROPS.map(([s, l]) => <option key={s} value={s}>{l}</option>)}
              </select>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="label">Harvest change: {harvestDelta > 0 ? "+" : ""}{harvestDelta}%</label>
                <input type="range" min="-40" max="40" value={harvestDelta} onChange={(e) => setHarvestDelta(Number(e.target.value))} className="w-full accent-brand-600" />
              </div>
              <div>
                <label className="label">Demand change: {demandDelta > 0 ? "+" : ""}{demandDelta}%</label>
                <input type="range" min="-40" max="40" value={demandDelta} onChange={(e) => setDemandDelta(Number(e.target.value))} className="w-full accent-brand-600" />
              </div>
            </div>
            <button className="btn-primary w-full" onClick={runSim} disabled={simBusy}>{simBusy ? "Simulating…" : "Run scenario"}</button>
          </div>

          {sim && (
            <div className="mt-5 space-y-3">
              <div className="rounded-xl bg-stone-50 p-4">
                <div className="text-xs font-semibold uppercase tracking-wide text-stone-400">Do nothing</div>
                <div className="mt-1 font-display text-xl font-bold">{formatINR(sim.baseline.net_30kg)}</div>
                <div className="text-xs text-stone-500">net on 30 kg at ~{formatINR(sim.baseline.price)}/kg</div>
              </div>
              <div className="rounded-xl bg-brand-50 p-4">
                <div className="text-xs font-semibold uppercase tracking-wide text-brand-600">Recommended intervention</div>
                <div className="mt-1 text-sm font-medium">{sim.intervention.action}</div>
                <div className="mt-1 font-display text-xl font-bold text-brand-700">{formatINR(sim.intervention.net_30kg)}</div>
                <div className={`text-sm font-semibold ${sim.intervention.delta >= 0 ? "text-brand-600" : "text-red-500"}`}>
                  {sim.intervention.delta >= 0 ? "+" : ""}{formatINR(sim.intervention.delta)} vs. doing nothing
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Supply aggregation */}
        <div className="card p-6">
          <h2 className="font-display text-lg font-bold">🤝 Supply aggregation</h2>
          <p className="mt-1 text-sm text-stone-500">Combine small lots from nearby farms into one deliverable order.</p>
          <div className="mt-4 grid grid-cols-2 gap-4">
            <div>
              <label className="label">Crop</label>
              <select className="input" value={aggCrop} onChange={(e) => setAggCrop(e.target.value)}>
                {CROPS.map(([s, l]) => <option key={s} value={s}>{l}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Required (kg)</label>
              <input type="number" min="10" className="input" value={aggQty} onChange={(e) => setAggQty(e.target.value)} />
            </div>
          </div>
          <button className="btn-primary mt-4 w-full" onClick={runAgg} disabled={aggBusy}>{aggBusy ? "Optimising…" : "Find aggregated supply"}</button>

          {agg && (
            <div className="mt-5">
              <div className={`badge ${agg.complete ? "bg-brand-100 text-brand-700" : "bg-amber-100 text-amber-700"}`}>
                {agg.complete ? "✓ Requirement fulfilable" : `Partial: ${agg.fulfilled_kg} of ${agg.required_kg} kg`}
              </div>
              <div className="mt-3 space-y-2">
                {agg.farmers.map((f, i) => (
                  <div key={i} className="flex items-center justify-between rounded-xl bg-stone-50 px-4 py-2.5 text-sm">
                    <span>🌱 <b>{f.farm_name}</b> — {f.farmer_location} ({f.distance_km} km)</span>
                    <span className="font-medium">{f.take_kg} kg × {formatINR(f.price_per_kg)}</span>
                  </div>
                ))}
              </div>
              <div className="mt-4 grid grid-cols-3 gap-2 text-center">
                <div className="rounded-xl bg-stone-50 p-3">
                  <div className="font-display font-bold">{agg.farmer_count}</div>
                  <div className="text-[11px] text-stone-400">farms combined</div>
                </div>
                <div className="rounded-xl bg-stone-50 p-3">
                  <div className="font-display font-bold">{formatINR(agg.avg_price)}</div>
                  <div className="text-[11px] text-stone-400">avg ₹/kg</div>
                </div>
                <div className="rounded-xl bg-brand-50 p-3">
                  <div className="font-display font-bold text-brand-700">{formatINR(agg.farmers_net_payout)}</div>
                  <div className="text-[11px] text-brand-600">farmers' net</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
