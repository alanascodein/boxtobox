"""Auth + onboarding endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..auth import create_access_token, get_current_user, hash_password, verify_password
from ..db import BuyerProfile, User, VendorProfile, get_db
from ..schemas import LoginIn, OnboardingIn, SignupIn, TokenOut, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _onboarded(u: User) -> bool:
    if u.role == "VENDOR":
        return u.vendor_profile is not None
    return u.phone != "" or u.role in ("STANDARD_USER", "ADMIN")


@router.post("/signup", response_model=TokenOut)
def signup(body: SignupIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email.lower()).first():
        raise HTTPException(status_code=400, detail="An account with this email already exists.")
    u = User(email=body.email.lower(), name=body.name, password_hash=hash_password(body.password))
    db.add(u)
    db.commit()
    db.refresh(u)
    return TokenOut(token=create_access_token(u), role=u.role, name=u.name, onboarded=False)


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    u = db.query(User).filter(User.email == body.email.lower()).first()
    if not u or not verify_password(body.password, u.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    return TokenOut(token=create_access_token(u), role=u.role, name=u.name, onboarded=_onboarded(u))


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    farm = user.vendor_profile
    return UserOut(
        id=user.id, email=user.email, name=user.name, role=user.role,
        phone=user.phone or "", language=user.language, onboarded=_onboarded(user),
        farm_name=farm.farm_name if farm else "",
        location=(farm.location if farm else "") or "",
        district=(farm.district if farm else "Ernakulam"),
    )


@router.post("/onboard", response_model=UserOut)
def onboard(body: OnboardingIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.phone = body.phone
    user.language = body.language
    if body.dob:
        user.dob = body.dob

    if body.is_vendor:
        user.role = "VENDOR"
        if not user.vendor_profile:
            vp = VendorProfile(
                user_id=user.id, farm_name=body.farm_name or f"{user.name}'s Farm",
                farm_area=body.farm_area, location=body.location, district=body.district,
                soil_type=body.soil_type, water_availability=body.water_availability,
            )
            db.add(vp)
        else:
            vp = user.vendor_profile
            vp.farm_name = body.farm_name or vp.farm_name
            vp.farm_area = body.farm_area or vp.farm_area
            vp.location = body.location or vp.location
            vp.district = body.district or vp.district
    else:
        user.role = user.role if user.role == "ADMIN" else "STANDARD_USER"
        if not db.query(BuyerProfile).filter(BuyerProfile.user_id == user.id).first():
            db.add(BuyerProfile(
                user_id=user.id, business_name=body.business_name,
                buyer_type=body.buyer_type, location=body.location or "Kochi", district="Ernakulam",
            ))

    db.commit()
    db.refresh(user)
    return me(user=user)
