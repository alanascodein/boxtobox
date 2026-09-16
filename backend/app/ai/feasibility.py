"""AMIE — Agricultural Market Infeasibility Engine (feasibility core).

Implements the deterministic pipeline from AMIE_Final_Revised_PRD.md:

    market analysis (real DB data)
      → scenario construction (synthetic micro-state, anchored on real macro data)
      → cascading day-by-day simulation (time-expanded feasibility check)
      → bottleneck detection + explanation (WHAT/WHEN/WHERE/HOW MUCH/WHY)
      → critical commitment set (greedy heuristic, PRD §14)
      → intervention generation + counterfactual re-simulation (PRD §15–17)
      → uncertainty bands P10/P50/P90 (PRD §19) → GREEN/AMBER/RED/BLACK (PRD §20)

PRD principles honored in this module:
- §2.1 Forecasting is an input, not the product; feasibility is the output.
- §2.6/§23 Every output exposes assumptions; no "AI magic" numbers.
- §2.8 No LLM anywhere in this file — deterministic calculations are the source of truth.
- §9/§40 The micro-state (farm commitments, processors, storage) is synthetic and
  labeled as such; macro anchors (prices, demand level, buyer requests) come from
  the application database.
- §18 Fixed seed → the demo is reproducible bit-for-bit.
- §32 Invariants: capacity, conservation, time, quality, nonnegativity are
  enforced structurally and verified in tests.
- §36 If anything fails, results degrade to the deterministic fallbacks below.

No third-party optimization library is required: allocation inside each day is a
deterministic FIFO cascade, and the intervention search is a bounded greedy scan
(PRD §16 explicitly allows a deterministic greedy fallback).
"""
from __future__ import annotations

import copy
import random
import statistics
import zlib
from datetime import date, timedelta

from sqlalchemy.orm import Session

from ..db import BuyerRequest, DemandSignal, Listing, PriceObservation
from .data import LOCATIONS, crop_meta

# ---------------------------------------------------------------------------
# Tunable model constants (all costs in ₹; documented as model assumptions)
# ---------------------------------------------------------------------------

VEHICLE_RATE_PER_KM = 14.0        # matches logistics.py ₹/km for a small lot vehicle
REFERENCE_LOT_KG = 500.0          # assumed shared-vehicle lot size → per-kg freight
HANDLING_PER_KG = 1.2             # ₹/kg loading/unloading
STORAGE_RATE_PER_KG_DAY = 1.5     # ₹/kg/day for rented emergency storage
ALT_PROCESSOR_RATE_PER_KG = 3.5   # ₹/kg tolling fee at an alternative processor
PROCUREMENT_PREMIUM_PCT = 0.15    # emergency offtake pays 15% above reference price
RESCHEDULE_PENALTY_PER_KG = 2.0   # ₹/kg farmer disruption compensation
RESCUE_VALUE_PCT = 0.92           # rescued produce recovers 92% of reference price

# Supply uncertainty band (PRD §19). Multipliers applied to arrival quantities.
SUPPLY_BANDS: dict[str, float] = {"P10": 0.85, "P50": 1.0, "P90": 1.18}

# Utilization thresholds (PRD §13 step 5 — configurable by design).
CRITICAL_UTILIZATION = 0.75       # ≥ 75% of capacity → AMBER day (feasible but strained)

# Crop-category scale factor for district-level daily flow (kg/day at neutral demand).
CATEGORY_FLOW_SCALE = {"vegetable": 1.0, "spice": 0.7, "fruit": 1.15, "leafy": 0.55}

SCENARIOS: dict[str, str] = {
    "baseline": "Normal week — no injected disturbance",
    "synchronized_harvest": "Synchronized harvest — later harvests pulled into the same window",
    "processor_outage": "Processor outage — capacity cut from day 2",
    "storage_shortage": "Storage shortage — buffer capacity cut",
    "buyer_withdrawal": "Buyer withdrawal — major buyer reduces offtake",
    "transport_disruption": "Transport disruption — market intake limited",
    "demand_shock": "Demand shock — absorption spikes then collapses",
    "bumper_harvest": "Bumper harvest — expected supply surges",
    "compound_shock": "Compound shock — synchronized harvest + processor outage",
}


# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------

def _stable_seed(*parts: object) -> int:
    """CRC32-based seed so results are identical across runs/processes
    (Python's built-in hash() is salted per process and must not be used)."""
    return zlib.crc32("|".join(str(p) for p in parts).encode("utf-8")) & 0xFFFFFFFF


def _mean(values: list[float], default: float = 0.0) -> float:
    return statistics.mean(values) if values else default


def _round1(x: float) -> float:
    return round(x + 0.0, 1)


def _avg_pairwise_km() -> float:
    """Mean pairwise haversine-ish distance between reference localities.
    Deterministic (derived from the static location catalog), used to price
    redirect freight without pretending we know the exact route."""
    names = list(LOCATIONS)
    total, n = 0.0, 0
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            la, lb = LOCATIONS[a], LOCATIONS[b]
            total += ((la["lat"] - lb["lat"]) ** 2 + (la["lng"] - lb["lng"]) ** 2) ** 0.5 * 111.0
            n += 1
    return round(total / n, 1) if n else 12.0


AVG_PAIRWISE_KM = _avg_pairwise_km()
REDIRECT_COST_PER_KG = round(AVG_PAIRWISE_KM * VEHICLE_RATE_PER_KM / REFERENCE_LOT_KG + HANDLING_PER_KG, 2)


# ---------------------------------------------------------------------------
# Step 0 — market analysis from REAL application data (PRD §21 page 1)
# ---------------------------------------------------------------------------

def extract_market_stats(db: Session, crop: str, district: str = "Ernakulam") -> dict:
    """Pull the real macro anchors for a crop: recent prices, demand signals,
    live supply (active listings) and stated buyer demand (active requests)."""
    prices = [
        r.modal_price
        for r in db.query(PriceObservation)
        .filter(PriceObservation.crop == crop)
        .order_by(PriceObservation.date.desc())
        .limit(30)
        .all()
    ]
    prices = list(reversed(prices))

    signals = [
        r.demand_score
        for r in db.query(DemandSignal)
        .filter(DemandSignal.crop == crop, DemandSignal.district == district)
        .order_by(DemandSignal.date.desc())
        .limit(30)
        .all()
    ]
    signals = list(reversed(signals))

    # Exponential smoothing (same α as forecast.py) → current demand level 0–100.
    level = 50.0
    for s in signals:
        level = 0.25 * s + 0.75 * level
    if not signals:
        level = 50.0

    listing_kg = float(sum(
        l.quantity_available_kg for l in db.query(Listing)
        .filter(Listing.crop == crop, Listing.status == "ACTIVE").all()
    ))
    request_kg = float(sum(
        r.quantity_kg for r in db.query(BuyerRequest)
        .filter(BuyerRequest.crop == crop, BuyerRequest.active.is_(True)).all()
    ))

    # Provenance of the price series (PRD §2.3: observed vs inferred vs synthetic)
    src_rows = (
        db.query(PriceObservation.source)
        .filter(PriceObservation.crop == crop)
        .order_by(PriceObservation.date.desc())
        .limit(30)
        .all()
    )
    sources = {s for (s,) in src_rows}
    if "agmarknet" in sources or "agmarknet_cache" in sources:
        price_source = "real" if "agmarknet" in sources else "real (cached snapshot)"
        price_source_detail = "AGMARKNET daily wholesale prices via data.gov.in"
    else:
        price_source = "synthetic"
        price_source_detail = "seeded demonstration series anchored on typical Kerala base prices"

    return {
        "crop": crop,
        "district": district,
        "price_recent": _mean(prices[-7:], crop_meta(crop)["base_price"]),
        "price_prev": _mean(prices[:14], crop_meta(crop)["base_price"]),
        "price_volatility": (statistics.pstdev(prices) / _mean(prices, 1.0)) if len(prices) >= 7 else 0.2,
        "price_points": len(prices),
        "price_source": price_source,
        "price_source_detail": price_source_detail,
        "demand_level": level,
        "demand_points": len(signals),
        "listing_kg": listing_kg,
        "request_kg": request_kg,
    }


def analyze_market(stats: dict) -> dict:
    """Deterministic reading of the CURRENT market from real data only.
    This is the 'CURRENT MARKET: HEALTHY' panel — no synthetic flows involved."""
    crop = stats["crop"]
    meta = crop_meta(crop)
    price = stats["price_recent"] or meta["base_price"]
    prev = stats["price_prev"] or price
    trend_pct = ((price - prev) / prev * 100) if prev else 0.0

    # Balance = stated buyer demand ÷ listed supply, scaled by demand-signal
    # pressure. Listings understate true supply, so treat as directional.
    demand_week_kg = stats["request_kg"]
    supply_week_kg = max(stats["listing_kg"], 0.0)
    balance = ((demand_week_kg / supply_week_kg) * (stats["demand_level"] / 50.0)
               if supply_week_kg > 1 else None)

    if balance is None:
        status, label = "UNKNOWN", "No live supply on the market"
    elif balance > 1.5:
        status, label = "TIGHT", "Demand outpaces listed supply"
    elif balance > 0.8:
        status, label = "HEALTHY", "Balanced market"
    elif balance > 0.5:
        status, label = "SOFT", "Supply running ahead of demand"
    else:
        status, label = "IMBALANCED", "Significant surplus on the market"

    confidence = "Low"
    if stats["price_points"] >= 21 and stats["demand_points"] >= 60:
        confidence = "High"
    elif stats["price_points"] >= 7:
        confidence = "Medium"

    return {
        "crop": crop,
        "crop_name": meta["name"],
        "emoji": meta["emoji"],
        "status": status,
        "label": label,
        "price_avg": round(price, 1),
        "price_trend_pct": round(trend_pct, 1),
        "price_volatility_pct": round(stats["price_volatility"] * 100, 1),
        "demand_level": round(stats["demand_level"], 1),
        "listed_supply_kg": round(supply_week_kg, 0),
        "stated_demand_kg": round(demand_week_kg, 0),
        "balance_ratio": round(balance, 2) if balance is not None else None,
        "confidence": confidence,
        "sources": {
            "prices": f"{stats['price_points']} recent price observations ({stats.get('price_source', 'synthetic')})",
            "demand": f"{stats['demand_points']} demand signals (DB)",
            "supply": "active listings (DB)",
            "buyer_demand": "active buyer requests (DB)",
        },
        "price_source": stats.get("price_source", "synthetic"),
        "price_source_detail": stats.get("price_source_detail", ""),
        "note": "Balance = stated buyer demand ÷ listed supply × demand-signal pressure "
                "(live data; directional — listings understate total supply). The forward "
                "simulation below adds a synthetic micro-state (PRD §9).",
    }


# ---------------------------------------------------------------------------
# Step 1 — scenario construction (synthetic micro-state, PRD §8/§18/§39)
# ---------------------------------------------------------------------------

def build_scenario(stats: dict, horizon_days: int = 7, scenario_name: str = "synchronized_harvest",
                   seed: int = 42) -> dict:
    """Build the time-expanded scenario. Deterministic for a given
    (crop, scenario, seed, stats). All quantities are derived, never hard-coded:
    the base daily flow scales with the real demand level and crop category."""
    crop = stats["crop"]
    meta = crop_meta(crop)
    H = max(3, min(14, int(horizon_days)))
    rng = random.Random(_stable_seed(crop, scenario_name, seed, H))

    price_ref = round(stats["price_recent"] or meta["base_price"], 1)
    perish = int(meta["perish_days"])
    base = 1400.0 * (stats["demand_level"] / 50.0) * CATEGORY_FLOW_SCALE.get(meta["category"], 1.0)

    # --- arrival profile -----------------------------------------------------
    # baseline: near-uniform week; each disturbance reshapes/magnifies it.
    uniform = [1.0] * H
    total_mult = 1.0
    peak_day = max(3, H - 1)          # 1-indexed day of concentrated arrivals
    profile = uniform

    if scenario_name == "synchronized_harvest":
        # Pull-forward: later harvests (next week's) get moved inside the window →
        # the weekly TOTAL rises even though weekly production is unchanged.
        total_mult = 1.30
        profile = _concentrate(H, peak_day, peak_share=0.34, rng=rng)
    elif scenario_name == "bumper_harvest":
        total_mult = 1.5
        profile = _jitter(uniform, rng)
    elif scenario_name == "storage_shortage":
        # A buffer shortage only bites when arrivals spike: mild pull-forward.
        total_mult = 1.20
        profile = _concentrate(H, peak_day, peak_share=0.32, rng=rng)
    elif scenario_name == "transport_disruption":
        total_mult = 1.20
        profile = _concentrate(H, peak_day, peak_share=0.30, rng=rng)
    elif scenario_name == "compound_shock":
        total_mult = 1.30
        profile = _concentrate(H, peak_day, peak_share=0.34, rng=rng)
    else:
        profile = _jitter(uniform, rng)

    arrivals = {d: _round1(base * H * total_mult * profile[d - 1]) for d in range(1, H + 1)}

    # --- farmer commitments (synthetic micro-state) ---------------------------
    commitments: list[dict] = []
    locations = list(LOCATIONS)
    n_farms = min(len(locations), 8)
    cid = 0
    remaining = {d: arrivals[d] for d in arrivals}
    days_order = sorted(arrivals, key=lambda d: -arrivals[d])
    for f in range(n_farms):
        loc = locations[(f * 3 + 1) % len(locations)]
        n_lots = rng.randint(2, 4) if H <= 7 else rng.randint(3, 5)
        for _ in range(n_lots):
            # biggest lots land on the biggest arrival days → realistic convergence
            d = days_order[cid % len(days_order)]
            kg_pool = remaining.get(d, 0.0)
            if kg_pool <= 1:
                d = max(remaining.items(), key=lambda kv: kv[1])[0]
                kg_pool = remaining.get(d, 0.0)
            kg = _round1(min(kg_pool, max(80.0, kg_pool / rng.uniform(2.0, 3.2))))
            if kg <= 0:
                continue
            remaining[d] = remaining.get(d, 0.0) - kg
            cid += 1
            commitments.append({
                "id": f"F-{cid:03d}",
                "farm": f"{loc} Farm {f + 1:02d}",
                "location": loc,
                "day": d,
                "kg": kg,
                "flexible": rng.random() < 0.55,   # can shift ±1 day if asked
            })
    # sweep any rounding leftovers onto their day
    for d, kg in remaining.items():
        if kg > 1:
            commitments.append({
                "id": f"F-{cid + 1:03d}", "farm": f"{locations[0]} Farm 09",
                "location": locations[0], "day": d, "kg": _round1(kg), "flexible": True,
            })
            cid += 1
    commitments.sort(key=lambda c: (c["day"], -c["kg"]))

    # --- capacity model (synthetic, labeled) ----------------------------------
    # Processor pool sized to ~155% of a normal day → comfortable GREEN headroom
    # on normal days, but a synchronized peak (~250% of a day) cannot pass.
    proc_total = base * 1.55
    shares = [0.34, 0.28, 0.22, 0.16]
    processors = [
        {"id": f"P{i + 1:02d}", "name": f"{locations[i + 1 % len(locations)]} Processing Unit",
         "location": locations[(i + 1) % len(locations)], "capacity_kg_day": _round1(proc_total * s)}
        for i, s in enumerate(shares)
    ]

    proc_profile = {d: proc_total for d in range(1, H + 1)}
    if scenario_name == "processor_outage":
        for d in range(2, H + 1):
            proc_profile[d] = proc_total * 0.60
    elif scenario_name == "compound_shock":
        for d in range(3, H + 1):
            proc_profile[d] = proc_total * 0.85

    storage_cap = base * 1.3
    if scenario_name == "storage_shortage":
        storage_cap *= 0.35
    inflow_limit = base * 0.80
    outflow_limit = base * 0.55
    intake_profile = {d: inflow_limit for d in range(1, H + 1)}
    if scenario_name == "transport_disruption":
        for d in range(2, min(5, H) + 1):
            intake_profile[d] = inflow_limit * 0.45

    # Buyers can absorb slightly more than a normal day of processing — so in
    # steady state absorption never binds and the failure mode is physical
    # (processor/storage). Demand-side scenarios cut this below the flow.
    daily_demand = base * 1.15
    demand_profile = {d: daily_demand for d in range(1, H + 1)}
    if scenario_name == "buyer_withdrawal":
        for d in range(3, H + 1):
            demand_profile[d] = daily_demand * 0.55
    elif scenario_name == "demand_shock":
        for d in range(1, min(3, H) + 1):
            demand_profile[d] = daily_demand * 1.45
        for d in range(max(2, min(3, H) + 1), H + 1):
            demand_profile[d] = daily_demand * 0.75

    trigger = {
        "synchronized_harvest": f"Harvest synchronization: {round(total_mult * 100 - 100)}% extra volume pulled "
                                f"into the window; day {peak_day} alone carries {round(profile[peak_day - 1] * 100)}% of the week",
        "processor_outage": "Processing capacity cut to 55% from day 2",
        "storage_shortage": "Buffer storage cut to 35% during an arrival spike",
        "buyer_withdrawal": "Major buyer cuts offtake 45% from day 3",
        "transport_disruption": "Market intake limited to 55% on days 2–4",
        "demand_shock": "Demand spikes 45% for 2 days then drops 25%",
        "bumper_harvest": "Expected supply surges 50% above normal",
        "compound_shock": "Synchronized arrivals + processing capacity cut to 70% from day 3",
    }.get(scenario_name, "Normal weekly pattern — no injected disturbance")

    nodes = (
        [{"id": f"MKT", "type": "MARKET", "name": f"{stats['district']} Assembly Market",
          "capacity_kg_day": None, "location": stats["district"]}]
        + [{"id": p["id"], "type": "PROCESSOR", "name": p["name"],
            "capacity_kg_day": p["capacity_kg_day"], "location": p["location"]} for p in processors]
        + [{"id": "STO", "type": "STORAGE", "name": "Buffer Storage Pool",
            "capacity_kg_day": None, "location": stats["district"]}]
        + [{"id": f"B{i + 1:02d}", "type": "BUYER", "name": f"{locations[i % len(locations)]} Buyer Cluster",
            "capacity_kg_day": _round1(daily_demand / 8), "location": locations[i % len(locations)]}
           for i in range(8)]
    )

    return {
        "crop": crop,
        "crop_name": meta["name"],
        "emoji": meta["emoji"],
        "district": stats["district"],
        "horizon_days": H,
        "scenario_name": scenario_name,
        "scenario_label": SCENARIOS.get(scenario_name, scenario_name),
        "seed": seed,
        "price_ref_per_kg": price_ref,
        "perish_days": perish,
        "base_daily_flow_kg": _round1(base),
        "peak_day": peak_day,
        "commitments": commitments,
        "arrivals_kg": arrivals,
        "processors": processors,
        "proc_capacity_profile": proc_profile,
        "storage": {
            "capacity_kg": _round1(storage_cap),
            "daily_inflow_kg": _round1(inflow_limit),
            "daily_outflow_kg": _round1(outflow_limit),
            "intake_profile": intake_profile,
        },
        "daily_demand_profile": demand_profile,
        "trigger_text": trigger,
        "nodes": nodes,
        "assumptions": [
            f"Base daily flow {_round1(base)} kg/day derived from live demand level "
            f"({round(stats['demand_level'], 1)}/100) × crop-category scale",
            f"Processor pool sized at 115% of a normal day; storage buffer at 90% (synthetic capacities)",
            f"Produce spoils after {perish} days (crop catalog)",
            f"Supply uncertainty band P10/P50/P90 = {SUPPLY_BANDS['P10']}/{SUPPLY_BANDS['P50']}/{SUPPLY_BANDS['P90']}× arrivals",
            f"Redirect freight ₹{REDIRECT_COST_PER_KG}/kg, storage ₹{STORAGE_RATE_PER_KG_DAY}/kg/day, "
            f"tolling ₹{ALT_PROCESSOR_RATE_PER_KG}/kg, procurement premium {int(PROCUREMENT_PREMIUM_PCT * 100)}%",
        ],
        "labels": {
            "synthetic_micro_state": True,
            "banner": "DEMONSTRATION SCENARIO — SYNTHETIC MICRO-STATE",
            "note": "Commitments, processors, storage and buyers are synthetic (PRD §9). "
                    "Prices and demand level are anchored on live application data.",
        },
    }


def _jitter(profile: list[float], rng: random.Random) -> list[float]:
    """Near-uniform profile with deterministic jitter, normalized to sum 1."""
    j = [w * rng.uniform(0.85, 1.15) for w in profile]
    s = sum(j)
    return [x / s for x in j]


def _concentrate(H: int, peak_day: int, peak_share: float, rng: random.Random) -> list[float]:
    """Concentrate `peak_share` of the week on peak_day (1-indexed), with the
    remainder spread over the other days (small deterministic jitter)."""
    rest = (1.0 - peak_share) / (H - 1)
    prof = [rest] * H
    prof[peak_day - 1] = peak_share
    idx = [i for i in range(H) if i != peak_day - 1]
    vals = [prof[i] * rng.uniform(0.92, 1.08) for i in idx]
    s = sum(vals)
    for i, v in zip(idx, vals):
        prof[i] = v / s * (1.0 - peak_share)
    return prof


# ---------------------------------------------------------------------------
# Step 2 — cascading simulation (PRD §13 + §17; deterministic)
# ---------------------------------------------------------------------------

RUN_DEFAULTS: dict[str, float] = {
    "supply_mult": 1.0,
    "demand_mult": 1.0,
    "extra_storage_kg": 0.0,
    "redirect_kg_per_day": 0.0,
    "alt_processor_kg_per_day": 0.0,
    "procurement_kg_per_day": 0.0,
    "reschedule_kg": 0.0,
}


def run_cascade(scenario: dict, overrides: dict | None = None) -> dict:
    """Run the day-by-day cascading feasibility simulation.

    Daily mechanics (visible calculation path, PRD §23):
      1. harvest commitments for the day arrive at the assembly market;
         optional REDIRECT reroutes part of the arrivals straight to an
         alternative market/buyer before the bottleneck.
      2. backlog ages; produce older than the crop's perish window spoils.
      3. the processor pool intakes FIFO up to its (profiled) daily capacity;
         an alternative processor (intervention) adds capacity.
      4. excess tries buffer storage: bounded by free capacity AND the daily
         intake limit (transport). Rented storage (intervention) adds room +
         proportional intake. What can't be placed spills → unabsorbed.
      5. emergency procurement (intervention) buys part of the spill at a premium.
      6. absorption: processed today + storage outflow are offered to buyers up
         to the day's demand; unsold produce returns to storage if there is
         room, otherwise it is unabsorbed.

    The cascade is the point: day d's overflow raises day d+1's backlog and
    fills storage, so a single synchronized day degrades every later day.
    """
    ov = dict(RUN_DEFAULTS)
    ov.update(overrides or {})
    H = scenario["horizon_days"]
    perish = scenario["perish_days"]
    supply_mult = float(ov["supply_mult"])
    demand_mult = float(ov["demand_mult"])

    commitments = copy.deepcopy(scenario["commitments"])

    # RESCHEDULE intervention: move kg off the peak day to its neighbours.
    rescheduled_kg = 0.0
    from_day = int(scenario.get("peak_day", max(scenario["arrivals_kg"], key=lambda d: scenario["arrivals_kg"][d])))
    want = float(ov["reschedule_kg"])
    if want > 0:
        moved = 0.0
        for c in sorted(commitments, key=lambda c: -c["kg"]):
            if moved >= want:
                break
            if c["day"] == from_day and c["flexible"]:
                take = min(c["kg"], want - moved)
                c["kg"] = _round1(c["kg"] - take)
                moved += take
                tgt_lo, tgt_hi = max(1, from_day - 1), min(H, from_day + 1)
                kg_lo = take / 2 if tgt_lo != from_day else 0.0
                kg_hi = take - kg_lo
                if kg_lo > 0:
                    commitments.append({**c, "id": c["id"] + "R", "day": tgt_lo, "kg": _round1(kg_lo)})
                if kg_hi > 0:
                    commitments.append({**c, "id": c["id"] + "R", "day": tgt_hi, "kg": _round1(kg_hi)})
        commitments = [c for c in commitments if c["kg"] > 0.05]
        rescheduled_kg = moved

    def arrivals_on(day: int) -> float:
        return sum(c["kg"] for c in commitments if c["day"] == day) * supply_mult

    backlog: list[list[float]] = []   # [age_days, kg] waiting at the market
    store: list[list[float]] = []     # [age_days, kg] in buffer storage
    base_store_cap = float(scenario["storage"]["capacity_kg"])
    extra_store_cap = float(ov["extra_storage_kg"])
    inflow_profile = scenario["storage"]["intake_profile"]
    outflow_limit = float(scenario["storage"]["daily_outflow_kg"])
    alt_proc = float(ov["alt_processor_kg_per_day"])
    redirect_cap = float(ov["redirect_kg_per_day"])
    procurement_cap = float(ov["procurement_kg_per_day"])
    price_ref = float(scenario["price_ref_per_kg"])

    days: list[dict] = []
    totals = {
        "arrivals_kg": 0.0, "redirected_kg": 0.0, "processed_kg": 0.0, "stored_kg": 0.0,
        "absorbed_kg": 0.0, "unabsorbed_kg": 0.0, "spoilage_kg": 0.0, "procured_kg": 0.0,
    }
    cost = {"redirect": 0.0, "storage": 0.0, "alt_processor": 0.0, "procurement": 0.0, "reschedule": 0.0}
    first_failure: dict | None = None
    peak_store_end = 0.0
    peak_extra_store_use = 0.0
    alt_processor_used = 0.0

    def take_kg(buckets: list[list[float]], amount: float) -> float:
        """FIFO removal from oldest buckets; returns actually removed kg."""
        removed = 0.0
        for b in buckets:
            if removed >= amount - 1e-9:
                break
            t = min(b[1], amount - removed)
            b[1] -= t
            removed += t
        return removed

    for d in range(1, H + 1):
        arrivals = _round1(arrivals_on(d))
        redirected = min(arrivals, redirect_cap)
        post_redirect = arrivals - redirected
        backlog.append([0.0, post_redirect])

        # aging + spoilage (time invariant: nothing spoils before its window)
        for b in backlog:
            b[0] += 1.0
        for b in store:
            b[0] += 1.0
        backlog_spoil = take_kg(backlog, sum(b[1] for b in backlog if b[0] > perish))
        backlog[:] = [b for b in backlog if b[1] > 1e-9]
        store_spoil = take_kg(store, sum(b[1] for b in store if b[0] > perish))
        store[:] = [b for b in store if b[1] > 1e-9]

        # processing (capacity profile bakes in outage scenarios)
        proc_cap = float(scenario["proc_capacity_profile"][d]) + alt_proc
        offer = sum(b[1] for b in backlog)
        processed = min(offer, proc_cap)
        take_kg(backlog, processed)
        alt_used = max(0.0, processed - float(scenario["proc_capacity_profile"][d]))
        alt_processor_used += alt_used
        backlog[:] = [b for b in backlog if b[1] > 1e-9]
        excess = offer - processed

        # storage intake (capacity + daily intake limit; rented storage adds both)
        store_pre_intake = sum(b[1] for b in store)
        store_free = max(0.0, (base_store_cap + extra_store_cap) - store_pre_intake)
        intake_limit = float(inflow_profile[d]) + extra_store_cap * 0.35
        stored = min(excess, store_free, intake_limit)
        if stored > 0:
            # remove FIFO from backlog, carrying each bucket's age into storage
            to_store = stored
            while to_store > 1e-9 and backlog:
                b = backlog[0]
                t = min(b[1], to_store)
                match = next((sb for sb in store if abs(sb[0] - b[0]) < 1e-9), None)
                if match:
                    match[1] += t
                else:
                    store.append([b[0], t])
                b[1] -= t
                to_store -= t
                if b[1] <= 1e-9:
                    backlog.pop(0)
        backlog[:] = [b for b in backlog if b[1] > 1e-9]
        spill = excess - stored
        if extra_store_cap > 0:
            peak_extra_store_use = max(peak_extra_store_use, max(0.0, store_pre_intake + stored - base_store_cap))

        # emergency procurement rescues part of the spill
        procured = min(spill, procurement_cap)
        spill -= procured
        unabsorbed_today = spill

        # absorption: buyers take processed + storage outflow up to demand
        demand_today = float(scenario["daily_demand_profile"][d]) * demand_mult
        store_pre_outflow = sum(b[1] for b in store)
        outflow = min(store_pre_outflow, outflow_limit)
        take_kg(store, outflow)
        sellable = processed + outflow
        absorbed = min(sellable, demand_today)
        unsold = sellable - absorbed
        store_free_now = max(0.0, (base_store_cap + extra_store_cap) - sum(b[1] for b in store))
        returned = min(unsold, store_free_now)
        if returned > 0:
            store.append([1.0, returned])   # re-enters storage one day older
        unabsorbed_today += unsold - returned
        store[:] = [b for b in store if b[1] > 1e-9]

        store_end = sum(b[1] for b in store)
        backlog_end = sum(b[1] for b in backlog)
        peak_store_end = max(peak_store_end, store_end)

        proc_util = (offer / proc_cap) if proc_cap > 0 else 0.0
        storage_util = ((store_pre_intake + stored) / (base_store_cap + extra_store_cap)) if (base_store_cap + extra_store_cap) > 0 else 0.0

        status = "GREEN"
        if unabsorbed_today > 0.5:
            status = "RED"
        elif proc_util >= CRITICAL_UTILIZATION or storage_util >= CRITICAL_UTILIZATION:
            status = "AMBER"

        totals["arrivals_kg"] += post_redirect
        totals["redirected_kg"] += redirected
        totals["processed_kg"] += processed
        totals["stored_kg"] += stored
        totals["absorbed_kg"] += absorbed
        totals["unabsorbed_kg"] += unabsorbed_today
        totals["spoilage_kg"] += backlog_spoil + store_spoil
        totals["procured_kg"] += procured
        cost["redirect"] += redirected * REDIRECT_COST_PER_KG
        cost["alt_processor"] += alt_used * ALT_PROCESSOR_RATE_PER_KG
        cost["procurement"] += procured * price_ref * PROCUREMENT_PREMIUM_PCT
        if extra_store_cap > 0:
            cost["storage"] += max(0.0, store_end - base_store_cap) * STORAGE_RATE_PER_KG_DAY

        if first_failure is None and status == "RED":
            first_failure = _explain_failure(scenario, d, {
                "unabsorbed": unabsorbed_today,
                "spill": spill + procured,
                "unsold": unsold - returned,
                "offer": offer,
                "proc_cap": proc_cap,
                "store_total": store_pre_intake + stored,
                "store_cap": base_store_cap + extra_store_cap,
                "stored": stored,
                "demand": demand_today,
                "sellable": sellable,
            })

        days.append({
            "day": d,
            "date": (date.today() + timedelta(days=d)).isoformat(),
            "arrivals_kg": _round1(arrivals),
            "redirected_kg": _round1(redirected),
            "processed_kg": _round1(processed),
            "stored_kg": _round1(stored),
            "procured_kg": _round1(procured),
            "spill_kg": _round1(spill),
            "spoilage_kg": _round1(backlog_spoil + store_spoil),
            "demand_kg": _round1(demand_today),
            "absorbed_kg": _round1(absorbed),
            "unabsorbed_kg": _round1(unabsorbed_today),
            "store_end_kg": _round1(store_end),
            "backlog_end_kg": _round1(backlog_end),
            "proc_required_kg": _round1(offer),
            "proc_capacity_kg": _round1(proc_cap),
            "proc_utilization_pct": round(proc_util * 100, 1),
            "storage_utilization_pct": round(min(storage_util, 9.99) * 100, 1),
            "status": status,
        })

    cost["reschedule"] = rescheduled_kg * RESCHEDULE_PENALTY_PER_KG
    cost["total"] = round(sum(cost.values()), 0)
    if extra_store_cap > 0:
        # storage cost ≈ peak rented volume × rate × avg holding time (perish/2)
        cost["storage"] = round(peak_extra_store_use * STORAGE_RATE_PER_KG_DAY * max(1.0, perish / 2.0), 0)
        cost["total"] = round(sum(v for k, v in cost.items() if k != "total"), 0)

    worst = "GREEN"
    if any(dy["status"] == "RED" for dy in days):
        worst = "RED"
    elif any(dy["status"] == "AMBER" for dy in days):
        worst = "AMBER"

    totals = {k: _round1(v) for k, v in totals.items()}
    return {
        "status": worst,
        "days": days,
        "first_failure": first_failure,
        "totals": {
            **totals,
            "end_backlog_kg": _round1(sum(b[1] for b in backlog)),
            "end_store_kg": _round1(sum(b[1] for b in store)),
            "rescue_rate_pct": 0.0,  # filled by caller when comparing to a baseline
        },
        "peak_utilization_pct": round(max(dy["proc_utilization_pct"] for dy in days), 1),
        "peak_storage_utilization_pct": round(max(dy["storage_utilization_pct"] for dy in days), 1),
        "max_unabsorbed_day_kg": round(max((dy["unabsorbed_kg"] for dy in days), default=0.0), 1),
        "bottlenecks": _rank_bottlenecks(scenario, days),
        "costs": {k: round(v, 0) for k, v in cost.items()},
        "detection_lead_time_hours": (max(0, (days[[i for i, dy in enumerate(days) if dy["status"] == "RED"][0]]["day"] - 1) * 24 + 12)
                                       if any(dy["status"] == "RED" for dy in days) else None),
        "rescheduled_kg": _round1(rescheduled_kg),
        "alt_processor_used_kg": _round1(alt_processor_used),
        "peak_extra_store_use_kg": _round1(peak_extra_store_use),
    }


def _explain_failure(scenario: dict, day: int, m: dict) -> dict:
    """Turn the day's numbers into a WHAT/WHEN/WHERE/HOW MUCH/WHY explanation
    (PRD §24). Attribution is deterministic from the binding constraint."""
    if m["unsold"] > 0.5:
        where, ntype = "Buyer absorption", "BUYER_ABSORPTION"
        why = "Sellable produce exceeds what buyers can absorb today"
        required, capacity = m["sellable"], m["demand"]
    elif m["store_total"] >= m["store_cap"] - 0.5 and m["spill"] > 0.5:
        where, ntype = "Buffer Storage Pool", "STORAGE"
        why = "Storage is full, so excess arrivals cannot be buffered"
        required, capacity = m["store_total"], m["store_cap"]
    else:
        where, ntype = "Processor pool", "PROCESSOR"
        why = "Arrivals exceed processing capacity and the overflow cannot be stored"
        required, capacity = m["offer"], m["proc_cap"]

    # name the specific processor that would overflow under proportional share
    named = None
    if ntype == "PROCESSOR":
        caps = [p["capacity_kg_day"] for p in scenario["processors"]]
        total_cap = sum(caps) or 1.0
        for p, cap in zip(scenario["processors"], caps):
            required_share = m["offer"] * cap / total_cap
            if required_share > cap * 1.001:
                named = {
                    "id": p["id"], "name": p["name"], "location": p["location"],
                    "capacity_kg": _round1(cap), "required_kg": _round1(required_share),
                    "deficit_kg": _round1(required_share - cap),
                }
                break

    return {
        "day": day,
        "node": named["id"] if named else ("STO" if ntype == "STORAGE" else "MKT"),
        "node_name": named["name"] if named else where,
        "node_type": ntype,
        "required_kg": _round1(required),
        "capacity_kg": _round1(capacity),
        "deficit_kg": _round1(m["unabsorbed"]),
        "why": why,
        "trigger": scenario["trigger_text"],
        "named_processor": named,
    }


def _rank_bottlenecks(scenario: dict, days: list[dict]) -> list[dict]:
    """Rank constraint pools by peak utilization and total deficit contribution
    (PRD GET /bottlenecks: ranked constraints)."""
    processors = scenario["processors"]
    rows = []
    proc_peak = max((dy["proc_utilization_pct"] for dy in days), default=0.0)
    proc_deficit = sum(max(0.0, dy["proc_required_kg"] - dy["proc_capacity_kg"]) for dy in days)
    for p in sorted(processors, key=lambda x: -x["capacity_kg_day"]):
        share = p["capacity_kg_day"] / (sum(q["capacity_kg_day"] for q in processors) or 1.0)
        rows.append({
            "id": p["id"], "name": p["name"], "type": "PROCESSOR",
            "peak_utilization_pct": round(proc_peak * share * 1.0, 1),
            "capacity_kg_day": p["capacity_kg_day"],
            "deficit_kg": _round1(proc_deficit * share),
        })
    rows.append({
        "id": "STO", "name": "Buffer Storage Pool", "type": "STORAGE",
        "peak_utilization_pct": round(max((dy["storage_utilization_pct"] for dy in days), default=0.0), 1),
        "capacity_kg_day": scenario["storage"]["capacity_kg"],
        "deficit_kg": _round1(sum(dy["unabsorbed_kg"] for dy in days if dy["storage_utilization_pct"] >= 99.0)),
    })
    rows.sort(key=lambda r: (-r["peak_utilization_pct"], -r["deficit_kg"]))
    return rows


# ---------------------------------------------------------------------------
# Step 3 — critical commitment set (greedy heuristic, PRD §14)
# ---------------------------------------------------------------------------

def find_critical_commitments(scenario: dict, baseline: dict, max_steps: int = 8) -> dict:
    """Greedy search for a small commitment set whose simultaneous presence
    causes the infeasibility. Heuristic, NOT proven minimal (PRD §14)."""
    if baseline["totals"]["unabsorbed_kg"] <= 0.5:
        return {"commitments": [], "combined_kg": 0.0, "note": "Scenario is feasible — no critical set."}

    base_unabsorbed = baseline["totals"]["unabsorbed_kg"]
    candidates = sorted(scenario["commitments"], key=lambda c: -c["kg"])[: max_steps * 3]
    chosen: list[dict] = []
    remaining_ids = {c["id"] for c in candidates}
    current_unabsorbed = base_unabsorbed

    for _ in range(max_steps):
        if current_unabsorbed <= 0.5:
            break
        best = None
        for c in candidates:
            if c["id"] not in remaining_ids:
                continue
            trial = copy.deepcopy(scenario)
            trial["commitments"] = [x for x in trial["commitments"] if x["id"] != c["id"]]
            res = run_cascade(trial)["totals"]["unabsorbed_kg"]
            gain = current_unabsorbed - res
            if best is None or gain > best[1] or (abs(gain - best[1]) < 1e-9 and c["kg"] > best[0]["kg"]):
                best = (c, gain, res)
        if best is None or best[1] <= 0.5:
            break
        c, gain, res = best
        chosen.append({**{k: c[k] for k in ("id", "farm", "location", "day", "kg")},
                       "unabsorbed_reduction_kg": _round1(gain)})
        remaining_ids.discard(c["id"])
        current_unabsorbed = res

    return {
        "commitments": chosen,
        "combined_kg": _round1(sum(c["kg"] for c in chosen)),
        "residual_unabsorbed_kg": _round1(current_unabsorbed),
        "note": "Critical set identified by heuristic (greedy) search — not proven minimal.",
    }


# ---------------------------------------------------------------------------
# Step 4 — intervention engine + counterfactuals (PRD §15–17)
# ---------------------------------------------------------------------------

INTERVENTION_LABELS = {
    "REDIRECT": "🚚 Redirect to alternative market",
    "STORE": "🏬 Rent emergency storage",
    "RESCHEDULE": "🗓️ Reschedule flexible harvests",
    "PROCESS": "🏭 Activate alternative processor",
    "PROCURE": "🏛️ Emergency procurement offtake",
}


def _auto_quantity(itype: str, baseline: dict, scenario: dict) -> float:
    """Derive a sensible intervention size from the measured deficit —
    never from hard-coded demo numbers."""
    peak_deficit = max((dy["unabsorbed_kg"] for dy in baseline["days"]), default=0.0)
    total_unabsorbed = baseline["totals"]["unabsorbed_kg"]
    peak_arrivals = max(scenario["arrivals_kg"].values())
    if itype == "REDIRECT":
        return round(peak_deficit * 0.40, 0)
    if itype == "STORE":
        return round(total_unabsorbed * 0.60, 0)
    if itype == "RESCHEDULE":
        return round(peak_arrivals * 0.22, 0)
    if itype == "PROCESS":
        return round(peak_deficit * 0.40, 0)
    if itype == "PROCURE":
        return round(peak_deficit * 0.60, 0)
    return 0.0


def _overrides_for(scenario: dict, baseline: dict, selection: list[str]) -> dict:
    ov: dict = {}
    for t in selection:
        q = _auto_quantity(t, baseline, scenario)
        if t == "REDIRECT":
            ov["redirect_kg_per_day"] = q
        elif t == "STORE":
            ov["extra_storage_kg"] = q
        elif t == "RESCHEDULE":
            ov["reschedule_kg"] = q
        elif t == "PROCESS":
            ov["alt_processor_kg_per_day"] = q
        elif t == "PROCURE":
            ov["procurement_kg_per_day"] = q
    return ov


def generate_intervention_options(scenario: dict, baseline: dict) -> list[dict]:
    """Evaluate every single intervention plus the most promising combinations
    (bounded deterministic search — PRD §16 greedy fallback)."""
    baseline_unabs = baseline["totals"]["unabsorbed_kg"]
    singles = ["REDIRECT", "STORE", "RESCHEDULE", "PROCESS", "PROCURE"]
    options: list[dict] = []

    def _eval(selection: list[str]) -> dict:
        res = run_cascade(scenario, _overrides_for(scenario, baseline, selection))
        residual = res["totals"]["unabsorbed_kg"]
        rescued = max(0.0, baseline_unabs - residual)
        cost = res["costs"]["total"]
        value = rescued * float(scenario["price_ref_per_kg"]) * RESCUE_VALUE_PCT
        return {
            "types": selection,
            "label": " + ".join(INTERVENTION_LABELS[t].split(" ", 1)[1] for t in selection),
            "quantities_kg": {t: _auto_quantity(t, baseline, scenario) for t in selection},
            "rescued_kg": _round1(rescued),
            "residual_kg": _round1(residual),
            "cost": round(cost, 0),
            "rescued_value": round(value, 0),
            "net_benefit": round(value - cost, 0),
            "cost_per_kg": round(cost / rescued, 1) if rescued > 0.5 else None,
            "status_after": "FEASIBLE" if residual <= 0.5 else res["status"],
            "farmer_disruption": _round1(res.get("rescheduled_kg", 0.0)),
        }

    for t in singles:
        options.append(_eval([t]))
    # pairwise combos of the best-performing singles (bounded search)
    ranked = sorted(singles, key=lambda t: -options[singles.index(t)]["rescued_kg"])[:3]
    for i in range(len(ranked)):
        for j in range(i + 1, len(ranked)):
            options.append(_eval([ranked[i], ranked[j]]))

    options.sort(key=lambda o: (o["residual_kg"] > 0.5, o["cost_per_kg"] if o["cost_per_kg"] is not None else 9e9))
    return options


# ---------------------------------------------------------------------------
# Step 5 — full pipeline (PRD §4 / §28 POST /simulate)
# ---------------------------------------------------------------------------

def run_amie(stats: dict, horizon_days: int = 7, scenario_name: str = "synchronized_harvest",
             seed: int = 42, with_interventions: bool = True) -> dict:
    """Full AMIE run: analysis → scenario → cascades (baseline + uncertainty) →
    bottlenecks → critical set → interventions → counterfactual."""
    scenario = build_scenario(stats, horizon_days, scenario_name, seed)
    baseline = run_cascade(scenario)

    # uncertainty band (PRD §19): rerun the baseline across P10/P50/P90 supply
    uncertainty = {}
    for band, mult in SUPPLY_BANDS.items():
        res = run_cascade(scenario, {"supply_mult": mult})
        uncertainty[band] = {
            "supply_multiplier": mult,
            "status": res["status"],
            "unabsorbed_kg": res["totals"]["unabsorbed_kg"],
            "first_failure_day": res["first_failure"]["day"] if res["first_failure"] else None,
        }

    worst_status = "GREEN"
    for band in ("P10", "P50", "P90"):
        s = uncertainty[band]["status"]
        if s == "RED" or (s == "AMBER" and worst_status == "GREEN"):
            worst_status = s
    best_intervention = None
    options = []
    critical = {"commitments": [], "combined_kg": 0.0,
                "note": "Scenario is feasible — no critical set."}
    counterfactual = None

    if baseline["totals"]["unabsorbed_kg"] > 0.5 and with_interventions:
        options = generate_intervention_options(scenario, baseline)
        best_intervention = options[0] if options else None
        if best_intervention:
            after = run_cascade(scenario, _overrides_for(scenario, baseline, best_intervention["types"]))
            counterfactual = _counterfactual(scenario, baseline, after, best_intervention)
        if best_intervention is None or best_intervention["residual_kg"] >= baseline["totals"]["unabsorbed_kg"] * 0.95:
            worst_status = "BLACK"
        critical = find_critical_commitments(scenario, baseline)

    return {
        "engine": "AMIE deterministic feasibility core (no LLM)",
        "crop": scenario["crop"],
        "crop_name": scenario["crop_name"],
        "emoji": scenario["emoji"],
        "district": scenario["district"],
        "horizon_days": scenario["horizon_days"],
        "scenario_name": scenario_name,
        "scenario_label": scenario["scenario_label"],
        "seed": seed,
        "market_analysis": analyze_market(stats),
        "scenario_summary": {
            "base_daily_flow_kg": scenario["base_daily_flow_kg"],
            "commitment_count": len(scenario["commitments"]),
            "total_commitment_kg": _round1(sum(c["kg"] for c in scenario["commitments"])),
            "processors": scenario["processors"],
            "storage": {k: v for k, v in scenario["storage"].items() if k != "intake_profile"},
            "peak_day": scenario["peak_day"],
            "trigger": scenario["trigger_text"],
            "nodes": scenario["nodes"],
        },
        "timeline": baseline["days"],
        "first_failure": baseline["first_failure"],
        "bottlenecks": baseline["bottlenecks"],
        "totals": baseline["totals"],
        "peak_utilization_pct": baseline["peak_utilization_pct"],
        "uncertainty": uncertainty,
        "system_status": worst_status,
        "detection_lead_time_hours": baseline["detection_lead_time_hours"],
        "critical_commitments": critical,
        "intervention_options": options,
        "best_intervention": best_intervention,
        "counterfactual": counterfactual,
        "assumptions": scenario["assumptions"],
        "labels": scenario["labels"],
    }


def _counterfactual(scenario: dict, baseline: dict, after: dict, option: dict) -> dict:
    """Side-by-side NO-INTERVENTION vs AMIE-INTERVENTION metrics (PRD §21 page 6)."""
    rescued = option["rescued_kg"]
    value = rescued * float(scenario["price_ref_per_kg"]) * RESCUE_VALUE_PCT
    return {
        "types": option["types"],
        "label": option["label"],
        "baseline": {
            "status": baseline["status"],
            "first_failure_day": baseline["first_failure"]["day"] if baseline["first_failure"] else None,
            "unabsorbed_kg": baseline["totals"]["unabsorbed_kg"],
            "spoilage_kg": baseline["totals"]["spoilage_kg"],
            "absorbed_kg": baseline["totals"]["absorbed_kg"],
            "cost": 0,
        },
        "after": {
            "status": "FEASIBLE" if after["totals"]["unabsorbed_kg"] <= 0.5 else after["status"],
            "first_failure_day": after["first_failure"]["day"] if after["first_failure"] else None,
            "unabsorbed_kg": after["totals"]["unabsorbed_kg"],
            "spoilage_kg": after["totals"]["spoilage_kg"],
            "absorbed_kg": after["totals"]["absorbed_kg"],
            "cost": option["cost"],
        },
        "rescued_kg": option["rescued_kg"],
        "residual_kg": option["residual_kg"],
        "cost": option["cost"],
        "rescued_value": round(value, 0),
        "net_benefit": round(value - option["cost"], 0),
        "timeline_after": after["days"],
        "quantities_kg": option["quantities_kg"],
    }


def simulate_selection(stats: dict, horizon_days: int, scenario_name: str, seed: int,
                       selection: list[str]) -> dict:
    """Evaluate a user-chosen intervention combination against the baseline
    (PRD §28 POST /interventions + /counterfactual)."""
    scenario = build_scenario(stats, horizon_days, scenario_name, seed)
    baseline = run_cascade(scenario)
    valid = [t for t in selection if t in INTERVENTION_LABELS]
    if not valid:
        after = baseline
        option = {"types": [], "label": "No intervention", "rescued_kg": 0.0, "residual_kg": baseline["totals"]["unabsorbed_kg"],
                  "cost": 0, "quantities_kg": {}}
    else:
        ov = _overrides_for(scenario, baseline, valid)
        after = run_cascade(scenario, ov)
        residual = after["totals"]["unabsorbed_kg"]
        rescued = max(0.0, baseline["totals"]["unabsorbed_kg"] - residual)
        option = {
            "types": valid,
            "label": " + ".join(INTERVENTION_LABELS[t].split(" ", 1)[1] for t in valid),
            "rescued_kg": _round1(rescued),
            "residual_kg": _round1(residual),
            "cost": after["costs"]["total"],
            "quantities_kg": {t: _auto_quantity(t, baseline, scenario) for t in valid},
        }
    cf = _counterfactual(scenario, baseline, after, option)
    cf["timeline_baseline"] = baseline["days"]
    return {
        "crop": scenario["crop"],
        "scenario_name": scenario_name,
        "seed": seed,
        "horizon_days": scenario["horizon_days"],
        "system_status_before": baseline["status"],
        "counterfactual": cf,
        "labels": scenario["labels"],
    }
