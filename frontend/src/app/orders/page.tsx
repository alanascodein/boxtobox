"use client";

import { useEffect, useState } from "react";
import { api, formatINR, timeAgo } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";

type Order = {
  id: string; crop: string; quantity_kg: number; unit_price: number; gross_amount: number;
  status: string; delivery_location: string; created_at: string; vendor_name: string;
};

const STATUS_STYLES: Record<string, string> = {
  PLACED: "bg-stone-100 text-stone-600",
  CONFIRMED: "bg-blue-100 text-blue-700",
  IN_TRANSIT: "bg-amber-100 text-amber-700",
  DELIVERED: "bg-brand-100 text-brand-700",
  CANCELLED: "bg-red-100 text-red-600",
};

const EMOJI: Record<string, string> = { tomato: "🍅", green_chilli: "🌶️", beans: "🫛", cucumber: "🥒", banana: "🍌", spinach: "🥬" };

const PIPELINE = ["CONFIRMED", "IN_TRANSIT", "DELIVERED"];

export default function OrdersPage() {
  const { user, loading } = useAuth();
  const [orders, setOrders] = useState<Order[]>([]);
  const [fetched, setFetched] = useState(false);

  useEffect(() => {
    if (!loading && user) {
      api<Order[]>("/api/orders/mine").then((o) => { setOrders(o); setFetched(true); });
    }
  }, [user, loading]);

  if (!loading && !user) {
    return (
      <div className="mx-auto max-w-md px-4 py-24 text-center">
        <h1 className="font-display text-2xl font-bold">Sign in to view your orders</h1>
        <a href="/login" className="btn-primary mt-6">Sign in</a>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6">
      <h1 className="font-display text-3xl font-bold tracking-tight">My Orders</h1>
      <p className="mt-1 text-stone-500">Track deliveries and review past purchases.</p>

      {fetched && orders.length === 0 ? (
        <div className="card mt-8 p-14 text-center">
          <div className="text-4xl">📦</div>
          <h3 className="mt-3 font-display text-lg font-bold">No orders yet</h3>
          <p className="mt-1 text-sm text-stone-500">Fresh produce is waiting in the marketplace.</p>
          <a href="/marketplace" className="btn-primary mt-5">Browse marketplace</a>
        </div>
      ) : (
        <div className="mt-8 space-y-4">
          {orders.map((o) => {
            const stage = PIPELINE.indexOf(o.status);
            return (
              <div key={o.id} className="card p-5">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-4">
                    <span className="grid h-12 w-12 place-items-center rounded-xl bg-stone-50 text-2xl">{EMOJI[o.crop] || "🌱"}</span>
                    <div>
                      <div className="font-semibold capitalize">{o.crop.replace("_", " ")} · {o.quantity_kg} kg</div>
                      <div className="text-sm text-stone-500">{o.vendor_name || "Farm direct"} → {o.delivery_location} · {timeAgo(o.created_at)}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-display text-lg font-bold">{formatINR(o.gross_amount)}</div>
                    <span className={`badge ${STATUS_STYLES[o.status]}`}>{o.status.replace("_", " ").toLowerCase()}</span>
                  </div>
                </div>
                {o.status !== "CANCELLED" && (
                  <div className="mt-4 flex items-center gap-2">
                    {PIPELINE.map((s, i) => (
                      <div key={s} className="flex flex-1 items-center gap-2">
                        <div className={`h-2 flex-1 rounded-full ${i <= stage ? "bg-brand-500" : "bg-stone-200"}`} />
                      </div>
                    ))}
                    <span className="w-24 text-right text-xs text-stone-400">{stage >= 2 ? "Delivered" : stage >= 1 ? "On the way" : "Awaiting pickup"}</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
