"""Synthetic demo data per PRD §45: Kochi/Ernakulam focus, 180-day history."""
import random
from datetime import date, datetime, timedelta

from sqlalchemy.orm import Session

from .ai.data import CROPS, LOCATIONS
from .auth import hash_password
from .db import (
    BuyerProfile, BuyerRequest, DemandSignal, Listing, Order, PriceObservation,
    SessionLocal, User, VendorProfile, init_db,
)

random.seed(42)

VENDORS = [
    ("ravi@farmmesh.demo", "Ravi Kumar", "Sunrise Farm", "Aluva", 0.6, ["tomato", "green_chilli", "beans"]),
    ("meera@farmmesh.demo", "Meera Nair", "Green Terrace Growers", "Tripunithura", 0.4, ["cucumber", "spinach", "beans"]),
    ("joseph@farmmesh.demo", "Joseph Mathew", "Periyar Fresh", "Paravur", 1.2, ["banana", "tomato", "green_chilli"]),
    ("fatima@farmmesh.demo", "Fatima Beevi", "Harbour Leaf Farm", "Mattancherry", 0.3, ["spinach", "green_chilli"]),
    ("suresh@farmmesh.demo", "Suresh Menon", "Backwater Veggies", "Vyttila", 0.8, ["tomato", "cucumber", "beans"]),
]

BUYERS = [
    ("chef@harbourkitchen.demo", "Chef Anand", "Harbour Kitchen", "restaurant", "Kochi"),
    ("procure@freshmart.demo", "Priya Menon", "FreshMart Retail", "retailer", "Kakkanad"),
    ("orders@saibhojans.demo", "Lakshmi S", "Sai Bhojans Catering", "restaurant", "Ernakulam"),
]

BUYER_REQUESTS = [
    ("green_chilli", 50, 75, "A", "today", "Kochi"),
    ("tomato", 120, 42, "A", "today_evening", "Kochi"),
    ("tomato", 100, 40, "B", "tomorrow", "Kakkanad"),
    ("beans", 70, 55, "A", "today", "Ernakulam"),
    ("cucumber", 60, 34, "A", "today_evening", "Vyttila"),
    ("spinach", 40, 30, "A", "today", "Kochi"),
    ("banana", 80, 48, "B", "tomorrow", "Kochi"),
    ("green_chilli", 30, 80, "A", "today_evening", "Aluva"),
]


def seed_if_empty() -> None:
    db: Session = SessionLocal()
    try:
        if db.query(User).count() > 0:
            return

        admin = User(email="admin@farmmesh.demo", name="FarmMesh Admin",
                     password_hash=hash_password("admin1234"), role="ADMIN")
        db.add(admin)

        vendor_users: list[tuple[User, VendorProfile, list]] = []
        for email, name, farm, loc, area, crops in VENDORS:
            u = User(email=email, name=name, password_hash=hash_password("farm1234"), role="VENDOR")
            vp = VendorProfile(user=u, farm_name=farm, farm_area=area, location=loc,
                               district="Ernakulam", reputation_score=round(random.uniform(4.2, 4.9), 1))
            db.add_all([u, vp])
            db.flush()
            vendor_users.append((u, vp, crops))

        buyer_users = []
        for email, name, biz, btype, loc in BUYERS:
            u = User(email=email, name=name, password_hash=hash_password("buyer1234"), role="STANDARD_USER")
            db.add(u)
            db.flush()
            db.add(BuyerProfile(user_id=u.id, business_name=biz, buyer_type=btype, location=loc, district="Ernakulam"))
            buyer_users.append((u, biz, btype, loc))

        # 180 days of synthetic market prices + demand signals per crop
        today = date.today()
        for slug, meta in CROPS.items():
            base = meta["base_price"]
            level = 0.5
            for d in range(180, -1, -1):
                day = today - timedelta(days=d)
                seasonal = 1 + 0.10 * ((d % 90) / 90 - 0.5) * 2
                noise = random.uniform(-0.07, 0.07)
                shock = 1.18 if (slug == "green_chilli" and 20 <= d <= 45) else 1.0
                modal = round(base * seasonal * shock * (1 + noise), 1)
                db.add(PriceObservation(
                    crop=slug, district="Ernakulam", date=day,
                    modal_price=modal, min_price=round(modal * 0.9, 1), max_price=round(modal * 1.12, 1),
                ))
                level = 0.25 * random.uniform(35, 85) + 0.75 * level
                db.add(DemandSignal(crop=slug, district="Ernakulam", date=day, demand_score=round(level, 1)))

        # fresh listings from each vendor
        for u, vp, crops in vendor_users:
            for crop in crops:
                meta = CROPS[crop]
                qty = random.choice([20, 25, 30, 35, 40, 60, 80])
                price = round(meta["base_price"] * random.uniform(0.92, 1.1), 0)
                db.add(Listing(
                    vendor_id=vp.id, crop=crop,
                    title=f"Fresh {meta['name']} — Grade A",
                    description=f"Harvested today at {vp.farm_name}, {vp.location}. Hand-picked, farm-fresh quality.",
                    quantity_kg=qty, quantity_available_kg=qty, price_per_kg=price,
                    quality_grade="A", harvest_date=date.today(),
                    location=vp.location, district=vp.district,
                    lot_id=f"LOT-EK-2026-{random.randint(10000, 99999)}",
                ))

        for crop, qty, maxp, quality, window, loc in BUYER_REQUESTS:
            u = random.choice(buyer_users)
            db.add(BuyerRequest(buyer_id=u[0].id, crop=crop, quantity_kg=qty, max_price=maxp,
                                quality=quality, delivery_window=window, location=loc))

        # a few completed orders for the earnings story
        demo_vendors = vendor_users[:3]
        for i in range(8):
            u, vp, crops = random.choice(demo_vendors)
            crop = random.choice(crops)
            meta = CROPS[crop]
            qty = random.choice([15, 20, 30])
            price = round(meta["base_price"] * random.uniform(0.95, 1.05), 0)
            gross = qty * price
            fee = round(gross * 0.03, 0)
            logi = random.choice([120, 150, 180, 220])
            buyer = random.choice(buyer_users)
            db.add(Order(
                buyer_id=buyer[0].id, vendor_id=vp.id, crop=crop, quantity_kg=qty,
                unit_price=price, gross_amount=gross, logistics_cost=logi, platform_fee=fee,
                farmer_payout=round(gross - fee - logi / 2, 0),
                delivery_location=buyer[3],
                status=random.choice(["DELIVERED", "DELIVERED", "CONFIRMED", "IN_TRANSIT"]),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 12)),
            ))

        db.commit()
    finally:
        db.close()
