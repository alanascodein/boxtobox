"""SQLAlchemy models + engine/session helpers."""
import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean, Column, Date, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

from .config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def uid() -> str:
    return uuid.uuid4().hex[:12]


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=uid)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String, default="")
    dob = Column(Date, nullable=True)
    language = Column(String, default="en")
    role = Column(String, default="STANDARD_USER")  # STANDARD_USER | VENDOR | ADMIN
    email_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    vendor_profile = relationship("VendorProfile", back_populates="user", uselist=False)


class VendorProfile(Base):
    __tablename__ = "vendor_profiles"
    id = Column(String, primary_key=True, default=uid)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    farm_name = Column(String, default="")
    farm_area = Column(Float, default=0.0)  # acres
    location = Column(String, default="")
    district = Column(String, default="Ernakulam")
    soil_type = Column(String, default="loamy")
    water_availability = Column(String, default="medium")
    reputation_score = Column(Float, default=4.5)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="vendor_profile")
    listings = relationship("Listing", back_populates="vendor")


class Listing(Base):
    __tablename__ = "listings"
    id = Column(String, primary_key=True, default=uid)
    vendor_id = Column(String, ForeignKey("vendor_profiles.id"), nullable=False)
    crop = Column(String, nullable=False)            # slug e.g. green_chilli
    title = Column(String, nullable=False)
    description = Column(Text, default="")
    quantity_kg = Column(Float, nullable=False)
    quantity_available_kg = Column(Float, nullable=False)
    price_per_kg = Column(Float, nullable=False)
    quality_grade = Column(String, default="A")      # A | B | C
    harvest_date = Column(Date, default=date.today)
    image_url = Column(String, default="")
    location = Column(String, default="")
    district = Column(String, default="Ernakulam")
    lot_id = Column(String, default="")
    ai_generated = Column(Boolean, default=False)
    status = Column(String, default="ACTIVE")        # ACTIVE | SOLD_OUT | CLOSED
    created_at = Column(DateTime, default=datetime.utcnow)

    vendor = relationship("VendorProfile", back_populates="listings")


class BuyerProfile(Base):
    __tablename__ = "buyer_profiles"
    id = Column(String, primary_key=True, default=uid)
    user_id = Column(String, ForeignKey("users.id"), unique=True, nullable=False)
    business_name = Column(String, default="")
    buyer_type = Column(String, default="consumer")  # restaurant | retailer | consumer
    location = Column(String, default="")
    district = Column(String, default="Ernakulam")


class Order(Base):
    __tablename__ = "orders"
    id = Column(String, primary_key=True, default=uid)
    buyer_id = Column(String, ForeignKey("users.id"), nullable=False)
    vendor_id = Column(String, ForeignKey("vendor_profiles.id"), nullable=True)
    listing_id = Column(String, ForeignKey("listings.id"), nullable=True)
    crop = Column(String, nullable=False)
    quantity_kg = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    gross_amount = Column(Float, nullable=False)
    logistics_cost = Column(Float, default=0.0)
    platform_fee = Column(Float, default=0.0)
    farmer_payout = Column(Float, default=0.0)
    delivery_location = Column(String, default="")
    status = Column(String, default="PLACED")        # PLACED | CONFIRMED | IN_TRANSIT | DELIVERED | CANCELLED
    created_at = Column(DateTime, default=datetime.utcnow)


class BuyerRequest(Base):
    """A purchase requirement used by the matching engine."""
    __tablename__ = "buyer_requests"
    id = Column(String, primary_key=True, default=uid)
    buyer_id = Column(String, ForeignKey("users.id"), nullable=False)
    crop = Column(String, nullable=False)
    quantity_kg = Column(Float, nullable=False)
    max_price = Column(Float, nullable=False)
    quality = Column(String, default="A")
    delivery_window = Column(String, default="today")
    location = Column(String, default="Kochi")
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class PriceObservation(Base):
    """Synthetic historical market price per crop per day."""
    __tablename__ = "price_observations"
    id = Column(String, primary_key=True, default=uid)
    crop = Column(String, index=True, nullable=False)
    district = Column(String, default="Ernakulam", index=True)
    date = Column(Date, index=True, nullable=False)
    modal_price = Column(Float, nullable=False)
    min_price = Column(Float, nullable=False)
    max_price = Column(Float, nullable=False)


class DemandSignal(Base):
    __tablename__ = "demand_signals"
    id = Column(String, primary_key=True, default=uid)
    crop = Column(String, index=True, nullable=False)
    district = Column(String, default="Ernakulam")
    date = Column(Date, index=True, nullable=False)
    demand_score = Column(Float, nullable=False)     # 0-100


class CopilotLog(Base):
    __tablename__ = "copilot_logs"
    id = Column(String, primary_key=True, default=uid)
    user_id = Column(String, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    provider = Column(String, default="engine")
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
