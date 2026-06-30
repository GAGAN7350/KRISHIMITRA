"""
Crop and soil knowledge base for Indian agriculture.
Provides crop recommendations, fertilizer advice, and planting calendars
based on soil type, season, and region — curated for Karnataka, Maharashtra,
Andhra Pradesh, and other major Indian farming states.
"""

# ─────────────────────────────────────────────
# KNOWLEDGE BASE DATA
# ─────────────────────────────────────────────

# Crop suitability: soil_type → season → list of suitable crops
CROP_SUITABILITY = {
    "red loamy": {
        "kharif": ["ragi", "groundnut", "maize", "cotton", "jowar"],
        "rabi": ["wheat", "sunflower", "safflower", "chickpea"],
        "summer": ["watermelon", "cucumber", "bitter gourd"],
        "zaid": ["watermelon", "muskmelon", "moong"],
    },
    "red": {
        "kharif": ["ragi", "groundnut", "maize", "cotton"],
        "rabi": ["wheat", "chickpea", "safflower"],
        "summer": ["watermelon", "cucumber"],
        "zaid": ["watermelon", "muskmelon"],
    },
    "black cotton": {
        "kharif": ["cotton", "soybean", "jowar", "tur (pigeon pea)", "maize"],
        "rabi": ["wheat", "chickpea", "sunflower", "linseed"],
        "summer": ["sunflower", "sesame"],
        "zaid": ["moong", "sesame"],
    },
    "black": {
        "kharif": ["cotton", "soybean", "jowar", "sorghum"],
        "rabi": ["wheat", "chickpea", "gram"],
        "summer": ["sesame", "sunflower"],
        "zaid": ["moong", "sesame"],
    },
    "alluvial": {
        "kharif": ["rice", "maize", "jute", "sugarcane", "cotton"],
        "rabi": ["wheat", "mustard", "barley", "peas"],
        "summer": ["rice", "vegetables"],
        "zaid": ["rice", "moong", "watermelon"],
    },
    "sandy": {
        "kharif": ["bajra", "groundnut", "moong", "cowpea"],
        "rabi": ["wheat", "barley", "mustard"],
        "summer": ["watermelon", "muskmelon", "cucumber"],
        "zaid": ["watermelon", "moong"],
    },
    "laterite": {
        "kharif": ["cashew", "coconut", "rubber", "tapioca", "rice"],
        "rabi": ["cassava", "turmeric"],
        "summer": ["banana", "pineapple"],
        "zaid": ["banana", "pineapple"],
    },
    "loamy": {
        "kharif": ["rice", "maize", "cotton", "groundnut", "sugarcane"],
        "rabi": ["wheat", "potato", "mustard", "peas"],
        "summer": ["vegetables", "cucumber", "tomato"],
        "zaid": ["moong", "tomato", "cucumber"],
    },
}

# Default fallback for unknown soil types
DEFAULT_CROPS = {
    "kharif": ["rice", "maize", "groundnut"],
    "rabi": ["wheat", "chickpea", "mustard"],
    "summer": ["watermelon", "cucumber", "moong"],
    "zaid": ["moong", "watermelon"],
}

# Fertilizer recommendations: crop → {soil_type → advice}
FERTILIZER_DATA = {
    "tomato": {
        "default": "Apply NPK (19:19:19) at transplanting. Side-dress with urea (100 kg/ha) at flowering. Use calcium nitrate to prevent blossom end rot. Avoid excess nitrogen after fruit set.",
        "red loamy": "Tomato does well in red soil. Add 5 tonnes FYM/ha before planting. Apply NPK 100:60:50 kg/ha. Micronutrient spray (boron + zinc) at flowering improves fruit quality.",
    },
    "rice": {
        "default": "Apply 120:60:40 kg/ha of N:P:K. Split nitrogen: 1/3 basal, 1/3 at tillering, 1/3 at panicle initiation. Use zinc sulphate (25 kg/ha) if deficiency observed.",
        "alluvial": "Alluvial soil is well-suited for rice. Basal dose: 60 kg N + 60 kg P2O5 + 40 kg K2O/ha. Top-dress urea at 21 and 45 days after transplanting.",
    },
    "wheat": {
        "default": "Apply 120:60:40 kg/ha of N:P:K. Full phosphorus and potassium as basal. Split nitrogen: half at sowing, half at first irrigation (CRI stage).",
        "black cotton": "Black soil retains phosphorus well. Apply 120:40:30 kg/ha N:P:K. Add 2 tonnes FYM to improve structure.",
    },
    "cotton": {
        "default": "Apply 150:75:75 kg/ha of N:P:K for Bt cotton. Boron and sulphur are critical micronutrients. Avoid excess nitrogen which promotes vegetative growth over boll formation.",
        "black cotton": "Black soil is ideal for cotton. Apply FYM (10 t/ha) + NPK 120:60:60 kg/ha. Top-dress urea at squaring and boll development stages.",
    },
    "maize": {
        "default": "Apply 180:80:60 kg/ha of N:P:K. Apply full P and K as basal with 1/3 N. Top-dress remaining nitrogen in 2 splits at knee-high stage and tasselling.",
    },
    "groundnut": {
        "default": "Apply 25:50:75 kg/ha of N:P:K. Groundnut is a legume — minimal nitrogen needed. Gypsum (400 kg/ha) at pegging stage improves pod filling. Ensure good calcium supply.",
        "red loamy": "Red sandy loam is ideal for groundnut. Apply rhizobium seed treatment to fix nitrogen. Gypsum application is critical at peg initiation.",
    },
    "ragi": {
        "default": "Apply 60:40:20 kg/ha of N:P:K. FYM application (5 t/ha) recommended. Top-dress urea at 30 and 60 days after sowing. Ragi is drought-tolerant — avoid waterlogging.",
    },
    "soybean": {
        "default": "Apply 30:80:40 kg/ha of N:P:K. Rhizobium inoculation reduces nitrogen requirement. Sulphur (20 kg/ha) improves protein content. Lime if soil pH < 6.0.",
    },
    "onion": {
        "default": "Apply 100:50:50 kg/ha of N:P:K. Split nitrogen: 1/3 basal, 1/3 at 30 days, 1/3 at 45 days. Stop nitrogen 30 days before harvest to improve storability.",
    },
    "sugarcane": {
        "default": "Apply 250:100:100 kg/ha of N:P:K over the season. FYM (25 t/ha) improves yields. Split nitrogen in 3–4 doses. Trash mulching reduces weed pressure.",
    },
}

# Planting calendar: crop → region → {sowing, harvest, duration_days}
PLANTING_CALENDAR = {
    "tomato": {
        "karnataka": {"sowing": "June–July (Kharif), October–November (Rabi)", "harvest": "Sept–Oct, Feb–Mar", "duration_days": "90–120"},
        "maharashtra": {"sowing": "June–July, Oct–Nov", "harvest": "Sept–Nov, Jan–Mar", "duration_days": "90–120"},
        "default": {"sowing": "June–July or October–November", "harvest": "90–120 days after transplanting", "duration_days": "90–120"},
    },
    "rice": {
        "karnataka": {"sowing": "June–July (transplanting)", "harvest": "November–December", "duration_days": "120–150"},
        "andhra pradesh": {"sowing": "June–July (Kharif), Nov–Dec (Rabi)", "harvest": "Oct–Nov, Mar–Apr", "duration_days": "115–135"},
        "default": {"sowing": "June–July for Kharif", "harvest": "October–December", "duration_days": "120–150"},
    },
    "wheat": {
        "punjab": {"sowing": "November 1–15", "harvest": "April", "duration_days": "140–160"},
        "karnataka": {"sowing": "October–November", "harvest": "February–March", "duration_days": "100–120"},
        "default": {"sowing": "October–December (Rabi season)", "harvest": "February–April", "duration_days": "110–150"},
    },
    "maize": {
        "karnataka": {"sowing": "June–July", "harvest": "September–October", "duration_days": "90–110"},
        "default": {"sowing": "June–July (Kharif)", "harvest": "September–October", "duration_days": "90–115"},
    },
    "groundnut": {
        "karnataka": {"sowing": "June–July", "harvest": "October–November", "duration_days": "105–120"},
        "andhra pradesh": {"sowing": "June–July (Kharif), Jan (Rabi/Summer)", "harvest": "Oct–Nov, Apr–May", "duration_days": "100–120"},
        "default": {"sowing": "June–July", "harvest": "October–November", "duration_days": "100–120"},
    },
    "cotton": {
        "karnataka": {"sowing": "May–June", "harvest": "October–January (pick over 3 months)", "duration_days": "160–200"},
        "default": {"sowing": "May–June", "harvest": "October–January", "duration_days": "160–200"},
    },
    "ragi": {
        "karnataka": {"sowing": "June–July", "harvest": "November–December", "duration_days": "120–130"},
        "default": {"sowing": "June–July (Kharif)", "harvest": "October–December", "duration_days": "115–130"},
    },
    "onion": {
        "karnataka": {"sowing": "Kharif: May–June; Rabi: Oct–Nov", "harvest": "Kharif: Sep–Oct; Rabi: Jan–Feb", "duration_days": "100–120"},
        "maharashtra": {"sowing": "Oct–Nov (Rabi)", "harvest": "January–March", "duration_days": "100–120"},
        "default": {"sowing": "October–November (Rabi)", "harvest": "January–March", "duration_days": "100–120"},
    },
}


# ─────────────────────────────────────────────
# TOOL FUNCTIONS
# ─────────────────────────────────────────────

def recommend_crops(soil_type: str, season: str, region: str = "") -> dict:
    """
    Recommends the top crops to grow based on soil type, season, and region.

    Args:
        soil_type: Type of soil (e.g., "red loamy", "black cotton", "alluvial", "sandy", "laterite").
        season: Farming season (e.g., "Kharif", "Rabi", "Zaid", "Summer").
        region: Optional. State or region name (e.g., "Karnataka", "Maharashtra").

    Returns:
        A dictionary with recommended crops, their brief rationale, and a summary.
    """
    soil_lower = soil_type.lower().strip()
    season_lower = season.lower().strip()

    # Match season
    season_map = {
        "kharif": "kharif", "monsoon": "kharif", "june": "kharif", "july": "kharif",
        "rabi": "rabi", "winter": "rabi", "october": "rabi", "november": "rabi",
        "zaid": "zaid", "summer": "summer", "april": "summer", "may": "summer",
    }
    matched_season = next((v for k, v in season_map.items() if k in season_lower), "kharif")

    # Match soil
    matched_soil = None
    for soil_key in CROP_SUITABILITY:
        if soil_key in soil_lower or soil_lower in soil_key:
            matched_soil = soil_key
            break

    crops = (
        CROP_SUITABILITY.get(matched_soil, DEFAULT_CROPS).get(matched_season, [])
        if matched_soil
        else DEFAULT_CROPS.get(matched_season, [])
    )

    top_crops = crops[:5] if len(crops) >= 5 else crops

    summary = (
        f"For {soil_type} soil in the {matched_season.capitalize()} season"
        f"{' in ' + region if region else ''}, recommended crops are: "
        f"{', '.join(top_crops)}."
    )

    return {
        "soil_type": soil_type,
        "season": matched_season,
        "region": region,
        "recommended_crops": top_crops,
        "summary": summary,
    }


def get_fertilizer_advice(crop: str, soil_type: str = "default") -> str:
    """
    Returns fertilizer and nutrient management advice for a specific crop and soil type.

    Args:
        crop: The name of the crop (e.g., "tomato", "wheat", "rice", "cotton").
        soil_type: The soil type (e.g., "red loamy", "black cotton"). Optional.

    Returns:
        A natural language fertilizer recommendation string.
    """
    crop_lower = crop.lower().strip()
    soil_lower = soil_type.lower().strip()

    crop_data = FERTILIZER_DATA.get(crop_lower)
    if not crop_data:
        return (
            f"Specific fertilizer data for '{crop}' is not in our database. "
            f"As a general rule: apply balanced NPK (120:60:40 kg/ha) with 5 tonnes of FYM/ha before sowing. "
            f"Consult your local KVK (Krishi Vigyan Kendra) for soil-test-based recommendations."
        )

    # Try soil-specific advice first, then fall back to default
    advice = crop_data.get(soil_lower) or crop_data.get("default", "")
    return f"Fertilizer advice for {crop.capitalize()} on {soil_type} soil: {advice}"


def get_planting_calendar(crop: str, region: str = "") -> dict:
    """
    Returns the recommended sowing and harvesting dates for a crop in a given region.

    Args:
        crop: The name of the crop (e.g., "tomato", "rice", "wheat").
        region: Optional. State or region (e.g., "Karnataka", "Punjab", "Maharashtra").

    Returns:
        A dictionary with sowing_window, harvest_window, duration_days, and a summary.
    """
    crop_lower = crop.lower().strip()
    region_lower = region.lower().strip()

    crop_calendar = PLANTING_CALENDAR.get(crop_lower)
    if not crop_calendar:
        return {
            "crop": crop,
            "region": region,
            "summary": (
                f"Planting calendar for '{crop}' is not in our database. "
                f"Please consult your nearest KVK or State Agricultural University for local recommendations."
            ),
        }

    # Try region-specific, then default
    region_data = crop_calendar.get(region_lower) or crop_calendar.get("default", {})

    summary = (
        f"Planting calendar for {crop.capitalize()} in {region or 'India'}: "
        f"Sowing: {region_data.get('sowing', 'N/A')}. "
        f"Harvest: {region_data.get('harvest', 'N/A')}. "
        f"Crop duration: {region_data.get('duration_days', 'N/A')} days."
    )

    return {
        "crop": crop,
        "region": region or "India (general)",
        "sowing_window": region_data.get("sowing", "N/A"),
        "harvest_window": region_data.get("harvest", "N/A"),
        "duration_days": region_data.get("duration_days", "N/A"),
        "summary": summary,
    }
