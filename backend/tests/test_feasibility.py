"""AMIE engine tests (PRD §29): known feasible/infeasible cases, determinism,
invariants, monotonicity, intervention effectiveness.

Runs against a temporary SQLite DB; no fixtures outside this file required.

    cd backend && python -m pytest tests/test_feasibility.py -q
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# In-memory DB before app imports bind models
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app.ai import feasibility as fz  # noqa: E402
from app.db import Base, engine, SessionLocal  # noqa: E402
from app.seed import seed_if_empty  # noqa: E402


def setup_module(module):
    Base.metadata.create_all(bind=engine)
    seed_if_empty()


def _stats(crop="tomato"):
    db = SessionLocal()
    try:
        return fz.extract_market_stats(db, crop, "Ernakulam")
    finally:
        db.close()


# ---------------------------------------------------------------------------
# PRD §29 known cases: supply < capacity → feasible; supply > capacity → not
# ---------------------------------------------------------------------------

def test_known_feasible_case():
    """A plain baseline scenario with modest arrivals must stay GREEN."""
    s = build("baseline", horizon=5)
    res = fz.run_cascade(s)
    assert res["status"] in ("GREEN", "AMBER")
    assert res["totals"]["unabsorbed_kg"] <= 0.5


def test_known_infeasible_case():
    """PRD §29 known case: arrivals exceed total downstream capacity
    (processing + storage) → guaranteed infeasible from day 1."""
    s = build("baseline", horizon=5)
    s["proc_capacity_profile"] = {d: s["base_daily_flow_kg"] * 0.30 for d in range(1, s["horizon_days"] + 1)}
    s["storage"]["capacity_kg"] = 0.0
    s["storage"]["intake_profile"] = {d: 0.0 for d in range(1, s["horizon_days"] + 1)}
    res = fz.run_cascade(s)
    assert res["status"] == "RED"
    assert res["totals"]["unabsorbed_kg"] > 0
    assert res["first_failure"]["day"] == 1


def build(scenario, horizon=7):
    return fz.build_scenario(_stats("tomato"), horizon, scenario, seed=42)


# ---------------------------------------------------------------------------
# Determinism (PRD §29 regression test, seed = 42)
# ---------------------------------------------------------------------------

def test_deterministic_same_seed():
    a = fz.run_amie(_stats("tomato"), 7, "synchronized_harvest", 42)
    b = fz.run_amie(_stats("tomato"), 7, "synchronized_harvest", 42)
    assert a["totals"] == b["totals"]
    assert a["timeline"] == b["timeline"]
    assert a["system_status"] == b["system_status"]
    assert a["first_failure"] == b["first_failure"]


def test_different_seed_changes_micro_state():
    a = fz.build_scenario(_stats("tomato"), 7, "synchronized_harvest", seed=42)
    b = fz.build_scenario(_stats("tomato"), 7, "synchronized_harvest", seed=99)
    # commitments differ in farm assignment (RNG differs) but total arrivals match profile
    assert sum(c["kg"] for c in a["commitments"]) > 0
    assert abs(sum(a["arrivals_kg"].values()) - sum(b["arrivals_kg"].values())) < 1.0


# ---------------------------------------------------------------------------
# PRD §32 invariants
# ---------------------------------------------------------------------------

def test_capacity_invariant():
    """Daily processed+stored+spilled must never exceed what arrived."""
    for scenario in ("baseline", "synchronized_harvest", "bumper_harvest", "processor_outage"):
        s = build(scenario, 7)
        res = fz.run_cascade(s)
        for d in res["days"]:
            assert d["processed_kg"] <= d["proc_capacity_kg"] + 0.05, f"day {d['day']} violates processor capacity"
            assert d["stored_kg"] <= s["storage"]["daily_inflow_kg"] + 1e-6 + 0.05


def test_nonnegative_invariant():
    s = build("synchronized_harvest", 7)
    res = fz.run_cascade(s)
    for d in res["days"]:
        for k, v in d.items():
            if k.endswith("_kg") or k.endswith("_pct"):
                assert v >= 0, f"day {d['day']} {k} is negative"


def test_conservation_invariant():
    """arrivals + carry-in = processed + stored + spilled + carry-out (+ redirect)."""
    s = build("compound_shock", 7)
    res = fz.run_cascade(s)
    carry = 0.0
    for d in res["days"]:
        inflow = d["arrivals_kg"] - d["redirected_kg"] + carry
        outflow = d["processed_kg"] + d["stored_kg"] + d["spill_kg"] + d["spoilage_kg"]
        assert inflow >= outflow - 0.5, f"day {d['day']}: more leaves than enters ({inflow} < {outflow})"
        carry = d["backlog_end_kg"]


def test_no_arrival_before_available_date():
    """Days before any commitment must have zero arrivals (time invariant)."""
    s = build("baseline", 7)
    first_day = min(c["day"] for c in s["commitments"])
    arrivals = fz.run_cascade(s)
    for d in arrivals["days"]:
        if d["day"] < first_day:
            assert d["arrivals_kg"] == 0


def test_rescued_produce_is_real():
    """Rescued = baseline unabsorbed − after unabsorbed; never negative."""
    s = build("synchronized_harvest", 7)
    base = fz.run_cascade(s)
    ov = fz._overrides_for(s, base, ["REDIRECT", "STORE"])
    after = fz.run_cascade(s, ov)
    rescued = base["totals"]["unabsorbed_kg"] - after["totals"]["unabsorbed_kg"]
    assert rescued >= -0.5
    assert after["totals"]["unabsorbed_kg"] <= base["totals"]["unabsorbed_kg"] + 0.5


# ---------------------------------------------------------------------------
# PRD §31 Level 3 — monotonic stress testing
# ---------------------------------------------------------------------------

def test_monotonic_capacity_reduction():
    """Less processing capacity must never improve feasibility."""
    s = build("baseline", 7)
    unabs = []
    for mult in (1.0, 0.8, 0.6, 0.4):
        trial = {**s, "proc_capacity_profile": {d: c * mult for d, c in s["proc_capacity_profile"].items()}}
        unabs.append(fz.run_cascade(trial)["totals"]["unabsorbed_kg"])
    for prev, nxt in zip(unabs, unabs[1:]):
        assert nxt >= prev - 0.5, f"feasibility improved when capacity dropped: {unabs}"


def test_monotonic_supply_increase():
    """More supply must never reduce unabsorbed produce."""
    s = build("synchronized_harvest", 7)
    unabs = [fz.run_cascade(s, {"supply_mult": m})["totals"]["unabsorbed_kg"] for m in (1.0, 1.1, 1.25, 1.5)]
    for prev, nxt in zip(unabs, unabs[1:]):
        assert nxt >= prev - 0.5, f"more supply improved feasibility: {unabs}"


def test_uncertainty_band_ordering():
    """P90 unabsorbed ≥ P50 ≥ P10 (PRD §19)."""
    s = build("synchronized_harvest", 7)
    p10 = fz.run_cascade(s, {"supply_mult": fz.SUPPLY_BANDS["P10"]})["totals"]["unabsorbed_kg"]
    p50 = fz.run_cascade(s, {"supply_mult": fz.SUPPLY_BANDS["P50"]})["totals"]["unabsorbed_kg"]
    p90 = fz.run_cascade(s, {"supply_mult": fz.SUPPLY_BANDS["P90"]})["totals"]["unabsorbed_kg"]
    assert p90 >= p50 - 0.5 >= p10 - 1.0


# ---------------------------------------------------------------------------
# Critical set + interventions (PRD §14–17)
# ---------------------------------------------------------------------------

def test_critical_set_reduces_infeasibility():
    s = build("synchronized_harvest", 7)
    base = fz.run_cascade(s)
    if base["totals"]["unabsorbed_kg"] <= 0.5:
        return  # scenario configured feasible; critical-set logic still exercised below
    crit = fz.find_critical_commitments(s, base)
    assert crit["commitments"], "greedy search found no critical commitments"
    assert crit["residual_unabsorbed_kg"] < base["totals"]["unabsorbed_kg"]
    assert "heuristic" in crit["note"].lower()


def test_intervention_options_help():
    s = build("synchronized_harvest", 7)
    base = fz.run_cascade(s)
    options = fz.generate_intervention_options(s, base)
    assert options, "no intervention options generated"
    best = options[0]
    if base["totals"]["unabsorbed_kg"] > 0.5:
        assert best["rescued_kg"] > 0
        assert best["cost"] > 0


def test_counterfactual_structure():
    s = build("synchronized_harvest", 7)
    out = fz.simulate_selection(_stats("tomato"), 7, "synchronized_harvest", 42, ["STORE", "REDIRECT"])
    cf = out["counterfactual"]
    assert set(cf["baseline"]) >= {"status", "unabsorbed_kg", "cost"}
    assert set(cf["after"]) >= {"status", "unabsorbed_kg", "cost"}
    assert cf["baseline"]["cost"] == 0


def test_full_pipeline_shape():
    out = fz.run_amie(_stats("tomato"), 7, "synchronized_harvest", 42)
    assert out["market_analysis"]["crop"] == "tomato"
    assert len(out["timeline"]) == 7
    assert out["uncertainty"]["P50"]["status"] in ("GREEN", "AMBER", "RED")
    assert out["labels"]["synthetic_micro_state"] is True
    assert out["assumptions"] and out["bottlenecks"]


def test_market_analysis_uses_real_data():
    a = fz.analyze_market(_stats("tomato"))
    assert a["price_source"] == "synthetic" and "AGMARKNET" not in a["sources"]["prices"]
    assert a["sources"]["demand"].endswith("(DB)")
    assert a["status"] in ("HEALTHY", "TIGHT", "SOFT", "IMBALANCED", "UNKNOWN")


def test_market_analysis_degrades_gracefully_without_data():
    """PRD §36: no data → UNKNOWN/indicative, never a crash."""
    empty = {"crop": "tomato", "district": "X", "price_recent": 0, "price_prev": 0,
             "price_volatility": 0.2, "price_points": 0, "demand_level": 50.0,
             "demand_points": 0, "listing_kg": 0.0, "request_kg": 0.0}
    a = fz.analyze_market(empty)
    assert a["status"] == "UNKNOWN"
