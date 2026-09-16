"""Listing text generation + harvest analysis (LLM-optional, per PRD §7-§9)."""
import re

from .data import CROPS, crop_name, crop_meta


def analyze_harvest(image_url: str = "", crop_hint: str = "", quantity_kg: float | None = None) -> dict:
    """MVP stand-in for the vision model: classifies from hint text.

    In production this call is routed to a multimodal provider; the response
    schema is identical so the frontend never changes.
    """
    q = (crop_hint or "").lower()
    crop = None
    for slug, meta in CROPS.items():
        if slug in q or meta["name"].lower() in q:
            crop = slug
            break

    if crop:
        confidence = 0.94
    else:
        crop = "tomato"
        confidence = 0.55

    meta = crop_meta(crop)
    grade = "A" if confidence > 0.9 else "B"
    defects: list[str] = []
    if "spot" in q or "bruise" in q:
        grade = "B"
        defects.append("minor surface blemishes visible")

    return {
        "crop": crop,
        "crop_name": crop_name(crop),
        "emoji": meta["emoji"],
        "confidence": confidence,
        "estimated_quality": grade,
        "visible_defects": defects,
        "quantity_kg": quantity_kg,
        "harvest_date": None,
        "note": "Preliminary visual grade — subject to buyer verification." if grade != "A" else None,
        "_needs_manual_crop": confidence < 0.6,
    }


def generate_listing_text(crop: str, quantity_kg: float, quality_grade: str, harvest_label: str, location: str) -> dict:
    """AI description generator (PRD §8). Deterministic template when no LLM key."""
    name = crop_name(crop)
    meta = crop_meta(crop)
    emoji = meta["emoji"]
    title = f"Fresh {name} — Grade {quality_grade}"
    freshness = "Harvested today" if "today" in harvest_label.lower() else f"Harvested {harvest_label}"
    description = (
        f"{freshness}. {quantity_kg:.0f} kg of hand-picked, farm-fresh {name.lower()} "
        f"from {location}. Suitable for restaurants, retailers and household buyers. "
        f"Visually graded {quality_grade} — uniform {meta['category']} quality with careful field handling."
    )
    keywords = [name.lower(), f"fresh {name.lower()}", f"{location} vegetables", f"grade {quality_grade.lower()}", meta["category"]]
    return {
        "title": title,
        "description": description,
        "keywords": keywords,
        "display_name": f"{emoji} {name}",
    }


def extract_quantity_from_text(text: str) -> float | None:
    """Parse spoken quantity like 'thirty kilos' / '30 kg' / '25kg'."""
    t = text.lower().replace(",", "")
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:kg|kilo|kilos|kgs)", t)
    if m:
        return float(m.group(1))
    words = {
        "ten": 10, "fifteen": 15, "twenty": 20, "twenty five": 25, "twenty-five": 25,
        "thirty": 30, "thirty five": 35, "forty": 40, "fifty": 50, "sixty": 60,
        "seventy": 70, "eighty": 80, "ninety": 90, "hundred": 100,
    }
    for w, v in words.items():
        if w in t and ("kilo" in t or "kg" in t):
            return float(v)
    return None
