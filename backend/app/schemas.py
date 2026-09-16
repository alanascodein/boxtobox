"""Pydantic schemas for request/response validation."""
from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class SignupIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(min_length=2)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    token: str
    role: str
    name: str
    onboarded: bool


class OnboardingIn(BaseModel):
    phone: str = ""
    dob: Optional[date] = None
    language: str = "en"
    is_vendor: bool
    # vendor fields
    farm_name: str = ""
    farm_area: float = 0
    location: str = ""
    district: str = "Ernakulam"
    soil_type: str = "loamy"
    water_availability: str = "medium"
    # buyer fields
    business_name: str = ""
    buyer_type: str = "consumer"


class UserOut(BaseModel):
    id: str
    email: str
    name: str
    role: str
    phone: str
    language: str
    onboarded: bool
    farm_name: str = ""
    location: str = ""
    district: str = ""


class ListingIn(BaseModel):
    crop: str
    title: str
    description: str = ""
    quantity_kg: float = Field(gt=0)
    price_per_kg: float = Field(gt=0)
    quality_grade: Literal["A", "B", "C"] = "A"
    harvest_date: Optional[date] = None
    image_url: str = ""
    ai_generated: bool = False


class ListingOut(BaseModel):
    id: str
    crop: str
    title: str
    description: str
    quantity_kg: float
    quantity_available_kg: float
    price_per_kg: float
    quality_grade: str
    harvest_date: date
    image_url: str
    location: str
    district: str
    lot_id: str
    status: str
    farm_name: str = ""
    vendor_name: str = ""
    reputation_score: float = 4.5
    created_at: str


class OrderIn(BaseModel):
    listing_id: str
    quantity_kg: float = Field(gt=0)
    delivery_location: str = "Kochi"


class OrderOut(BaseModel):
    id: str
    crop: str
    quantity_kg: float
    unit_price: float
    gross_amount: float
    logistics_cost: float
    platform_fee: float
    farmer_payout: float
    status: str
    delivery_location: str
    created_at: str
    listing_id: str = ""
    vendor_name: str = ""
    buyer_name: str = ""


class HarvestAnalysisIn(BaseModel):
    crop_hint: str = ""
    quantity_kg: Optional[float] = None
    image_url: str = ""


class PriceIn(BaseModel):
    crop: str
    quantity_kg: float = 30
    quality_grade: str = "A"
    location: str = "Ernakulam"


class CopilotIn(BaseModel):
    question: str
