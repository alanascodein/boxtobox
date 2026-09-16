"""Price recommendation engine (PRD §10 weighted statistical MVP)."""
import statistics
from datetime import date, timedelta

from sqlalchemy.orm import Session

from ..db import DemandSignal, PriceObservation
from .data import crop_meta


def _recent_prices(db: Session, crop: str, days: int = 30) -> list[float]:
    since = date.today() - timedelta(days=days)
    rows = (
        db.query(PriceObservation)
        .filter(PriceObservation.crop == crop, PriceObservation.date >= since)
        .order_by(PriceObservation.date)
        .all()
    )
    return [r.modal_price for r in rows]


def _demand_score(db: Session, crop: str) -> float:
    rows = db.query(DemandSignal).filter(DemandSignal.crop == crop).order_by(DemandSignal.date.desc()).limit(7).all()
    if not rows:
        return 50.0
    return statistics.mean(r.demand_score for r in rows)


def recommend_price(
    db: Session,
    crop: str,
    quantity_kg: float,
    quality_grade: str,
    location: str = "Ernakulam",
) -> dict:
    prices = _recent_prices(db, crop)
    if not prices:
        base = crop_meta(crop)["base_price"]
        confidence = "Low"
        reasons = ["Insufficient recent local data. Treat this estimate as indicative."]
        center = base
        trend = 0.0
    else:
        base = statistics.mean(prices[-7:])  # last week's local modal price
        prev = statistics.mean(prices[: max(1, len(prices) // 2)])
        trend = (base - prev) / prev if prev else 0.0
        confidence = "High" if len(prices) >= 21 else "Medium"

        demand = _demand_score(db, crop)
        demand_adj = (demand - 50) / 100 * base * 0.18          # ±18% by demand
        quality_adj = {"A": 0.10, "B": 0.0, "C": -0.08}[quality_grade] * base
        season_adj = 0.03 * base * (1 if trend > 0.02 else (-1 if trend < -0.02 else 0))

        # Excess nearby supply pushes price down slightly
        center = base + demand_adj + quality_adj + season_adj

        reasons = []
        if demand > 62:
            reasons.append("Local demand is above average")
        elif demand < 40:
            reasons.append("Local demand is below average")
        if quality_grade == "A":
            reasons.append("Grade A produce commands a premium")
        if trend > 0.02:
            reasons.append("Recent local prices are trending upward")
        elif trend < -0.02:
            reasons.append("Recent local prices are trending downward")
        if quantity_kg >= 100:
            reasons.append("Bulk quantity — buyers may negotiate volume rates")

    lo = round(center * 0.92, 1)
    hi = round(center * 1.08, 1)
    return {
        "crop": crop,
        "recommended_min": lo,
        "recommended_max": hi,
        "confidence": confidence,
        "trend_pct": round(trend * 100, 1),
        "recent_avg": round(statistics.mean(prices), 1) if prices else base,
        "reasons": reasons or ["Stable local market conditions"],
        "disclaimer": "Estimated market range — not a guaranteed price.",
    }
