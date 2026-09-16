"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useAuth } from "@/lib/auth-context";

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const u = await login(email, password);
      if (!u.onboarded) router.push("/onboarding");
      else if (u.role === "VENDOR") router.push("/vendor");
      else if (u.role === "ADMIN") router.push("/admin");
      else router.push("/marketplace");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
      setBusy(false);
    }
  }

  function quickFill(kind: "vendor" | "buyer" | "admin") {
    if (kind === "vendor") { setEmail("ravi@farmmesh.demo"); setPassword("farm1234"); }
    else if (kind === "buyer") { setEmail("chef@harbourkitchen.demo"); setPassword("buyer1234"); }
    else { setEmail("admin@farmmesh.demo"); setPassword("admin1234"); }
  }

  return (
    <div className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-md flex-col justify-center px-4 py-12">
      <div className="card p-8">
        <h1 className="font-display text-2xl font-bold">Welcome back</h1>
        <p className="mt-1.5 text-sm text-stone-500">Sign in to your FarmMesh account.</p>

        <form onSubmit={submit} className="mt-6 space-y-4">
          <div>
            <label className="label" htmlFor="email">Email</label>
            <input id="email" type="email" className="input" value={email} onChange={(e) => setEmail(e.target.value)} required />
          </div>
          <div>
            <label className="label" htmlFor="password">Password</label>
            <input id="password" type="password" className="input" value={password} onChange={(e) => setPassword(e.target.value)} required />
          </div>
          {error && <div className="rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
          <button type="submit" className="btn-primary w-full" disabled={busy}>
            {busy ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <div className="mt-6 rounded-xl bg-stone-50 p-4">
          <div className="mb-2 text-xs font-semibold uppercase tracking-wide text-stone-400">Demo accounts</div>
          <div className="flex flex-wrap gap-2">
            <button onClick={() => quickFill("vendor")} className="badge bg-brand-100 text-brand-800 hover:bg-brand-200">🌱 Farmer</button>
            <button onClick={() => quickFill("buyer")} className="badge bg-amber-100 text-amber-800 hover:bg-amber-200">🍽️ Restaurant buyer</button>
            <button onClick={() => quickFill("admin")} className="badge bg-stone-200 text-stone-700 hover:bg-stone-300">🛡️ Admin</button>
          </div>
        </div>

        <p className="mt-6 text-center text-sm text-stone-500">
          New here?{" "}
          <Link href="/signup" className="font-semibold text-brand-700 hover:underline">Create an account</Link>
        </p>
      </div>
    </div>
  );
}
