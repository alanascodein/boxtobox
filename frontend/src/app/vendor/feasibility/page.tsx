"use client";

import { useEffect, useState } from "react";
import { api, formatINR } from "@/lib/api";

/* AMIE Feasibility Lab (AMIE_Final_Revised_PRD.md §21):
   Command Center → Future Timeline → Why? → Intervention Lab → Counterfactual.
   Every number shown comes from the deterministic backend engine — nothing hard-coded. */

type Day = {
  day: number; date: string; status: "GREEN" | "AMBER" | "RED";
  arrivals_kg: number; redirected_kg: number; processed_kg: number; stored_kg: number;
  procured_kg: number; spill_kg: number; spoilage_kg: number;
  demand_kg: number; absorbed_kg: number; unabsorbed_kg: number;
  store_end_kg: number; backlog_end_kg: number;
  proc_required_kg: number; proc_capacity_kg: number;
  proc_utilization_pct: number; storage_utilization_pct: number;
};

type Failure = {
  day: number; node: string; node_name: string; node_type: string;
  required_kg: number; capacity_kg: number; deficit_kg: number;
  why: string; trigger: string;
  named_processor: { id: string; name: string; capacity_kg: number; required_kg: number; deficit_kg: number } | null;
};

type CriticalSet = {
  commitments: { id: string; farm: string; location: string; day: number; kg: number; unabsorbed_reduction_kg: number }[];
  combined_kg: number; residual_unabsorbed_kg: number; note: string;
};

type Option = {
  types: string[]; label: string;
  quantities_kg: Record<string, number>;
  rescued_kg: number; residual_kg: number; cost: number; rescued_value: number;
  net_benefit: number; cost_per_kg: number | null; status_after: string; farmer_disruption: number;
};

type Analysis = {
  status: string; label: string; price_avg: number; price_trend_pct: number;
  demand_level: number;
  balance_ratio: number | null; confidence: string; note: string;
  price_source?: string; price_source_detail?: string;
};

type Counterfactual = {
  types: string[]; label: string;
  baseline: { status: string; first_failure_day: number | null; unabsorbed_kg: number; spoilage_kg: number; absorbed_kg: number; cost: number };
  after: { status: string; first_failure_day: number | null; unabsorbed_kg: number; spoilage_kg: number; absorbed_kg: number; cost: number };
  rescued_kg: number; residual_kg: number; cost: number; rescued_value: number; net_benefit: number;
  timeline_after: Day[];
};

type AmieResult = {
  crop: string; crop_name: string; emoji: string; district: string; horizon_days: number;
  scenario_name: string; scenario_label: string; seed: number;
  system_status: "GREEN" | "AMBER" | "RED" | "BLACK";
  market_analysis: Analysis;
  timeline: Day[];
  first_failure: Failure | null;
  bottlenecks: { id: string; name: string; type: string; peak_utilization_pct: number; capacity_kg_day: number; deficit_kg: number }[];
  totals: Record<string, number>;
  peak_utilization_pct: number;
  uncertainty: Record<string, { status: string; unabsorbed_kg: number; first_failure_day: number | null }>;
  detection_lead_time_hours: number | null;
  critical_commitments: CriticalSet;
  intervention_options: Option[];
  best_intervention: Option | null;
  counterfactual: Counterfactual | null;
  assumptions: string[];
  labels: { banner: string; note: string };
};

type CfResult = { counterfactual: Counterfactual; system_status_before: string };

const CROPS = [
  ["tomato", "🍅 Tomato"], ["green_chilli", "🌶️ Green Chilli"], ["beans", "🫛 Beans"],
  ["cucumber", "🥒 Cucumber"], ["banana", "🍌 Banana"], ["spinach", "🥬 Spinach"],
];

const STATUS_STYLES: Record<string, string> = {
  GREEN: "bg-brand-100 text-brand-700", AMBER: "bg-amber-100 text-amber-700",
  RED: "bg-red-100 text-red-700", BLACK: "bg-stone-800 text-white",
  FEASIBLE: "bg-brand-100 text-brand-700", INFEASIBLE: "bg-red-100 text-red-700",
  HEALTHY: "bg-brand-100 text-brand-700", TIGHT: "bg-amber-100 text-amber-700",
  SOFT: "bg-blue-100 text-blue-700", IMBALANCED: "bg-red-100 text-red-700", UNKNOWN: "bg-stone-100 text-stone-600",
};

const badgeStyle = (s: string | undefined) => (s && STATUS_STYLES[s]) || "bg-stone-100 text-stone-600";

const DAY_STYLES: Record<string, string> = {
  GREEN: "bg-brand-500/90 text-white", AMBER: "bg-amber-400/90 text-white", RED: "bg-red-500/90 text-white",
};

const OPTION_ICON: Record<string, string> = {
  REDIRECT: "🚚", STORE: "🏬", RESCHEDULE: "🗓️", PROCESS: "🏭", PROCURE: "🏛️",
};

export default function FeasibilityLabPage() {
  const [crop, setCrop] = useState("tomato");
  const [scenario, setScenario] = useState("synchronized_harvest");
  const [scenarios, setScenarios] = useState<{ name: string; label: string }[]>([]);
  const [result, setResult] = useState<AmieResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [showAssumptions, setShowAssumptions] = useState(false);
  const [cf, setCf] = useState<CfResult | null>(null);
  const [cfBusy, setCfBusy] = useState(false);

  useEffect(() => {
    api<{ name: string; label: string }[]>("/api/vendor/amie/scenarios").then(setScenarios).catch(() => {});
  }, []);

  async function runAmie() {
    setBusy(true); setErr(""); setCf(null);
    try {
      const r = await api<AmieResult>("/api/vendor/amie/analyze", {
        method: "POST",
        body: JSON.stringify({ crop, scenario, horizon_days: 7, seed: 42 }),
      });
      setResult(r);
    } catch (e) {
      setErr(e instanceof Error ? e.message : "AMIE run failed");
    } finally {
      setBusy(false);
    }
  }

  async function runSelection(types: string[]) {
    if (!result) return;
    setCfBusy(true);
    try {
      const r = await api<CfResult>("/api/vendor/amie/counterfactual", {
        method: "POST",
        body: JSON.stringify({ crop, scenario, horizon_days: 7, seed: 42, interventions: types }),
      });
      setCf(r);
    } finally {
      setCfBusy(false);
    }
  }

  return (
    <div className="animate-fadeUp">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl font-bold tracking-tight">Feasibility Lab</h1>
          <p className="mt-1 text-stone-500">
            AMIE simulates the next 7 days day-by-day and detects when the market physically breaks.
          </p>
        </div>
        <span className="badge bg-stone-100 text-stone-500">deterministic engine · no LLM</span>
      </div>

      {/* Command center */}
      <div className="card mt-6 p-6">
        <div className="grid gap-4 sm:grid-cols-3">
          <div>
            <label className="label">Commodity</label>
            <select className="input" value={crop} onChange={(e) => setCrop(e.target.value)}>
              {CROPS.map(([s, l]) => <option key={s} value={s}>{l}</option>)}
            </select>
          </div>
          <div className="sm:col-span-2">
            <label className="label">Disturbance scenario</label>
            <select className="input" value={scenario} onChange={(e) => setScenario(e.target.value)}>
              {(scenarios.length ? scenarios : [{ name: scenario, label: "Synchronized harvest" }]).map((s) => (
                <option key={s.name} value={s.name}>{s.label}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="mt-4 flex flex-wrap items-center gap-3">
          <button className="btn-primary" onClick={runAmie} disabled={busy}>
            {busy ? "Simulating 7 days…" : "▶ Run AMIE"}
          </button>
          <span className="text-xs text-stone-400">seed 42 · reproducible</span>
        </div>
      </div>

      {err && <div className="mt-4 rounded-xl bg-red-50 p-4 text-sm text-red-600">{err}</div>}

      {result && (
        <>
          {/* Synthetic-data banner (PRD §9) */}
          <div className="mt-6 rounded-xl border border-amber-200 bg-amber-50 px-4 py-2.5 text-xs text-amber-700">
            ⚠️ {result.labels.banner} — commitments, capacities and buyers are synthetic;
            prices &amp; demand are anchored on live market data.
          </div>

          {/* Current market vs future */}
          <div className="mt-4 grid gap-4 lg:grid-cols-3">
            <div className="card p-5">
              <div className="flex items-center justify-between">
                <div className="text-sm text-stone-500">Current market ({result.crop_name})</div>
                <span className={`badge ${badgeStyle(result.market_analysis.status)}`}>{result.market_analysis.status}</span>
              </div>
              <div className="mt-3 font-display text-2xl font-bold">{formatINR(result.market_analysis.price_avg)}<span className="text-sm font-medium text-stone-400">/kg</span></div>
              <div className={`text-xs ${result.market_analysis.price_trend_pct >= 0 ? "text-brand-600" : "text-red-500"}`}>
                {result.market_analysis.price_trend_pct >= 0 ? "▲" : "▼"} {Math.abs(result.market_analysis.price_trend_pct)}% 14d trend
              </div>
              <div className="mt-2 text-[11px] leading-snug text-stone-400">{result.market_analysis.label}</div>
              {result.market_analysis.price_source && (
                <div className={`mt-2 text-[11px] font-medium ${result.market_analysis.price_source.startsWith("real") ? "text-brand-600" : "text-amber-600"}`}>
                  {result.market_analysis.price_source.startsWith("real") ? "✓ " : "⚠ "}
                  Prices: {result.market_analysis.price_source}
                  {result.market_analysis.price_source_detail ? ` — ${result.market_analysis.price_source_detail}` : ""}
                </div>
              )}
            </div>

            <div className="card p-5 lg:col-span-2">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="text-sm text-stone-500">Simulated future — {result.scenario_label}</div>
                <div className="flex items-center gap-2">
                  {Object.entries(result.uncertainty).map(([band, u]) => (
                    <span key={band} className={`badge ${badgeStyle(u.status)}`}>{band}</span>
                  ))}
                </div>
              </div>
              <div className="mt-3 flex items-end gap-2">
                <div className="font-display text-4xl font-extrabold">
                  {result.system_status === "GREEN" ? "Feasible" : result.system_status === "AMBER" ? "Strained" : "Infeasible"}
                </div>
                <span className={`badge mb-1.5 ${badgeStyle(result.system_status)}`}>{result.system_status}</span>
              </div>
              {/* Timeline (PRD §21 page 2) */}
              <div className="mt-4 flex gap-1.5">
                {result.timeline.map((d) => (
                  <div key={d.day} className="flex-1">
                    <div className={`grid h-16 place-items-center rounded-xl font-display text-sm font-bold text-white ${DAY_STYLES[d.status]}`}
                      title={`Day ${d.day}: ${d.status} · arrivals ${Math.round(d.arrivals_kg)} kg · unabsorbed ${Math.round(d.unabsorbed_kg)} kg`}>
                      D{d.day}
                    </div>
                    <div className="mt-1 text-center text-[10px] text-stone-400">
                      {d.unabsorbed_kg > 0.5 ? `${Math.round(d.unabsorbed_kg)} kg lost` : `${Math.round(d.proc_utilization_pct)}%`}
                    </div>
                  </div>
                ))}
              </div>
              {result.detection_lead_time_hours != null && (
                <div className="mt-3 text-sm font-medium text-red-600">
                  ⚡ Future infeasibility detected — {result.detection_lead_time_hours} h before failure
                </div>
              )}
            </div>
          </div>

          {/* Why? (PRD §21 page 4) */}
          {result.first_failure && (
            <div className="card mt-4 border-red-200 p-6">
              <h2 className="font-display text-lg font-bold text-red-600">Why does the market fail?</h2>
              <div className="mt-4 grid gap-4 sm:grid-cols-4">
                <div className="rounded-xl bg-stone-50 p-4">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-stone-400">Where / when</div>
                  <div className="mt-1 text-sm font-bold">{result.first_failure.node_name}</div>
                  <div className="text-xs text-stone-500">Day {result.first_failure.day}</div>
                </div>
                <div className="rounded-xl bg-stone-50 p-4">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-stone-400">Required</div>
                  <div className="mt-1 font-display text-lg font-bold">{Math.round(result.first_failure.required_kg).toLocaleString()} kg</div>
                </div>
                <div className="rounded-xl bg-stone-50 p-4">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-stone-400">Capacity</div>
                  <div className="mt-1 font-display text-lg font-bold">{Math.round(result.first_failure.capacity_kg).toLocaleString()} kg</div>
                </div>
                <div className="rounded-xl bg-red-50 p-4">
                  <div className="text-[11px] font-semibold uppercase tracking-wide text-red-400">Deficit</div>
                  <div className="mt-1 font-display text-lg font-bold text-red-600">{Math.round(result.first_failure.deficit_kg).toLocaleString()} kg</div>
                </div>
              </div>
              <div className="mt-4 text-sm text-stone-600">
                <b>Why:</b> {result.first_failure.why}. <b>Trigger:</b> {result.first_failure.trigger}.
              </div>
              <div className="mt-4">
                <div className="text-xs font-semibold uppercase tracking-wide text-stone-400">Ranked bottlenecks</div>
                <div className="mt-2 space-y-2">
                  {result.bottlenecks.slice(0, 4).map((b) => (
                    <div key={b.id} className="flex items-center gap-3">
                      <span className="w-40 shrink-0 truncate text-sm">{b.id} · {b.name}</span>
                      <div className="h-2.5 flex-1 overflow-hidden rounded-full bg-stone-100">
                        <div className={`h-full rounded-full ${b.peak_utilization_pct >= 100 ? "bg-red-500" : b.peak_utilization_pct >= 75 ? "bg-amber-400" : "bg-brand-500"}`}
                          style={{ width: `${Math.min(100, b.peak_utilization_pct)}%` }} />
                      </div>
                      <span className="w-24 shrink-0 text-right text-xs text-stone-500">
                        {Math.round(b.peak_utilization_pct)}%{b.deficit_kg > 0.5 ? ` · −${Math.round(b.deficit_kg)} kg` : ""}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Critical commitments (PRD §14) */}
          {result.critical_commitments.commitments.length > 0 && (
            <div className="card mt-4 p-6">
              <h2 className="font-display text-lg font-bold">⚠️ Critical commitments</h2>
              <p className="mt-1 text-sm text-stone-500">{result.critical_commitments.note}</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {result.critical_commitments.commitments.map((c) => (
                  <div key={c.id} className="rounded-xl bg-stone-50 px-4 py-2.5 text-sm">
                    <b>{c.id}</b> · {c.farm} · day {c.day} · <b>{Math.round(c.kg)} kg</b>
                    <span className="ml-1 text-xs text-stone-400">(−{Math.round(c.unabsorbed_reduction_kg)} kg infeasibility if shifted)</span>
                  </div>
                ))}
              </div>
              <div className="mt-3 text-sm text-stone-600">
                Combined: <b>{Math.round(result.critical_commitments.combined_kg).toLocaleString()} kg</b>
                {result.critical_commitments.residual_unabsorbed_kg > 0.5 && (
                  <> · residual infeasibility after removal: {Math.round(result.critical_commitments.residual_unabsorbed_kg).toLocaleString()} kg</>
                )}
              </div>
            </div>
          )}

          {/* Intervention lab (PRD §21 page 5) */}
          {result.intervention_options.length > 0 && (
            <div className="card mt-4 p-6">
              <h2 className="font-display text-lg font-bold">🧪 Intervention lab</h2>
              <p className="mt-1 text-sm text-stone-500">
                Each option is re-simulated through the same cascade. Sizes are derived from the measured deficit.
              </p>
              <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                {result.intervention_options.map((o, i) => (
                  <div key={o.types.join("+")} className={`rounded-2xl border p-4 ${i === 0 ? "border-brand-300 bg-brand-50/50" : "border-stone-200"}`}>
                    <div className="flex items-center justify-between">
                      <div className="flex gap-1">{o.types.map((t) => <span key={t} title={t}>{OPTION_ICON[t]}</span>)}</div>
                      {i === 0 && <span className="badge bg-brand-100 text-brand-700">cheapest fix</span>}
                    </div>
                    <div className="mt-2 text-sm font-bold">{o.label}</div>
                    <div className="mt-1 text-xs text-stone-500">
                      {o.types.map((t) => `${Math.round(o.quantities_kg[t] || 0)} kg ${t.toLowerCase()}`).join(" + ")}
                    </div>
                    <div className="mt-3 grid grid-cols-3 gap-1.5 text-center text-xs">
                      <div className="rounded-lg bg-white p-2">
                        <div className="font-display font-bold">{Math.round(o.rescued_kg).toLocaleString()}</div>
                        <div className="text-stone-400">kg rescued</div>
                      </div>
                      <div className="rounded-lg bg-white p-2">
                        <div className="font-display font-bold">{formatINR(o.cost)}</div>
                        <div className="text-stone-400">cost</div>
                      </div>
                      <div className={`rounded-lg p-2 ${o.residual_kg <= 0.5 ? "bg-brand-50" : "bg-amber-50"}`}>
                        <div className="font-display font-bold">{o.residual_kg <= 0.5 ? "0" : Math.round(o.residual_kg).toLocaleString()}</div>
                        <div className="text-stone-400">kg residual</div>
                      </div>
                    </div>
                    <div className="mt-2 flex items-center justify-between text-xs">
                      <span className={o.net_benefit >= 0 ? "font-semibold text-brand-600" : "font-semibold text-red-500"}>
                        net {o.net_benefit >= 0 ? "+" : ""}{formatINR(o.net_benefit)}
                      </span>
                      <button className="btn-ghost" onClick={() => runSelection(o.types)} disabled={cfBusy}>
                        {cfBusy ? "…" : "simulate →"}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Counterfactual (PRD §21 page 6) */}
          {(cf || result.counterfactual) && (
            (() => {
              // cf is the API wrapper { counterfactual }, result.counterfactual is already the object
              const c = (cf ? cf.counterfactual : result.counterfactual) as Counterfactual;
              if (!c?.baseline || !c?.after) return null;
              return (
                <div className="card mt-4 p-6">
                  <h2 className="font-display text-lg font-bold">⚖️ Counterfactual — {c.label}</h2>
                  <div className="mt-4 grid gap-4 sm:grid-cols-2">
                    <div className="rounded-2xl bg-red-50 p-5">
                      <div className="text-xs font-semibold uppercase tracking-wide text-red-400">No intervention</div>
                      <div className={`mt-2 badge ${badgeStyle(c.baseline.status)}`}>{c.baseline.status}</div>
                      <div className="mt-3 space-y-1.5 text-sm">
                        <div>Failure: <b>{c.baseline.first_failure_day ? `day ${c.baseline.first_failure_day}` : "none"}</b></div>
                        <div>Unabsorbed: <b>{Math.round(c.baseline.unabsorbed_kg).toLocaleString()} kg</b></div>
                        <div>Spoiled: <b>{Math.round(c.baseline.spoilage_kg).toLocaleString()} kg</b></div>
                        <div>Cost: <b>{formatINR(0)}</b></div>
                      </div>
                    </div>
                    <div className="rounded-2xl bg-brand-50 p-5">
                      <div className="text-xs font-semibold uppercase tracking-wide text-brand-600">With AMIE intervention</div>
                      <div className={`mt-2 badge ${badgeStyle(c.after.status)}`}>{c.after.status}</div>
                      <div className="mt-3 space-y-1.5 text-sm">
                        <div>Failure: <b>{c.after.first_failure_day ? `day ${c.after.first_failure_day}` : "none"}</b></div>
                        <div>Unabsorbed: <b>{Math.round(c.after.unabsorbed_kg).toLocaleString()} kg</b></div>
                        <div>Spoiled: <b>{Math.round(c.after.spoilage_kg).toLocaleString()} kg</b></div>
                        <div>Intervention cost: <b>{formatINR(c.cost)}</b></div>
                      </div>
                    </div>
                  </div>
                  <div className="mt-4 flex flex-wrap items-center gap-4 text-sm">
                    <span>Produce rescued: <b>{Math.round(c.rescued_kg).toLocaleString()} kg</b></span>
                    <span>Rescued value: <b>≈ {formatINR(c.rescued_value)}</b></span>
                    <span className={c.net_benefit >= 0 ? "font-bold text-brand-600" : "font-bold text-red-500"}>
                      Net benefit: {c.net_benefit >= 0 ? "+" : ""}{formatINR(c.net_benefit)}
                    </span>
                  </div>
                  {/* after-timeline */}
                  <div className="mt-4 flex gap-1.5">
                    {c.timeline_after.map((d) => (
                      <div key={d.day} className="flex-1">
                        <div className={`grid h-10 place-items-center rounded-lg text-xs font-bold text-white ${DAY_STYLES[d.status]}`}>D{d.day}</div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })()
          )}

          {/* Assumptions (PRD §2.6: every output exposes assumptions) */}
          <div className="card mt-4 p-6">
            <button className="flex w-full items-center justify-between" onClick={() => setShowAssumptions(!showAssumptions)}>
              <span className="font-display text-lg font-bold">📋 Assumptions &amp; calculation path</span>
              <span className="text-stone-400">{showAssumptions ? "hide" : "show"}</span>
            </button>
            {showAssumptions && (
              <div className="mt-4 space-y-3">
                <div className="text-sm text-stone-600">
                  <b>Path:</b> live market data → synthetic scenario → day-by-day cascade
                  (arrivals → redirect → process → store/overflow → procure → absorb) → bottleneck → interventions → re-simulation.
                </div>
                <ul className="list-inside list-disc space-y-1 text-sm text-stone-500">
                  {result.assumptions.map((a, i) => <li key={i}>{a}</li>)}
                </ul>
              </div>
            )}
          </div>
        </>
      )}

      {!result && !busy && (
        <div className="card mt-6 grid place-items-center p-12 text-center">
          <span className="text-5xl">🧭</span>
          <h3 className="mt-4 font-display text-lg font-bold">The market looks fine today. Will it stay that way?</h3>
          <p className="mt-1 max-w-md text-sm text-stone-500">
            Pick a commodity and a disturbance scenario, then run AMIE. It reconstructs the future
            day-by-day and tells you exactly when, where and why the market breaks — and what the cheapest fix is.
          </p>
        </div>
      )}
    </div>
  );
}
