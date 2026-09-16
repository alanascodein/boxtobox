"use client";

import Link from "next/link";
import { useState } from "react";
import { useAuth } from "@/lib/auth-context";

export default function Navbar() {
  const { user, logout, loading } = useAuth();
  const [open, setOpen] = useState(false);

  const links: { href: string; label: string }[] = user
    ? user.role === "VENDOR"
      ? [
          { href: "/vendor", label: "Dashboard" },
          { href: "/marketplace", label: "Marketplace" },
          { href: "/vendor/earnings", label: "Earnings" },
        ]
      : user.role === "ADMIN"
      ? [
          { href: "/admin", label: "Admin" },
          { href: "/marketplace", label: "Marketplace" },
        ]
      : [
          { href: "/marketplace", label: "Marketplace" },
          { href: "/orders", label: "My Orders" },
        ]
    : [
        { href: "/marketplace", label: "Marketplace" },
      ];

  return (
    <header className="fixed inset-x-0 top-0 z-40 border-b border-stone-200/70 bg-white/85 backdrop-blur-md">
      <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6">
        <Link href="/" className="flex items-center gap-2.5">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 text-lg shadow-card">
            🌱
          </span>
          <span className="font-display text-lg font-bold tracking-tight text-stone-900">
            FarmMesh <span className="text-brand-600">AI</span>
          </span>
        </Link>

        <div className="hidden items-center gap-1 md:flex">
          {links.map((l) => (
            <Link key={l.href} href={l.href} className="btn-ghost">
              {l.label}
            </Link>
          ))}
        </div>

        <div className="hidden items-center gap-3 md:flex">
          {loading ? (
            <div className="h-9 w-24 animate-pulse-soft rounded-xl bg-stone-200" />
          ) : user ? (
            <>
              <div className="text-right">
                <div className="text-sm font-semibold leading-tight">{user.name}</div>
                <div className="text-xs leading-tight text-stone-500">
                  {user.role === "VENDOR" ? user.farm_name || "Farmer" : user.role === "ADMIN" ? "Administrator" : "Buyer"}
                </div>
              </div>
              {user.role === "VENDOR" && (
                <Link href="/vendor/sell" className="btn-primary !px-4 !py-2 text-xs">
                  + Sell Harvest
                </Link>
              )}
              <button onClick={logout} className="btn-secondary !px-3.5 !py-2 text-xs">
                Sign out
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="btn-secondary !px-4 !py-2 text-xs">
                Sign in
              </Link>
              <Link href="/signup" className="btn-primary !px-4 !py-2 text-xs">
                Get started
              </Link>
            </>
          )}
        </div>

        <button onClick={() => setOpen(!open)} className="rounded-lg p-2 hover:bg-stone-100 md:hidden" aria-label="Menu">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            {open ? <path d="M6 6l12 12M18 6L6 18" /> : <path d="M4 7h16M4 12h16M4 17h16" />}
          </svg>
        </button>
      </nav>

      {open && (
        <div className="border-t border-stone-200 bg-white px-4 py-3 md:hidden">
          {links.map((l) => (
            <Link key={l.href} href={l.href} onClick={() => setOpen(false)} className="block rounded-lg px-3 py-2.5 text-sm font-medium hover:bg-stone-100">
              {l.label}
            </Link>
          ))}
          {user ? (
            <button onClick={logout} className="mt-2 w-full rounded-lg bg-stone-100 px-3 py-2.5 text-sm font-semibold">
              Sign out ({user.name})
            </button>
          ) : (
            <div className="mt-2 flex gap-2">
              <Link href="/login" className="btn-secondary flex-1">Sign in</Link>
              <Link href="/signup" className="btn-primary flex-1">Get started</Link>
            </div>
          )}
        </div>
      )}
    </header>
  );
}
