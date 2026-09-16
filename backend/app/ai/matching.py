"""Buyer matching (PRD §11 weighted scores) + supply aggregation (PRD §12 greedy)."""
import math
from datetime import date

from sqlalchemy.orm import Session

from ..db import BuyerProfile, BuyerRequest, User, VendorProfile
from .data import location_coords


def haversine_km(a: tuple, b: tuple) -> float:
    lat1, lng1, lat2, lng2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    dlat, dlng = lat2 - lat1, lng2 - lng1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng / 2) ** 2
    return round(6371 * 2 * math.asin(math.sqrt(h)), 1)


def match_buyers(db: Session, listing) -> list[dict]:
    """Score active buyer requirements against a listing (weights from PRD §11)."""
    listing_loc = location_coords(listing.location)
    results = []
    for req in db.query(BuyerRequest).filter(BuyerRequest.active.is_(True)).all():
        crop_score = 1.0 if req.crop == listing.crop else 0.0
        if crop_score == 0.0:
            continue

        qty_ratio = min(listing.quantity_available_kg, req.quantity_kg) / req.quantity_kg
        qty_score = max(0.0, min(1.0, qty_ratio))

        price_score = 1.0 if listing.price_per_kg <= req.max_price else max(0.0, 1 - (listing.price_per_kg - req.max_price) / req.max_price)

        req_loc = location_coords(req.location)
        dist = haversine_km((listing_loc["lat"], listing_loc["lng"]), (req_loc["lat"], req_loc["lng"]))
        dist_score = max(0.0, 1 - dist / 40.0)  # 40 km → 0

        quality_score = 1.0 if listing.quality_grade == req.quality else (0.6 if listing.quality_grade == "A" else 0.3)

        time_score = 0.8 if "today" in req.delivery_window else 0.6

        score = (
            crop_score * 0.30
            + qty_score * 0.20
            + price_score * 0.15
            + dist_score * 0.15
            + quality_score * 0.10
            + time_score * 0.10
        )

        buyer = db.get(User, req.buyer_id)
        profile = db.query(BuyerProfile).filter(BuyerProfile.user_id == req.buyer_id).first()
        results.append({
            "request_id": req.id,
            "buyer_name": (profile.business_name if profile and profile.business_name else buyer.name) if buyer else "Buyer",
            "buyer_type": profile.buyer_type if profile else "consumer",
            "crop": req.crop,
            "quantity_kg": req.quantity_kg,
            "max_price": req.max_price,
            "distance_km": dist,
            "delivery_window": req.delivery_window,
            "location": req.location,
            "match_score": round(score * 100),
            "match_pct": round(score * 100),
        })

    results.sort(key=lambda r: r["match_score"], reverse=True)
    return results[:8]


def aggregate_supply(db: Session, crop: str, needed_kg: float, buyer_location: str = "Kochi") -> dict:
    """Greedy aggregation: pick nearest compatible listings until requirement met."""
    listings = (
        db.query(Listing_)
        .filter(Listing_.crop == crop, Listing_.status == "ACTIVE", Listing_.quantity_available_kg > 0)
        .order_by(Listing_.price_per_kg)
        .all()
        if (Listing_ := _listing_model()) is not None
        else []
    )
    buyer_loc = location_coords(buyer_location)
    chosen, remaining = [], needed_kg
    for l in listings:
        if remaining <= 0:
            break
        take = min(l.quantity_available_kg, remaining)
        vendor = db.get(VendorProfile, l.vendor_id)
        vloc = location_coords(l.location)
        dist = haversine_km((vloc["lat"], vloc["lng"]), (buyer_loc["lat"], buyer_loc["lng"]))
        chosen.append({
            "listing_id": l.id,
            "farm_name": vendor.farm_name if vendor else "Farm",
            "farmer_location": l.location,
            "distance_km": dist,
            "take_kg": round(take, 1),
            "price_per_kg": l.price_per_kg,
            "quality_grade": l.quality_grade,
            "lot_id": l.lot_id,
        })
        remaining -= take

    fulfilled = needed_kg - max(0.0, remaining)
    total_cost = sum(c["take_kg"] * c["price_per_kg"] for c in chosen)
    platform_fee = round(total_cost * 0.03, 0)
    route_cost = round(sum(c["distance_km"] for c in chosen) * 14, 0)  # ₹14/km
    farmers_net = round(total_cost - platform_fee, 0)

    return {
        "crop": crop,
        "required_kg": needed_kg,
        "fulfilled_kg": round(fulfilled, 1),
        "complete": fulfilled >= needed_kg - 0.01,
        "farmers": chosen,
        "farmer_count": len(chosen),
        "total_cost": round(total_cost, 0),
        "avg_price": round(total_cost / fulfilled, 1) if fulfilled else 0,
        "platform_fee": platform_fee,
        "logistics_cost": route_cost,
        "farmers_net_payout": farmers_net,
    }


def _listing_model():
    from ..db import Listing
    return Listing
