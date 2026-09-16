"""Public marketplace endpoints: listings feed, search, filters, crop catalog, buyer requests."""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..ai.data import CROPS
from ..auth import get_current_user
from ..db import BuyerProfile, BuyerRequest, Listing, User, VendorProfile, get_db
from ..schemas import ListingOut

router = APIRouter(prefix="/api/market", tags=["market"])


def _to_out(l: Listing, db: Session) -> ListingOut:
    vendor = db.get(VendorProfile, l.vendor_id)
    owner = db.get(User, vendor.user_id) if vendor else None
    return ListingOut(
        id=l.id, crop=l.crop, title=l.title, description=l.description,
        quantity_kg=l.quantity_kg, quantity_available_kg=l.quantity_available_kg,
        price_per_kg=l.price_per_kg, quality_grade=l.quality_grade,
        harvest_date=l.harvest_date, image_url=l.image_url,
        location=l.location, district=l.district, lot_id=l.lot_id, status=l.status,
        farm_name=vendor.farm_name if vendor else "",
        vendor_name=owner.name if owner else "",
        reputation_score=vendor.reputation_score if vendor else 4.5,
        created_at=l.created_at.isoformat(),
    )


@router.get("/listings", response_model=list[ListingOut])
def list_listings(
    search: str = "",
    crop: str = "",
    grade: str = "",
    max_price: float | None = Query(default=None),
    sort: str = "newest",
    db: Session = Depends(get_db),
):
    q = db.query(Listing).filter(Listing.status == "ACTIVE", Listing.quantity_available_kg > 0)
    if crop:
        q = q.filter(Listing.crop == crop)
    if grade:
        q = q.filter(Listing.quality_grade == grade)
    if max_price is not None:
        q = q.filter(Listing.price_per_kg <= max_price)
    if search:
        like = f"%{search.lower()}%"
        q = q.filter(or_(
            Listing.title.ilike(like),
            Listing.description.ilike(like),
            Listing.crop.ilike(like),
            Listing.location.ilike(like),
        ))
    if sort == "price_asc":
        q = q.order_by(Listing.price_per_kg.asc())
    elif sort == "price_desc":
        q = q.order_by(Listing.price_per_kg.desc())
    else:
        q = q.order_by(Listing.created_at.desc())
    return [_to_out(l, db) for l in q.limit(60).all()]


@router.get("/listings/{listing_id}", response_model=ListingOut)
def get_listing(listing_id: str, db: Session = Depends(get_db)):
    l = db.get(Listing, listing_id)
    if not l:
        raise HTTPException(status_code=404, detail="Listing not found.")
    return _to_out(l, db)


@router.get("/crops")
def crops():
    return [{"slug": s, "name": m["name"], "emoji": m["emoji"], "category": m["category"]} for s, m in CROPS.items()]


@router.post("/requests")
def create_request(
    body: dict,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    req = BuyerRequest(
        buyer_id=user.id,
        crop=body.get("crop", "tomato"),
        quantity_kg=float(body.get("quantity_kg", 10)),
        max_price=float(body.get("max_price", 100)),
        quality=body.get("quality", "A"),
        delivery_window=body.get("delivery_window", "today"),
        location=body.get("location", "Kochi"),
    )
    db.add(req)
    db.commit()
    return {"ok": True, "id": req.id}


@router.get("/requests")
def my_requests(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    reqs = db.query(BuyerRequest).filter(BuyerRequest.buyer_id == user.id, BuyerRequest.active.is_(True)).all()
    return [{
        "id": r.id, "crop": r.crop, "quantity_kg": r.quantity_kg, "max_price": r.max_price,
        "quality": r.quality, "delivery_window": r.delivery_window, "location": r.location,
    } for r in reqs]
