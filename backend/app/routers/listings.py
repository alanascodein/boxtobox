"""Vendor listing management."""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import require_vendor
from ..db import Listing, User, VendorProfile, get_db
from ..schemas import ListingIn, ListingOut

router = APIRouter(prefix="/api/listings", tags=["listings"])


def _lot_id(crop: str, district: str) -> str:
    import random
    return f"LOT-{district[:2].upper()}-{date.today().year}-{random.randint(10000, 99999)}"


@router.post("", response_model=ListingOut)
def create_listing(
    body: ListingIn,
    user: User = Depends(require_vendor),
    db: Session = Depends(get_db),
):
    vp: VendorProfile = user.vendor_profile
    l = Listing(
        vendor_id=vp.id,
        crop=body.crop,
        title=body.title,
        description=body.description,
        quantity_kg=body.quantity_kg,
        quantity_available_kg=body.quantity_kg,
        price_per_kg=body.price_per_kg,
        quality_grade=body.quality_grade,
        harvest_date=body.harvest_date or date.today(),
        image_url=body.image_url,
        location=vp.location or "Ernakulam",
        district=vp.district or "Ernakulam",
        lot_id=_lot_id(body.crop, vp.district or "KL"),
        ai_generated=body.ai_generated,
    )
    db.add(l)
    db.commit()
    db.refresh(l)

    from .public import _to_out
    return _to_out(l, db)


@router.get("/mine")
def my_listings(user: User = Depends(require_vendor), db: Session = Depends(get_db)):
    ls = db.query(Listing).filter(Listing.vendor_id == user.vendor_profile.id).order_by(Listing.created_at.desc()).all()
    from .public import _to_out
    return [_to_out(l, db) for l in ls]


@router.delete("/{listing_id}")
def close_listing(listing_id: str, user: User = Depends(require_vendor), db: Session = Depends(get_db)):
    l = db.get(Listing, listing_id)
    if not l or l.vendor_id != user.vendor_profile.id:
        raise HTTPException(status_code=404, detail="Listing not found.")
    l.status = "CLOSED"
    db.commit()
    return {"ok": True}
