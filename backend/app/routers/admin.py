"""Admin dashboard metrics (PRD §37)."""
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import require_admin
from ..db import BuyerRequest, Listing, Order, User, VendorProfile, get_db

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/metrics")
def metrics(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    week_ago = date.today() - timedelta(days=7)
    orders = db.query(Order).all()
    gmv = sum(o.gross_amount for o in orders)
    payouts = sum(o.farmer_payout for o in orders)
    logistics = sum(o.logistics_cost for o in orders)
    return {
        "active_farmers": db.query(VendorProfile).count(),
        "active_listings": db.query(Listing).filter(Listing.status == "ACTIVE").count(),
        "buyers": db.query(User).filter(User.role == "STANDARD_USER").count(),
        "orders": len(orders),
        "gmv": round(gmv, 0),
        "farmer_payouts": round(payouts, 0),
        "platform_fees": round(sum(o.platform_fee for o in orders), 0),
        "avg_logistics_cost": round(logistics / len(orders), 0) if orders else 0,
        "sold_out_listings": db.query(Listing).filter(Listing.status == "SOLD_OUT").count(),
        "open_buyer_requests": db.query(BuyerRequest).filter(BuyerRequest.active.is_(True)).count(),
    }
