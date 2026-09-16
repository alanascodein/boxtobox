"""Logistics estimation: nearest-neighbour route + cost, net farmer payout (PRD §13/§34)."""
from .matching import haversine_km
from .data import location_coords


def estimate_route(stops: list[str], start: str, end: str) -> dict:
    """Greedy nearest-neighbour route over named localities."""
    def coords(n):
        c = location_coords(n)
        return (c["lat"], c["lng"])

    cur = coords(start)
    remaining = [s for s in stops if s != start]
    route, total_km = [start], 0.0
    while remaining:
        nearest = min(remaining, key=lambda s: haversine_km(cur, coords(s)))
        d = haversine_km(cur, coords(nearest))
        total_km += d
        route.append(nearest)
        cur = coords(nearest)
        remaining.remove(nearest)
    d_home = haversine_km(cur, coords(end))
    total_km += d_home
    route.append(end)
    return {"route": route, "total_km": round(total_km, 1)}


def transport_cost(km: float, kg: float) -> float:
    """₹14/km base + ₹1.2/kg handling — tuned for small B2B lots."""
    return round(km * 14 + kg * 1.2, 0)


def net_economics(gross: float, logistics: float, quantity_kg: float, logistics_share: float = 0.5) -> dict:
    platform_fee = round(gross * 0.03, 0)
    logistics = round(logistics * logistics_share, 0)
    net = round(gross - platform_fee - logistics, 0)
    return {
        "gross": round(gross, 0),
        "platform_fee": platform_fee,
        "logistics": logistics,
        "net": net,
        "net_per_kg": round(net / quantity_kg, 1) if quantity_kg else 0,
    }
