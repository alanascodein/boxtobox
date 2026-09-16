"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { api, formatINR } from "@/lib/api";

type Analysis = {
  crop: string; crop_name: string; emoji: string; confidence: number; estimated_quality: string;
  visible_defects: string[]; quantity_kg: number | null; _needs_manual_crop: boolean;
  suggested_price_range: { min: number; max: number }; price_confidence: string; price_reasons: string[];
};

const CROPS = [
  ["tomato", "🍅 Tomato"], ["green_chilli", "🌶️ Green Chilli"], ["beans", "🫛 Beans"],
  ["cucumber", "🥒 Cucumber"], ["banana", "🍌 Banana"], ["spinach", "🥬 Spinach"],
];

export default function SellPage() {
  const router = useRouter();
  const [stage, setStage] = useState<"capture" | "analyzing" | "review" | "done">("capture");
  const [voiceText, setVoiceText] = useState("");
  const [manualCrop, setManualCrop] = useState("");
  const [qty, setQty] = useState("");
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [listing, setListing] = useState({ title: "", description: "" });
  const [price, setPrice] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [publishedId, setPublishedId] = useState("");

  async function analyze() {
    setError("");
    if (!voiceText.trim() && !manualCrop) {
      setError("Describe your harvest (e.g. \"30 kg green chilli harvested today\") or pick the crop manually.");
      return;
    }
    setStage("analyzing");
    try {
      const a = await api<Analysis>("/api/vendor/ai/analyze-harvest", {
        method: "POST",
        body: JSON.stringify({ crop_hint: voiceText, quantity_kg: qty ? Number(qty) : null }),
      });
      setAnalysis(a);
      setQty((prev) => prev || (a.quantity_kg ? String(a.quantity_kg) : "30"));
      setPrice(String(Math.round(((a.suggested_price_range.min + a.suggested_price_range.max) / 2) * 10) / 10));
      // generate listing text
      const gen = await api<{ title: string; description: string }>("/api/vendor/ai/generate-listing", {
        method: "POST",
        body: JSON.stringify({
          crop: manualCrop || a.crop, quantity_kg: Number(qty || a.quantity_kg || 30),
          quality_grade: a.estimated_quality, harvest_label: "today",
        }),
      });
      setListing({ title: gen.title, description: gen.description });
      setStage("review");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
      setStage("capture");
    }
  }

  async function publish() {
    setBusy(true);
    setError("");
    try {
      const l = await api<{ id: string }>("/api/listings", {
        method: "POST",
        body: JSON.stringify({
          crop: manualCrop || analysis?.crop, title: listing.title, description: listing.description,
          quantity_kg: Number(qty), price_per_kg: Number(price), quality_grade: analysis?.estimated_quality || "A",
          ai_generated: true,
        }),
      });
      setPublishedId(l.id);
      setStage("done");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to publish");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="animate-fadeUp">
      <h1 className="font-display text-3xl font-bold tracking-tight">Sell a harvest</h1>
      <p className="mt-1 text-stone-500">Three steps: describe → review AI analysis → publish.</p>

      {/* Stepper */}
      <div className="mt-6 flex items-center gap-2 text-xs font-semibold">
        {["Describe", "Review", "Publish"].map((s, i) => {
          const idx = ["capture", "review", "done"].indexOf(stage === "analyzing" ? "capture" : stage);
          const active = i === Math.max(0, idx);
          return (
            <div key={s} className={`flex items-center gap-2 rounded-full px-3 py-1.5 ${active ? "bg-brand-600 text-white" : "bg-stone-100 text-stone-500"}`}>
              <span>{i + 1}</span>{s}
            </div>
          );
        })}
      </div>

      {stage === "capture" && (
        <div className="card mt-6 p-8">
          <div className="mx-auto grid max-w-xl place-items-center rounded-3xl border-2 border-dashed border-brand-200 bg-brand-50/50 p-10 text-center">
            <span className="text-5xl">📸</span>
            <div className="mt-3 font-display text-lg font-bold">Photograph or describe your harvest</div>
            <p className="mt-1 text-sm text-stone-500">
              In production this uses your camera + voice. For this demo, type what you harvested.
            </p>
            <textarea
              className="input mt-5 min-h-24 w-full"
              placeholder='e.g. "I have 30 kilos of green chilli, harvested today"'
              value={voiceText}
              onChange={(e) => setVoiceText(e.target.value)}
            />
            <div className="mt-4 w-full">
              <label className="label">Or pick the crop manually</label>
              <div className="flex flex-wrap gap-2">
                {CROPS.map(([slug, label]) => (
                  <button key={slug} onClick={() => setManualCrop(manualCrop === slug ? "" : slug)}
                    className={`badge px-3 py-1.5 ${manualCrop === slug ? "bg-brand-600 text-white" : "bg-white text-stone-700 shadow-card hover:bg-brand-50"}`}>
                    {label}
                  </button>
                ))}
              </div>
            </div>
          </div>
          {error && <div className="mx-auto mt-4 max-w-xl rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
          <div className="mt-6 text-center">
            <button className="btn-primary !px-8 !py-3" onClick={analyze}>✨ Analyze harvest</button>
          </div>
        </div>
      )}

      {stage === "analyzing" && (
        <div className="card mt-6 p-14 text-center">
          <div className="text-4xl">🤖</div>
          <div className="mt-3 font-display text-lg font-bold animate-pulse-soft">AI analyzing your harvest…</div>
          <div className="mx-auto mt-4 h-1.5 w-56 overflow-hidden rounded-full bg-stone-100">
            <div className="h-full w-1/3 animate-pulse-soft rounded-full bg-brand-500" />
          </div>
        </div>
      )}

      {stage === "review" && analysis && (
        <div className="mt-6 grid gap-6 lg:grid-cols-2">
          {/* AI analysis */}
          <div className="card p-6">
            <div className="badge bg-brand-100 text-brand-700">AI analysis</div>
            <div className="mt-4 flex items-center gap-4">
              <span className="grid h-16 w-16 place-items-center rounded-2xl bg-stone-50 text-4xl">{analysis.emoji}</span>
              <div>
                <div className="font-display text-xl font-bold">{analysis.crop_name}</div>
                <div className="text-sm text-stone-500">
                  Visual grade <b className="text-stone-700">{analysis.estimated_quality}</b> · confidence {(analysis.confidence * 100).toFixed(0)}%
                </div>
              </div>
            </div>

            {analysis._needs_manual_crop && (
              <div className="mt-4 rounded-xl bg-amber-50 p-3 text-sm text-amber-800">
                We couldn't confidently identify this crop — please confirm it manually before publishing.
              </div>
            )}

            <div className="mt-5 rounded-xl bg-stone-50 p-4">
              <div className="text-xs font-semibold uppercase tracking-wide text-stone-400">Suggested price range</div>
              <div className="font-display text-2xl font-bold text-brand-700">
                {formatINR(analysis.suggested_price_range.min)} – {formatINR(analysis.suggested_price_range.max)}<span className="text-sm font-medium text-stone-400">/kg</span>
              </div>
              <div className="mt-1 text-xs text-stone-500">Confidence: {analysis.price_confidence} · Estimated market range — not a guaranteed price</div>
              <ul className="mt-3 space-y-1 text-sm text-stone-600">
                {analysis.price_reasons.map((r) => <li key={r}>• {r}</li>)}
              </ul>
            </div>
          </div>

          {/* Listing draft */}
          <div className="card p-6">
            <div className="badge bg-blue-100 text-blue-700">Listing draft — editable</div>
            <div className="mt-4 space-y-4">
              <div>
                <label className="label">Title</label>
                <input className="input" value={listing.title} onChange={(e) => setListing({ ...listing, title: e.target.value })} />
              </div>
              <div>
                <label className="label">Description</label>
                <textarea className="input min-h-28" value={listing.description} onChange={(e) => setListing({ ...listing, description: e.target.value })} />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="label">Quantity (kg)</label>
                  <input type="number" min="1" className="input" value={qty} onChange={(e) => setQty(e.target.value)} />
                </div>
                <div>
                  <label className="label">Your price (₹/kg)</label>
                  <input type="number" step="0.5" min="1" className="input" value={price} onChange={(e) => setPrice(e.target.value)} />
                </div>
              </div>
              <div className="rounded-xl bg-brand-50 p-3 text-sm text-brand-800">
                At {formatINR(Number(price) || 0)}/kg · gross {formatINR((Number(price) || 0) * (Number(qty) || 0))}
                <span className="text-brand-600"> · est. net after fees ≈ {formatINR((Number(price) || 0) * (Number(qty) || 0) * 0.94)}</span>
              </div>
              {error && <div className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
              <div className="flex gap-3">
                <button className="btn-secondary" onClick={() => setStage("capture")} disabled={busy}>← Redescribe</button>
                <button className="btn-primary flex-1" onClick={publish} disabled={busy}>
                  {busy ? "Publishing…" : "Publish listing 🚀"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {stage === "done" && (
        <div className="card mt-6 p-12 text-center">
          <div className="text-5xl">🎉</div>
          <h2 className="mt-4 font-display text-2xl font-bold">Listing is live!</h2>
          <p className="mt-2 text-stone-500">Buyers near you will see it immediately. AI matching will surface buyer requests.</p>
          <div className="mt-6 flex flex-wrap justify-center gap-3">
            <Link href="/vendor/listings" className="btn-primary">View my listings</Link>
            <Link href="/vendor/sell" className="btn-secondary">Sell another</Link>
          </div>
        </div>
      )}
    </div>
  );
}
