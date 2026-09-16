"use client";

import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api, API_URL } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

const DISTRICTS = ["Ernakulam"];
const LOCATIONS = ["Kochi", "Ernakulam", "Aluva", "Tripunithura", "Kakkanad", "Mattancherry", "Paravur", "Vyttila"];

export default function OnboardingPage() {
  const { user, loading, refresh } = useAuth();
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [role, setRole] = useState<null | "buyer" | "vendor">(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    phone: "", dob: "", language: "en",
    farm_name: "", farm_area: "1", location: "Ernakulam", soil_type: "loamy", water_availability: "medium",
    business_name: "", buyer_type: "restaurant",
  });

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [loading, user, router]);

  function set(k: string, v: string) {
    setForm((f) => ({ ...f, [k]: v }));
  }

  async function submit() {
    if (!role) return;
    setBusy(true);
    setError("");
    try {
      await api(`${API_URL}`.length ? "/api/auth/onboard" : "/api/auth/onboard", {
        method: "POST",
        body: JSON.stringify({
          phone: form.phone,
          dob: form.dob || null,
          language: form.language,
          is_vendor: role === "vendor",
          farm_name: form.farm_name,
          farm_area: Number(form.farm_area) || 0,
          location: form.location,
          district: "Ernakulam",
          soil_type: form.soil_type,
          water_availability: form.water_availability,
          business_name: form.business_name,
          buyer_type: form.buyer_type,
        }),
      });
      await refresh();
      router.push(role === "vendor" ? "/vendor" : "/marketplace");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save profile");
      setBusy(false);
    }
  }

  if (loading || !user) return <div className="p-10 text-center text-stone-400">Loading…</div>;

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      {/* progress */}
      <div className="mb-8 flex items-center gap-3">
        {[1, 2].map((s) => (
          <div key={s} className="flex flex-1 items-center gap-3">
            <div className={`grid h-8 w-8 shrink-0 place-items-center rounded-full text-sm font-bold ${step >= s ? "bg-brand-600 text-white" : "bg-stone-200 text-stone-500"}`}>{s}</div>
            <div className={`h-1 flex-1 rounded-full ${step > s ? "bg-brand-500" : "bg-stone-200"}`} />
          </div>
        ))}
      </div>

      {step === 1 && (
        <div className="card animate-fadeUp p-8">
          <h1 className="font-display text-2xl font-bold">Complete your profile</h1>
          <p className="mt-1.5 text-sm text-stone-500">Just the basics — you can change these later.</p>
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <label className="label">Phone (optional)</label>
              <input className="input" value={form.phone} onChange={(e) => set("phone", e.target.value)} placeholder="+91 …" />
            </div>
            <div>
              <label className="label">Date of birth (optional)</label>
              <input type="date" className="input" value={form.dob} onChange={(e) => set("dob", e.target.value)} />
            </div>
            <div>
              <label className="label">Preferred language</label>
              <select className="input" value={form.language} onChange={(e) => set("language", e.target.value)}>
                <option value="en">English</option>
                <option value="ml">മലയാളം (Malayalam)</option>
                <option value="hi">हिन्दी (Hindi)</option>
                <option value="ta">தமிழ் (Tamil)</option>
              </select>
            </div>
          </div>
          <button className="btn-primary mt-6 w-full" onClick={() => setStep(2)}>Continue →</button>
        </div>
      )}

      {step === 2 && (
        <div className="animate-fadeUp">
          <h1 className="font-display text-2xl font-bold">Are you a farmer/vendor?</h1>
          <p className="mt-1.5 text-sm text-stone-500">This controls access to the AI vendor workspace. You can request a role change later.</p>

          {!role ? (
            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              <button onClick={() => setRole("buyer")} className="card group p-6 text-left transition hover:-translate-y-1 hover:shadow-lift">
                <span className="grid h-12 w-12 place-items-center rounded-xl bg-amber-100 text-2xl">🛒</span>
                <div className="mt-4 font-display text-lg font-bold">No, I'm a buyer/customer</div>
                <p className="mt-1 text-sm text-stone-500">Browse the marketplace, order fresh produce, track deliveries.</p>
              </button>
              <button onClick={() => setRole("vendor")} className="card group p-6 text-left transition hover:-translate-y-1 hover:shadow-lift">
                <span className="grid h-12 w-12 place-items-center rounded-xl bg-brand-100 text-2xl">🌾</span>
                <div className="mt-4 font-display text-lg font-bold">Yes, I'm a farmer/vendor</div>
                <p className="mt-1 text-sm text-stone-500">Everything buyers get — plus the AI vendor workspace: pricing, matching, aggregation.</p>
              </button>
            </div>
          ) : (
            <div className="card mt-6 p-8">
              {role === "vendor" ? (
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="sm:col-span-2">
                    <label className="label">Farm name</label>
                    <input className="input" value={form.farm_name} onChange={(e) => set("farm_name", e.target.value)} placeholder="e.g. Sunrise Farm" />
                  </div>
                  <div>
                    <label className="label">Farm area (acres)</label>
                    <input type="number" step="0.1" min="0" className="input" value={form.farm_area} onChange={(e) => set("farm_area", e.target.value)} />
                  </div>
                  <div>
                    <label className="label">Location</label>
                    <select className="input" value={form.location} onChange={(e) => set("location", e.target.value)}>
                      {LOCATIONS.map((l) => <option key={l}>{l}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="label">Soil type</label>
                    <select className="input" value={form.soil_type} onChange={(e) => set("soil_type", e.target.value)}>
                      <option value="loamy">Loamy</option>
                      <option value="clay">Clay</option>
                      <option value="sandy">Sandy</option>
                      <option value="laterite">Laterite</option>
                    </select>
                  </div>
                  <div>
                    <label className="label">Water availability</label>
                    <select className="input" value={form.water_availability} onChange={(e) => set("water_availability", e.target.value)}>
                      <option value="high">High</option>
                      <option value="medium">Medium</option>
                      <option value="low">Low</option>
                    </select>
                  </div>
                </div>
              ) : (
                <div className="grid gap-4 sm:grid-cols-2">
                  <div>
                    <label className="label">Business name (optional)</label>
                    <input className="input" value={form.business_name} onChange={(e) => set("business_name", e.target.value)} placeholder="e.g. Harbour Kitchen" />
                  </div>
                  <div>
                    <label className="label">I buy as a…</label>
                    <select className="input" value={form.buyer_type} onChange={(e) => set("buyer_type", e.target.value)}>
                      <option value="consumer">Household consumer</option>
                      <option value="restaurant">Restaurant</option>
                      <option value="retailer">Retailer</option>
                    </select>
                  </div>
                  <div className="sm:col-span-2">
                    <label className="label">Delivery location</label>
                    <select className="input" value={form.location} onChange={(e) => set("location", e.target.value)}>
                      {LOCATIONS.map((l) => <option key={l}>{l}</option>)}
                    </select>
                  </div>
                </div>
              )}
              {error && <div className="mt-4 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
              <div className="mt-6 flex gap-3">
                <button className="btn-secondary" onClick={() => setRole(null)} disabled={busy}>Back</button>
                <button className="btn-primary flex-1" onClick={submit} disabled={busy}>
                  {busy ? "Setting up…" : role === "vendor" ? "Create vendor workspace 🌱" : "Enter marketplace 🛒"}
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
