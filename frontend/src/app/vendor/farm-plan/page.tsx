"use client";

import { useEffect, useState } from "react";
import { api, formatINR } from "@/lib/api";

type Rec = {
  crop: string; name: string; emoji: string; harvest_days: number; demand: string;
  demand_score: number; avg_price: number; price_trend: number; expected_profit_per_kg: number;
  market_risk: string; risk_score: number; final_score: number;
};

export default function FarmPlanPage() {
  const [recs, setRecs] = useState<Rec[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    api<Rec[]>("/api/vendor/ai/crop-recommendation").then((r) => { setRecs(r); setLoaded(true); });
  }, []);

  if (!loaded) {
    return <div className="mt-8 space-y-3">{Array.from({ length: 3 }).map((_, i) => <div key={i} className="card h-28 animate-pulse-soft bg-stone-100/50" />)}</div>;
  }

  const top = recs[0];

  return (
    <div className="animate-fadeUp">
      <h1 className="font-display text-3xl font-bold tracking-tight">Farm Plan</h1>
      <p className="mt-1 text-stone-500">
        Ranked by <b>expected profit × probability of sale × (1 − risk)</b> — not price alone.
      </p>

      {top && (
        <div className="card mt-6 border-brand-200 bg-gradient-to-br from-brand-50 to-white p-6">
          <div className="badge bg-brand-600 text-white">Top recommendation</div>
          <div className="mt-3 flex flex-wrap items-center gap-4">
            <span className="text-4xl">{top.emoji}</span>
            <div>
              <div className="font-display text-2xl font-bold">{top.name}</div>
              <div className="text-sm text-stone-500">
                {top.demand} demand · harvest in ~{top.harvest_days} days · avg {formatINR(top.avg_price)}/kg
              </div>
            </div>
            <div className="ml-auto text-right">
              <div className="text-xs font-semibold uppercase tracking-wide text-stone-400">Score</div>
              <div className="font-display text-3xl font-bold text-brand-700">{top.final_score.toFixed(1)}</div>
            </div>
          </div>
        </div>
      )}

      <div className="mt-6 space-y-3">
        {recs.map((r, rank) => (
          <div key={r.crop} className="card flex flex-wrap items-center gap-5 p-5">
            <div className="grid h-10 w-10 shrink-0 place-items-center rounded-full bg-stone-100 font-display font-bold text-stone-500">{rank + 1}</div>
            <span className="text-3xl">{r.emoji}</span>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-semibold">{r.name}</span>
                <span className={`badge ${r.demand === "High" ? "bg-brand-100 text-brand-700" : "bg-amber-100 text-amber-700"}`}>{r.demand} demand</span>
                <span className={`badge ${r.market_risk === "Low" ? "bg-brand-100 text-brand-700" : r.market_risk === "Medium" ? "bg-amber-100 text-amber-700" : "bg-red-100 text-red-600"}`}>
                  {r.market_risk} risk
                </span>
              </div>
              <div className="mt-1 text-sm text-stone-500">
                ~{r.harvest_days} days to harvest · {formatINR(r.avg_price)}/kg avg ({r.price_trend >= 0 ? "+" : ""}{r.price_trend}% trend) · profit ≈ {formatINR(r.expected_profit_per_kg)}/kg
              </div>
            </div>
            <div className="text-right">
              <div className="font-display text-xl font-bold">{r.final_score.toFixed(1)}</div>
              <div className="text-[11px] text-stone-400">final score</div>
            </div>
          </div>
        ))}
      </div>

      <p className="mt-6 rounded-xl bg-stone-100 p-4 text-xs leading-relaxed text-stone-500">
        Recommendations are advisory estimates from local demand signals and 60-day price history. A crop with a
        theoretical high price but uncertain demand may rank below a reliable, slightly lower-margin crop — the model
        optimises expected profit × probability of successful sale, and adjusts for your district's conditions.
      </p>
    </div>
  );
}
