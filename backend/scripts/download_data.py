"""AMIE data pipeline — real AGMARKNET prices via data.gov.in (PRD §7).

Pipeline:  fetch → validate → normalize → cache (data/processed/) → optional DB load
Fallback:  offline → use cached snapshot; no cache → keep synthetic data (PRD §36).
No personal API key required: uses data.gov.in's public sample key.

Usage (from backend/):
    python scripts/download_data.py            # fetch + cache + report
    python scripts/download_data.py --load     # also load into farmmesh.db
    python scripts/download_data.py --load-only  # load existing cache only

Real rows are tagged source='agmarknet' / 'agmarknet_cache'; synthetic rows keep
source='synthetic'. The engines can then report their price provenance (PRD §2.3).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

# data.gov.in public sample key (documented, free; PRD §7.1: no paid/keyed APIs required)
API_KEY = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"
RESOURCE_ID = "9ef942dc-d4b7-4f18-9ca7-9916eb2bc0a5"  # AGMARKNET daily prices
BASE_URL = f"https://api.data.gov.in/resource/{RESOURCE_ID}"

# Crop-name → app slug mapping (AGMARKNET uses local commodity names)
CROP_ALIASES: dict[str, str] = {
    "tomato": "tomato",
    "cucumber": "cucumber",
    "beans": "beans",
    "banana": "banana",
    "green chilli": "green_chilli",
    "green chilli (dry)": "green_chilli",
    "chilli green": "green_chilli",
    "spinach": "spinach",
    "palak": "spinach",
    "amaranthus": "spinach",
}

STATE = "Kerala"
ROOT = Path(__file__).resolve().parents[1]          # backend/
DATA_DIR = ROOT.parent / "data"
PROCESSED_DIR = DATA_DIR / "processed"
METADATA_DIR = DATA_DIR / "metadata"
CACHE_FILE = PROCESSED_DIR / "agmarknet_kerala_prices.csv"


def _http_get_json(url: str, timeout: int = 30) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "AMIE-prototype/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch(state: str = STATE, limit_per_page: int = 5000, max_pages: int = 12) -> list[dict]:
    """Page through the AGMARKNET resource for the given state."""
    rows: list[dict] = []
    for page in range(1, max_pages + 1):
        params = {
            "api-key": API_KEY,
            "format": "json",
            "limit": limit_per_page,
            "offset": (page - 1) * limit_per_page,
            "filters[state]": state,
        }
        url = BASE_URL + "?" + urllib.parse.urlencode(params)
        try:
            payload = _http_get_json(url)
        except Exception as e:  # offline / DNS failure / 5xx → caller falls back
            print(f"  fetch failed on page {page}: {e}")
            break
        records = payload.get("records") or []
        rows.extend(records)
        total = int(payload.get("total") or 0)
        print(f"  page {page}: +{len(records)} rows (total so far {len(rows)}/{total or '?'})")
        if not records or len(rows) >= total:
            break
    return rows


def validate_and_normalize(raw: list[dict]) -> list[dict]:
    """Keep only usable records; enforce nonnegative numeric prices (PRD §29 data tests)."""
    out: list[dict] = []
    seen: set[tuple] = set()
    for r in raw:
        try:
            commodity = str(r.get("commodity", "")).strip()
            slug = CROP_ALIASES.get(commodity.lower())
            if not slug:
                # AGMARKNET appends variety notes ("Cucumber(Vegetable)") — try prefix/contains match
                for alias, mapped in CROP_ALIASES.items():
                    if commodity.lower().startswith(alias) or alias in commodity.lower():
                        slug = mapped
                        break
            if not slug:
                continue
            market = str(r.get("market", "")).strip()
            district = str(r.get("district", "")).strip() or "Ernakulam"
            d = datetime.strptime(str(r.get("arrival_date", "")).strip(), "%d/%m/%Y").date()
            modal = float(str(r.get("modal_price", "0")).strip() or 0)
            mn = float(str(r.get("min_price", "0")).strip() or 0)
            mx = float(str(r.get("max_price", "0")).strip() or 0)
        except (ValueError, TypeError):
            continue
        # AGMARKNET prices are per quintal (100 kg) → convert to ₹/kg
        if modal > 900:  # nothing in our catalog trades near ₹900/kg; per-quintal values are 100×
            modal, mn, mx = modal / 100.0, mn / 100.0, mx / 100.0
        if modal <= 0 or mn < 0 or mx < mn:
            continue
        key = (slug, district, market, d)
        if key in seen:
            continue  # duplicate record handling (PRD §29)
        seen.add(key)
        out.append({
            "crop": slug,
            "district": district,
            "market_name": market,
            "date": d.isoformat(),
            "modal_price": round(modal, 1),
            "min_price": round(mn, 1) if mn > 0 else round(modal * 0.9, 1),
            "max_price": round(mx, 1) if mx > 0 else round(modal * 1.1, 1),
            "source": "agmarknet",
        })
    return out


def write_cache(rows: list[dict]) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    fieldnames = ["crop", "district", "market_name", "date", "modal_price", "min_price", "max_price", "source"]
    with CACHE_FILE.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"  cached {len(rows)} rows → {CACHE_FILE}")


def read_cache() -> list[dict]:
    if not CACHE_FILE.exists():
        return []
    with CACHE_FILE.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_into_db(rows: list[dict]) -> int:
    """Insert real rows into price_observations (idempotent per source+date+market)."""
    sys.path.insert(0, str(ROOT))
    from app.db import PriceObservation, SessionLocal, init_db  # noqa: E402

    init_db()
    db = SessionLocal()
    try:
        existing = {
            (r.crop, r.date, r.market_name)
            for r in db.query(PriceObservation).filter(PriceObservation.source != "synthetic").all()
        }
        added = 0
        for r in rows:
            key = (r["crop"], r["date"], r.get("market_name", ""))
            if key in existing:
                continue
            db.add(PriceObservation(
                crop=r["crop"], district=r["district"], date=date.fromisoformat(r["date"]),
                modal_price=r["modal_price"], min_price=r["min_price"], max_price=r["max_price"],
                source=r["source"], market_name=r.get("market_name", ""),
            ))
            added += 1
        db.commit()
        return added
    finally:
        db.close()


def write_metadata(n_rows: int, n_days: int, markets: list[str], fetched_at: datetime) -> None:
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    entry = {
        "dataset_name": "agmarknet_kerala_prices",
        "source_url": f"{BASE_URL} (resource {RESOURCE_ID})",
        "access_date": fetched_at.date().isoformat(),
        "license": "Government Open Data License – India (GODL)",
        "geographic_scope": f"Kerala markets: {', '.join(sorted(markets)) or 'n/a'}",
        "temporal_scope": f"{n_days} distinct arrival dates ending {date.today().isoformat()}",
        "columns": ["crop", "district", "market_name", "date", "modal_price", "min_price", "max_price", "source"],
        "units": "₹/kg (converted from ₹/quintal)",
        "preprocessing": "crop-name aliasing → app slugs; dd/mm/YYYY → ISO dates; per-quintal → per-kg; dedup on (crop, district, market, date); nonnegative validation",
        "rows_cached": n_rows,
    }
    path = METADATA_DIR / "DATA_SOURCES.md"
    lines = [
        "# Data Sources (PRD §7.3)",
        "",
        "> No undocumented dataset enters the project.",
        "",
        "## agmarknet_kerala_prices",
        "",
        "```json",
        json.dumps(entry, indent=2),
        "```",
        "",
        "Cache file: `data/processed/agmarknet_kerala_prices.csv`",
        "",
        "Rows carry `source='agmarknet'` (fresh fetch) or `'agmarknet_cache'` (offline fallback).",
        "Synthetic seed data keeps `source='synthetic'` and is labeled as demonstration data in the UI.",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  metadata → {path}")


def main() -> int:
    ap = argparse.ArgumentParser(description="AMIE AGMARKNET price pipeline")
    ap.add_argument("--load", action="store_true", help="load fetched rows into farmmesh.db")
    ap.add_argument("--load-only", action="store_true", help="load existing cache into DB without fetching")
    args = ap.parse_args()

    now = datetime.now()

    if not args.load_only:
        print("Fetching AGMARKNET Kerala prices…")
        raw = fetch()
        rows = validate_and_normalize(raw)
        if rows:
            markets = sorted({r["market_name"] for r in rows})
            days = sorted({r["date"] for r in rows})
            write_cache(rows)
            write_metadata(len(rows), len(days), markets, now)
        else:
            print("  no rows fetched (offline or empty response).")

    if args.load or args.load_only:
        cached = read_cache()
        if cached:
            for r in cached:
                r.setdefault("source", "agmarknet_cache")
            added = load_into_db(cached)
            print(f"  DB load: +{added} real price rows (source=agmarknet_cache)")
        else:
            print("  no cache file — DB left on synthetic data (PRD §36 fallback).")

    cached_exists = CACHE_FILE.exists()
    if not cached_exists:
        print("Result: OFFLINE — app continues on labeled synthetic data.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
