"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import CopilotDrawer from "@/components/CopilotDrawer";
import { useAuth } from "@/lib/auth-context";

const NAV = [
  { href: "/vendor", label: "Dashboard", emoji: "🏠" },
  { href: "/vendor/sell", label: "Sell Harvest", emoji: "📸" },
  { href: "/vendor/listings", label: "My Listings", emoji: "🧺" },
  { href: "/vendor/market-intel", label: "Market Intel", emoji: "📊" },
  { href: "/vendor/feasibility", label: "Feasibility Lab", emoji: "🧭" },
  { href: "/vendor/farm-plan", label: "Farm Plan", emoji: "🌾" },
  { href: "/vendor/earnings", label: "Earnings", emoji: "💰" },
];

export default function VendorLayout({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && (!user || user.role === "STANDARD_USER")) {
      router.replace(user ? "/marketplace" : "/login");
    }
  }, [user, loading, router]);

  if (loading || !user || user.role === "STANDARD_USER") {
    return <div className="p-10 text-center text-stone-400">Loading workspace…</div>;
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
      <div className="grid gap-8 lg:grid-cols-[220px_1fr]">
        <aside className="lg:sticky lg:top-24 lg:self-start">
          <div className="mb-4 rounded-2xl bg-gradient-to-br from-brand-600 to-brand-800 p-4 text-white shadow-card">
            <div className="text-xs font-medium uppercase tracking-wider text-brand-200">Vendor workspace</div>
            <div className="mt-1 font-display font-bold">{user.farm_name || user.name}</div>
            <div className="text-xs text-brand-200">📍 {user.location || "Ernakulam"}, {user.district}</div>
          </div>
          <nav className="flex gap-1 overflow-x-auto pb-2 lg:flex-col lg:overflow-visible lg:pb-0">
            {NAV.map((n) => {
              const active = pathname === n.href || (n.href !== "/vendor" && pathname.startsWith(n.href));
              return (
                <Link key={n.href} href={n.href}
                  className={`flex shrink-0 items-center gap-2.5 rounded-xl px-3.5 py-2.5 text-sm font-medium transition ${
                    active ? "bg-brand-600 text-white shadow-card" : "text-stone-600 hover:bg-stone-100 hover:text-stone-900"
                  }`}>
                  <span>{n.emoji}</span>{n.label}
                </Link>
              );
            })}
          </nav>
        </aside>
        <div className="min-w-0">{children}</div>
      </div>
      <CopilotDrawer />
    </div>
  );
}
