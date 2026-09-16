"""Vendor-only endpoints (server-side RBAC): AI workspace, matching, intelligence, AMIE."""
from datetime import date, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..ai import copilot, feasibility, forecast, listing_gen, logistics, matching, pricing
from ..ai.data import CROPS, LOCATIONS, crop_name, crop_meta
from ..auth import require_vendor
from ..db import BuyerRequest, Listing, User, VendorProfile, get_db
from ..schemas import CopilotIn, HarvestAnalysisIn, ListingOut, PriceIn

router = APIRouter(prefix="/api/vendor", tags=["vendor-ai"])


@router.post("/ai/analyze-harvest")
def analyze_harvest(
    body: HarvestAnalysisIn,
    user: User = Depends(require_vendor),
    db: Session = Depends(get_db),
):
    """PRD Feature 1: crop identification + preliminary grade."""
    result = listing_gen.analyze_harvest(body.image_url, body.crop_hint, body.quantity_kg)
    # attach live price guidance immediately
    price = pricing.recommend_price(db, result["crop"], body.quantity_kg or 30, result["estimated_quality"], user.vendor_profile.district)
    result["suggested_price_range"] = {"min": price["recommended_min"], "max": price["recommended_max"]}
    result["price_confidence"] = price["confidence"]
    result["price_reasons"] = price["reasons"]
    return result


@router.post("/ai/generate-listing")
def generate_listing(body: dict, user: User = Depends(require_vendor)):
    """PRD Feature 2: AI description/title generation."""
    crop = body.get("crop", "tomato")
    return listing_gen.generate_listing_text(
        crop=crop,
        quantity_kg=float(body.get("quantity_kg", 30)),
        quality_grade=body.get("quality_grade", "A"),
        harvest_label=body.get("harvest_label", "today"),
        location=body.get("location", user.vendor_profile.location or "Ernakulam"),
    )


@router.post("/ai/price")
def ai_price(body: PriceIn, user: User = Depends(require_vendor), db: Session = Depends(get_db)):
    """PRD Feature 4: price recommendation with reasons + confidence."""
    return pricing.recommend_price(db, body.crop, body.quantity_kg, body.quality_grade, body.location)


@router.get("/ai/match/{listing_id}")
def ai_match(listing_id: str, user: User = Depends(require_vendor), db: Session = Depends(get_db)):
    """PRD Feature 5: buyer matching for a listing."""
    l = db.get(Listing, listing_id)
    if not l or l.vendor_id != user.vendor_profile.id:
        raise HTTPException(status_code=404, detail="Listing not found.")
    return matching.match_buyers(db, l)


@router.post("/ai/aggregate")
def ai_aggregate(body: dict, user: User = Depends(require_vendor), db: Session = Depends(get_db)):
    """PRD Feature 6: supply aggregation across nearby farms."""
    crop = body.get("crop", "tomato")
    needed = float(body.get("quantity_kg", 100))
    loc = body.get("location", "Kochi")
    return matching.aggregate_supply(db, crop, needed, loc)


@router.post("/ai/logistics")
def ai_logistics(body: dict, user: User = Depends(require_vendor), db: Session = Depends(get_db)):
    """PRD Feature 7: pickup route + net economics."""
    stops = body.get("stops", ["Aluva", "Tripunithura", "Kakkanad"])
    start = body.get("start", "Ernakulam")
    end = body.get("end", "Kochi")
    kg = float(body.get("quantity_kg", 100))
    route = logistics.estimate_route(stops, start, end)
    cost = logistics.transport_cost(route["total_km"], kg)
    gross = round(kg * float(body.get("price_per_kg", 40)), 0)
    econ = logistics.net_economics(gross, cost, kg, logistics_share=float(body.get("logistics_share", 0.5)))
    return {"route": route["route"], "total_km": route["total_km"], "transport_cost": cost, **econ}


@router.get("/ai/demand/{crop}")
def ai_demand(crop: str, user: User = Depends(require_vendor), db: Session = Depends(get_db)):
    """PRD Feature 9: demand forecast."""
    return forecast.forecast_demand(db, crop)


@router.get("/ai/crop-recommendation")
def ai_crop_rec(user: User = Depends(require_vendor), db: Session = Depends(get_db)):
    """PRD Feature 8: what should I grow next."""
    return forecast.recommend_crops(db, user.vendor_profile.district or "Ernakulam")


@router.get("/intelligence/outlook")
def intelligence_outlook(user: User = Depends(require_vendor), db: Session = Depends(get_db)):
    """PRD §77A: market outlook + imbalance detection for the vendor's crops."""
    vp = user.vendor_profile
    out = []
    for slug in CROPS:
        f = forecast.forecast_demand(db, slug, vp.district or "Ernakulam")
        prices = pricing._recent_prices(db, slug, days=14)
        if not prices:
            continue
        base = sum(prices) / len(prices)
        prev_week = pricing._recent_prices(db, slug, days=30)[:14]
        trend = (base - (sum(prev_week) / len(prev_week))) / (sum(prev_week) / len(prev_week)) if prev_week else 0
        # Real supply/demand balance from live listings vs stated buyer demand
        analysis = feasibility.analyze_market(feasibility.extract_market_stats(db, slug, vp.district or "Ernakulam"))
        balance = analysis["balance_ratio"]
        if balance is None:
            risk, label = "MEDIUM", "Insufficient live data"
        elif balance > 1.15:
            risk, label = "LOW", "Demand outpaces supply"
        elif balance > 0.9:
            risk, label = "MEDIUM", "Balanced market"
        elif balance > 0.65:
            risk, label = "HIGH", "Supply exceeding demand"
        else:
            risk, label = "CRITICAL", "Significant surplus expected"
        out.append({
            "crop": slug,
            "crop_name": crop_name(slug),
            "emoji": crop_meta(slug)["emoji"],
            "price_avg": round(base, 1),
            "price_trend_pct": round(trend * 100, 1),
            "demand_7d_pct": f["next_7d_pct"],
            "listed_supply_kg": analysis["listed_supply_kg"],
            "stated_demand_kg": analysis["stated_demand_kg"],
            "surplus_risk": risk,
            "risk_label": label,
            "confidence": f["confidence"],
        })
    out.sort(key=lambda r: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}[r["surplus_risk"]])
    return out


@router.post("/intelligence/simulate")
def intelligence_simulate(body: dict, user: User = Depends(require_vendor), db: Session = Depends(get_db)):
    """PRD §77A: what-if counterfactual simulation."""
    crop = body.get("crop", "green_chilli")
    harvest_delta = float(body.get("harvest_delta_pct", 0)) / 100
    demand_delta = float(body.get("demand_delta_pct", 0)) / 100
    transport_delta = float(body.get("transport_delta_pct", 0)) / 100

    f = forecast.forecast_demand(db, crop)
    prices = pricing._recent_prices(db, crop, days=14)
    base_price = sum(prices) / len(prices) if prices else crop_meta(crop)["base_price"]
    base_supply = 1000.0
    base_demand = f["current_level"] * 10

    supply = base_supply * (1 + harvest_delta)
    demand = base_demand * (1 + demand_delta)
    price_multiplier = min(1.4, max(0.6, demand / supply if supply else 1))
    new_price = round(base_price * price_multiplier, 1)

    # intervention: aggregate with nearby vendors to capture demand at better price
    intervention_price = round(new_price * 1.04, 1)  # aggregated lots earn a coordination premium
    intervention_logistics = round((1 + transport_delta) * 220, 0)
    baseline_logistics = round(220 * (1 + transport_delta * 0.3), 0)

    do_nothing_net = round(new_price * 30 - baseline_logistics, 0)
    intervention_net = round(intervention_price * 30 - intervention_logistics, 0)

    return {
        "crop": crop,
        "scenario": {
            "harvest_delta_pct": harvest_delta * 100,
            "demand_delta_pct": demand_delta * 100,
            "transport_delta_pct": transport_delta * 100,
        },
        "baseline": {"price": new_price, "net_30kg": do_nothing_net},
        "intervention": {
            "action": "Aggregate supply with 2 nearby vendors before harvest",
            "price": intervention_price,
            "net_30kg": intervention_net,
            "delta": round(intervention_net - do_nothing_net, 0),
        },
        "confidence": f["confidence"],
    }


# --- AMIE: market feasibility engine (AMIE_Final_Revised_PRD.md) ------------

@router.get("/amie/scenarios")
def amie_scenarios(user: User = Depends(require_vendor)):
    """List available disturbance scenarios (PRD §18)."""
    return [{"name": k, "label": v} for k, v in feasibility.SCENARIOS.items()]


@router.post("/amie/analyze")
def amie_analyze(body: dict, user: User = Depends(require_vendor), db: Session = Depends(get_db)):
    """Full AMIE run: market analysis → cascading day-by-day simulation →
    bottlenecks → critical commitments → interventions → counterfactual."""
    crop = body.get("crop", "tomato")
    if crop not in CROPS:
        raise HTTPException(status_code=400, detail="Unknown crop.")
    horizon = int(body.get("horizon_days", 7))
    scenario_name = body.get("scenario", "synchronized_harvest")
    if scenario_name not in feasibility.SCENARIOS:
        raise HTTPException(status_code=400, detail="Unknown scenario.")
    seed = int(body.get("seed", 42))
    stats = feasibility.extract_market_stats(db, crop, user.vendor_profile.district or "Ernakulam")
    return feasibility.run_amie(stats, horizon, scenario_name, seed)


@router.post("/amie/counterfactual")
def amie_counterfactual(body: dict, user: User = Depends(require_vendor), db: Session = Depends(get_db)):
    """Re-simulate with a user-chosen intervention combination (PRD §28)."""
    crop = body.get("crop", "tomato")
    if crop not in CROPS:
        raise HTTPException(status_code=400, detail="Unknown crop.")
    selection = body.get("interventions", [])
    stats = feasibility.extract_market_stats(db, crop, user.vendor_profile.district or "Ernakulam")
    return feasibility.simulate_selection(
        stats,
        int(body.get("horizon_days", 7)),
        body.get("scenario", "synchronized_harvest"),
        int(body.get("seed", 42)),
        selection,
    )


@router.post("/copilot")
async def copilot_endpoint(body: CopilotIn, user: User = Depends(require_vendor), db: Session = Depends(get_db)):
    """PRD Feature 10: conversational copilot over verified tools."""
    return await copilot.answer(db, user.vendor_profile, user, body.question)


@router.get("/earnings")
def earnings(user: User = Depends(require_vendor), db: Session = Depends(get_db)):
    """PRD §35 Screen 5: earnings breakdown."""
    from ..db import Order
    orders = db.query(Order).filter(Order.vendor_id == user.vendor_profile.id).order_by(Order.created_at.desc()).all()
    gross = sum(o.gross_amount for o in orders)
    fees = sum(o.platform_fee for o in orders)
    logi = sum(o.logistics_cost for o in orders)
    delivered = [o for o in orders if o.status == "DELIVERED"]
    today = date.today()
    todays = [o for o in orders if o.created_at.date() == today]
    return {
        "gross": round(gross, 0),
        "platform_fee": round(fees, 0),
        "logistics": round(logi, 0),
        "net": round(gross - fees - logi, 0),
        "order_count": len(orders),
        "today_net": round(sum(o.farmer_payout for o in todays), 0),
        "fulfilment_rate": round(len(delivered) / len(orders) * 100) if orders else 100,
        "recent": [{
            "id": o.id, "crop": o.crop, "quantity_kg": o.quantity_kg, "unit_price": o.unit_price,
            "farmer_payout": o.farmer_payout, "status": o.status, "buyer": o.delivery_location,
            "created_at": o.created_at.isoformat(),
        } for o in orders[:10]],
    }


@router.get("/dashboard")
def vendor_dashboard(user: User = Depends(require_vendor), db: Session = Depends(get_db)):
    """PRD §35 Screen 1: vendor home."""
    vp = user.vendor_profile
    listings = db.query(Listing).filter(Listing.vendor_id == vp.id, Listing.status == "ACTIVE").all()
    today_kg = sum(l.quantity_kg for l in listings if l.harvest_date == date.today())
    price_ctx = pricing.recommend_price(db, "tomato", 30, "A", vp.district or "Ernakulam")

    # buyer opportunity count across vendor's active listings
    opp = 0
    for l in listings:
        opp += len(matching.match_buyers(db, l))

    return {
        "farmer_name": user.name,
        "farm_name": vp.farm_name,
        "today_harvest_kg": round(today_kg, 1),
        "active_listings": len(listings),
        "available_kg": round(sum(l.quantity_available_kg for l in listings), 1),
        "potential_earnings": {"min": round(price_ctx["recommended_min"] * today_kg, 0), "max": round(price_ctx["recommended_max"] * today_kg, 0)},
        "buyer_opportunities": opp,
        "reputation": vp.reputation_score,
    }
