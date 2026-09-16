"""Order placement + lifecycle (PRD §38 simulated payments, §35 net earnings)."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..ai.logistics import haversine_km
from ..ai.data import location_coords
from ..auth import get_current_user
from ..db import Listing, Order, User, VendorProfile, get_db
from ..schemas import OrderIn, OrderOut

router = APIRouter(prefix="/api/orders", tags=["orders"])


def _out(o: Order, db: Session) -> OrderOut:
    vendor = db.get(VendorProfile, o.vendor_id) if o.vendor_id else None
    buyer = db.get(User, o.buyer_id)
    return OrderOut(
        id=o.id, crop=o.crop, quantity_kg=o.quantity_kg, unit_price=o.unit_price,
        gross_amount=o.gross_amount, logistics_cost=o.logistics_cost,
        platform_fee=o.platform_fee, farmer_payout=o.farmer_payout,
        status=o.status, delivery_location=o.delivery_location,
        created_at=o.created_at.isoformat(), listing_id=o.listing_id or "",
        vendor_name=vendor.farm_name if vendor else "",
        buyer_name=buyer.name if buyer else "",
    )


@router.post("", response_model=OrderOut)
def place_order(body: OrderIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    l = db.get(Listing, body.listing_id)
    if not l or l.status != "ACTIVE":
        raise HTTPException(status_code=404, detail="Listing not available.")
    if l.quantity_available_kg < body.quantity_kg:
        raise HTTPException(status_code=400, detail=f"Only {l.quantity_available_kg:.0f} kg available.")

    buyer_loc = location_coords(body.delivery_location)
    listing_loc = location_coords(l.location)
    dist = haversine_km((buyer_loc["lat"], buyer_loc["lng"]), (listing_loc["lat"], listing_loc["lng"]))

    gross = round(body.quantity_kg * l.price_per_kg, 0)
    logistics = round(dist * 14 * 0.5 + body.quantity_kg * 0.6, 0)  # buyer-paid share
    platform_fee = round(gross * 0.03, 0)
    farmer_payout = round(gross - platform_fee - round(dist * 14 * 0.5, 0), 0)

    o = Order(
        buyer_id=user.id, vendor_id=l.vendor_id, listing_id=l.id,
        crop=l.crop, quantity_kg=body.quantity_kg, unit_price=l.price_per_kg,
        gross_amount=gross, logistics_cost=logistics, platform_fee=platform_fee,
        farmer_payout=farmer_payout, delivery_location=body.delivery_location,
        status="CONFIRMED",
    )
    l.quantity_available_kg = round(l.quantity_available_kg - body.quantity_kg, 1)
    if l.quantity_available_kg <= 0.01:
        l.status = "SOLD_OUT"
    db.add(o)
    db.commit()
    db.refresh(o)
    return _out(o, db)


@router.get("/mine", response_model=list[OrderOut])
def my_orders(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role == "VENDOR":
        orders = db.query(Order).filter(Order.vendor_id == user.vendor_profile.id).order_by(Order.created_at.desc()).all()
    else:
        orders = db.query(Order).filter(Order.buyer_id == user.id).order_by(Order.created_at.desc()).all()
    return [_out(o, db) for o in orders]


@router.post("/{order_id}/status")
def advance_status(order_id: str, body: dict, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    o = db.get(Order, order_id)
    if not o:
        raise HTTPException(status_code=404, detail="Order not found.")
    if user.role == "VENDOR" and o.vendor_id != user.vendor_profile.id:
        raise HTTPException(status_code=403, detail="Not your order.")
    if user.role == "STANDARD_USER" and o.buyer_id != user.id:
        raise HTTPException(status_code=403, detail="Not your order.")
    new_status = body.get("status", "")
    allowed = {"CONFIRMED", "IN_TRANSIT", "DELIVERED", "CANCELLED"}
    if new_status not in allowed:
        raise HTTPException(status_code=400, detail="Invalid status.")
    o.status = new_status
    db.commit()
    return {"ok": True, "status": o.status}
