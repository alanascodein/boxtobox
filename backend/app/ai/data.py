"""Reference data: crop catalog and Kochi/Ernakulam locations (synthetic)."""

# slug -> catalog entry (base prices in ₹/kg typical for Kerala markets)
CROPS = {
    "tomato": {"name": "Tomato", "emoji": "🍅", "base_price": 34.0, "harvest_days": 75, "perish_days": 6, "category": "vegetable"},
    "green_chilli": {"name": "Green Chilli", "emoji": "🌶️", "base_price": 62.0, "harvest_days": 80, "perish_days": 5, "category": "spice"},
    "beans": {"name": "Beans", "emoji": "🫛", "base_price": 48.0, "harvest_days": 55, "perish_days": 6, "category": "vegetable"},
    "cucumber": {"name": "Cucumber", "emoji": "🥒", "base_price": 28.0, "harvest_days": 50, "perish_days": 7, "category": "vegetable"},
    "banana": {"name": "Banana", "emoji": "🍌", "base_price": 42.0, "harvest_days": 110, "perish_days": 8, "category": "fruit"},
    "spinach": {"name": "Spinach", "emoji": "🥬", "base_price": 24.0, "harvest_days": 30, "perish_days": 3, "category": "leafy"},
}

# Approximate localities around Kochi / Ernakulam (synthetic reference points)
LOCATIONS = {
    "Kochi": {"lat": 9.931, "lng": 76.267},
    "Ernakulam": {"lat": 9.982, "lng": 76.296},
    "Aluva": {"lat": 10.107, "lng": 76.351},
    "Tripunithura": {"lat": 9.946, "lng": 76.328},
    "Kakkanad": {"lat": 10.001, "lng": 76.308},
    "Mattancherry": {"lat": 9.958, "lng": 76.259},
    "Paravur": {"lat": 10.147, "lng": 76.333},
    "Vyttila": {"lat": 9.967, "lng": 76.318},
}

DEFAULT_LOCATION = "Ernakulam"


def crop_name(slug: str) -> str:
    return CROPS.get(slug, {}).get("name", slug.replace("_", " ").title())


def crop_meta(slug: str) -> dict:
    return CROPS.get(slug, CROPS["tomato"])


def location_coords(name: str) -> dict | None:
    for key, v in LOCATIONS.items():
        if key.lower() in (name or "").lower():
            return v
    return LOCATIONS[DEFAULT_LOCATION]
