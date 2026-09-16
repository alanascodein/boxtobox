"""Data pipeline tests (PRD §29 data tests): units, duplicates, ranges, dates,
plus price-provenance extraction (PRD §2.3 observed vs synthetic).

    cd backend && python -m pytest tests/test_data_pipeline.py -q
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from download_data import validate_and_normalize  # noqa: E402
from app.db import Base, engine, SessionLocal  # noqa: E402
from app.seed import seed_if_empty  # noqa: E402
from app.ai.feasibility import analyze_market, extract_market_stats  # noqa: E402


def setup_module(module):
    Base.metadata.create_all(bind=engine)
    seed_if_empty()


# ---------------------------------------------------------------------------
# validate_and_normalize (PRD §29 data tests)
# ---------------------------------------------------------------------------

RAW = [
    # normal record: per-quintal prices (₹/100kg), dd/mm/YYYY date
    {"commodity": "Tomato", "market": "Kochi", "district": "Ernakulam",
     "arrival_date": "05/09/2026", "modal_price": "3400", "min_price": "3000", "max_price": "3800"},
    # exact duplicate → dropped
    {"commodity": "Tomato", "market": "Kochi", "district": "Ernakulam",
     "arrival_date": "05/09/2026", "modal_price": "3400", "min_price": "3000", "max_price": "3800"},
    # already per-kg prices (small values) → kept as-is
    {"commodity": "Cucumber(Vegetable)", "market": "Tripunithura", "district": "Ernakulam",
     "arrival_date": "05/09/2026", "modal_price": "28.5", "min_price": "24", "max_price": "32"},
    # unknown commodity → skipped
    {"commodity": "Dragon Fruit", "market": "Kochi", "district": "Ernakulam",
     "arrival_date": "05/09/2026", "modal_price": "9000", "min_price": "8000", "max_price": "10000"},
    # bad date → skipped
    {"commodity": "Beans", "market": "Aluva", "district": "Ernakulam",
     "arrival_date": "garbage", "modal_price": "4800", "min_price": "4400", "max_price": "5200"},
    # negative min price → skipped
    {"commodity": "Beans", "market": "Aluva", "district": "Ernakulam",
     "arrival_date": "06/09/2026", "modal_price": "4800", "min_price": "-5", "max_price": "5200"},
    # green chilli alias
    {"commodity": "Chilli Green", "market": "Kochi", "district": "Ernakulam",
     "arrival_date": "06/09/2026", "modal_price": "6200", "min_price": "5800", "max_price": "6800"},
]


def test_normalizes_quintal_to_kg():
    rows = validate_and_normalize(RAW)
    tomato = next(r for r in rows if r["crop"] == "tomato" and r["market_name"] == "Kochi")
    assert tomato["modal_price"] == 34.0          # 3400 ₹/quintal → ₹34/kg
    assert tomato["min_price"] == 30.0
    assert tomato["date"] == "2026-09-05"          # ISO date
    assert tomato["source"] == "agmarknet"


def test_small_values_treated_as_per_kg():
    rows = validate_and_normalize(RAW)
    cu = next(r for r in rows if r["crop"] == "cucumber")
    assert cu["modal_price"] == 28.5               # untouched


def test_duplicates_removed():
    rows = validate_and_normalize(RAW)
    tomatoes = [r for r in rows if r["crop"] == "tomato"]
    assert len(tomatoes) == 1


def test_unknown_commodity_and_bad_records_skipped():
    rows = validate_and_normalize(RAW)
    crops = {r["crop"] for r in rows}
    assert "tomato" in crops and "cucumber" in crops and "green_chilli" in crops
    assert all(r["modal_price"] > 0 for r in rows)
    assert all(r["min_price"] >= 0 for r in rows)
    assert all(r["max_price"] >= r["min_price"] for r in rows)


def test_alias_mapping():
    rows = validate_and_normalize(RAW)
    assert any(r["crop"] == "green_chilli" for r in rows)


# ---------------------------------------------------------------------------
# Provenance: synthetic seed data must be labeled synthetic (PRD §2.3)
# ---------------------------------------------------------------------------

def test_synthetic_provenance_detected():
    db = SessionLocal()
    try:
        stats = extract_market_stats(db, "tomato", "Ernakulam")
        assert stats["price_source"] == "synthetic"
        a = analyze_market(stats)
        assert a["price_source"] == "synthetic"
        assert "synthetic" in a["sources"]["prices"]
    finally:
        db.close()


def test_real_rows_detected_as_real():
    """Real AGMARKNET rows must flip provenance for their crop (use beans to
    avoid polluting the shared tomato series other tests assert on)."""
    db = SessionLocal()
    try:
        from datetime import date
        from app.db import PriceObservation
        db.add(PriceObservation(crop="beans", district="Ernakulam", date=date.today(),
                                modal_price=48.0, min_price=44.0, max_price=52.0,
                                source="agmarknet", market_name="Kochi"))
        db.commit()
        stats = extract_market_stats(db, "beans", "Ernakulam")
        assert stats["price_source"].startswith("real")
        a = analyze_market(stats)
        assert a["price_source"].startswith("real")
        assert "AGMARKNET" in a["price_source_detail"]
    finally:
        db.close()
