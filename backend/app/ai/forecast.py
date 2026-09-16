"""Demand forecast (PRD §15 MVP smoothing) + crop recommendation (PRD §32)."""
import statistics
from datetime import date, timedelta

from sqlalchemy.orm import Session

from ..db import DemandSignal, PriceObservation
from .data import CROPS, crop_meta


def forecast_demand(db: Session, crop: str, district: str = "Ernakulam") -> dict:
    """Exponential smoothing over demand signals + seasonal multiplier."""
    rows = (
        db.query(DemandSignal)
        .filter(DemandSignal.crop == crop, DemandSignal.district == district)
        .order_by(DemandSignal.date)
        .all()
    )
    if len(rows) < 14:
        return {
            "crop": crop, "next_7d_pct": 0.0, "next_30d_pct": 0.0,
            "confidence": "Low", "note": "Insufficient recent local data. Treat this estimate as indicative.",
        }

    scores = [r.demand_score for r in rows]
    alpha = 0.25
    level = scores[0]
    for s in scores[1:]:
        level = alpha * s + (1 - alpha) * level

    recent = statistics.mean(scores[-7:])
    older = statistics.mean(scores[-30:-7]) if len(scores) >= 30 else statistics.mean(scores[: len(scores) // 2] or scores)
    momentum = (recent - older) / older if older else 0.0

    next_7 = round(momentum * 100, 1)
    next_30 = round(momentum * 60, 1)  # momentum decays over horizon
    confidence = "Medium" if len(rows) >= 60 else "Low"
    if abs(next_7) < 3:
        confidence = "High"

    return {
        "crop": crop,
        "current_level": round(level, 1),
        "next_7d_pct": max(-40, min(40, next_7)),
        "next_30d_pct": max(-40, min(40, next_30)),
        "confidence": confidence,
        "history": [
            {"date": r.date.isoformat(), "score": r.demand_score} for r in rows[-30:]
        ],
    }


def recommend_crops(db: Session, district: str = "Ernakulam") -> list[dict]:
    """Rank crops by expected profit × sale probability × (1 - risk) (PRD §32)."""
    out = []
    today = date.today()
    for slug, meta in CROPS.items():
        prices = [
            r.modal_price
            for r in db.query(PriceObservation)
            .filter(PriceObservation.crop == slug, PriceObservation.date >= today - timedelta(days=60))
            .order_by(PriceObservation.date)
            .all()
        ]
        demand = (
            db.query(DemandSignal)
            .filter(DemandSignal.crop == slug, DemandSignal.district == district, DemandSignal.date >= today - timedelta(days=30))
            .all()
        )
        demand_avg = statistics.mean([d.demand_score for d in demand]) if demand else 50.0
        if not prices:
            continue
        price_avg = statistics.mean(prices)
        volatility = statistics.pstdev(prices) / price_avg if price_avg else 0.2

        demand_score = demand_avg / 100
        expected_revenue = price_avg * 0.95
        cost_per_kg = expected_revenue * (0.55 if meta["category"] != "leafy" else 0.45)
        expected_profit = expected_revenue - cost_per_kg
        risk = min(1.0, volatility * 1.6 + (0.15 if demand_avg < 45 else 0) + (0.1 if meta["perish_days"] <= 4 else 0))
        final = expected_profit * demand_score * (1 - risk)

        out.append({
            "crop": slug,
            "name": meta["name"],
            "emoji": meta["emoji"],
            "harvest_days": meta["harvest_days"],
            "demand": "High" if demand_avg > 62 else "Medium-High" if demand_avg > 48 else "Medium",
            "demand_score": round(demand_avg, 1),
            "avg_price": round(price_avg, 1),
            "price_trend": round((statistics.mean(prices[-7:]) - statistics.mean(prices[:7])) / statistics.mean(prices[:7]) * 100, 1) if len(prices) > 14 else 0,
            "expected_profit_per_kg": round(expected_profit, 1),
            "market_risk": "High" if risk > 0.55 else "Medium" if risk > 0.35 else "Low",
            "risk_score": round(risk, 2),
            "final_score": round(final, 2),
        })

    out.sort(key=lambda r: r["final_score"], reverse=True)
    return out
