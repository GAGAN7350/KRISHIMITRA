"""
Market pricing tool using the data.gov.in Agmarknet Commodity Prices API.
Fetches live mandi (agricultural market) prices for crops across Indian APMCs.
API Docs: https://data.gov.in/resource/current-daily-price-various-commodities-various-markets-mandi
"""

import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

AGMARKNET_API_KEY = os.getenv("AGMARKNET_API_KEY", "")
AGMARKNET_BASE_URL = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"

# Commodity name mapping for common aliases
COMMODITY_ALIASES = {
    "tomato": "Tomato",
    "onion": "Onion",
    "potato": "Potato",
    "rice": "Rice",
    "wheat": "Wheat",
    "maize": "Maize",
    "corn": "Maize",
    "cotton": "Cotton",
    "groundnut": "Groundnut",
    "soybean": "Soybean",
    "chili": "Dry Chillies",
    "chilli": "Dry Chillies",
    "green chili": "Green Chilli",
    "banana": "Banana",
    "mango": "Mango",
    "jowar": "Jowar(Sorghum)",
    "bajra": "Bajra(Pearl Millet/Cumbu)",
    "ragi": "Ragi (Finger Millet/Naachanie)",
    "sugarcane": "Sugarcane",
    "turmeric": "Turmeric",
    "ginger": "Ginger(Dry)",
    "garlic": "Garlic",
    "brinjal": "Brinjal",
    "cauliflower": "Cauliflower",
    "cabbage": "Cabbage",
}

# State name mapping
STATE_ALIASES = {
    "karnataka": "Karnataka",
    "maharashtra": "Maharashtra",
    "tamil nadu": "Tamil Nadu",
    "andhra pradesh": "Andhra Pradesh",
    "telangana": "Telangana",
    "kerala": "Kerala",
    "gujarat": "Gujarat",
    "rajasthan": "Rajasthan",
    "uttar pradesh": "Uttar Pradesh",
    "punjab": "Punjab",
    "haryana": "Haryana",
    "madhya pradesh": "Madhya Pradesh",
    "bengaluru": "Karnataka",
    "bangalore": "Karnataka",
    "mumbai": "Maharashtra",
    "pune": "Maharashtra",
    "hyderabad": "Telangana",
    "delhi": "Delhi",
    "chennai": "Tamil Nadu",
}


def get_mandi_price(crop: str, market: str = "") -> dict:
    """
    Fetches live mandi (agricultural market) prices for a given crop
    from the data.gov.in Agmarknet API.

    Args:
        crop: The name of the crop (e.g., "tomato", "onion", "wheat", "rice").
        market: Optional. The market/APMC name or city (e.g., "Bengaluru", "Pune", "Delhi").
                If empty, returns prices from all available markets.

    Returns:
        A dictionary with records containing market, min_price, max_price, modal_price
        (all in INR per quintal), and a formatted summary string.
    """
    if not AGMARKNET_API_KEY:
        return {"error": "Agmarknet API key not configured."}

    # Normalize crop name
    crop_lower = crop.lower().strip()
    commodity = COMMODITY_ALIASES.get(crop_lower, crop.capitalize())

    try:
        params = {
            "api-key": AGMARKNET_API_KEY,
            "format": "json",
            "filters[commodity]": commodity,
            "limit": 10,
            "offset": 0,
        }

        # Add state filter if market matches a known state/city
        if market:
            market_lower = market.lower().strip()
            state = STATE_ALIASES.get(market_lower, "")
            if state:
                params["filters[state]"] = state
            else:
                # Try as district/market name
                params["filters[market]"] = market.capitalize()

        response = requests.get(AGMARKNET_BASE_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        records = data.get("records", [])
        if not records:
            return {
                "crop": crop,
                "market": market or "All India",
                "records": [],
                "summary": (
                    f"No price data found for '{commodity}' in '{market or 'All India'}' today. "
                    f"Prices may not have been reported yet. Try a different market or check tomorrow."
                ),
            }

        # Format results
        formatted = []
        for r in records[:5]:  # Top 5 results
            formatted.append({
                "state": r.get("state", "N/A"),
                "district": r.get("district", "N/A"),
                "market": r.get("market", "N/A"),
                "commodity": r.get("commodity", commodity),
                "variety": r.get("variety", "N/A"),
                "arrival_date": r.get("arrival_date", "N/A"),
                "min_price_per_quintal": r.get("min_price", "N/A"),
                "max_price_per_quintal": r.get("max_price", "N/A"),
                "modal_price_per_quintal": r.get("modal_price", "N/A"),
            })

        # Build summary string
        if formatted:
            sample = formatted[0]
            modal = sample["modal_price_per_quintal"]
            summary = (
                f"Today's {commodity} price at {sample['market']}, {sample['district']}: "
                f"₹{modal} per quintal (modal price). "
                f"Range: ₹{sample['min_price_per_quintal']} – ₹{sample['max_price_per_quintal']} per quintal. "
                f"Data as of {sample['arrival_date']}."
            )
        else:
            summary = f"Price data retrieved for {commodity}."

        return {
            "crop": commodity,
            "market_filter": market or "All India",
            "records": formatted,
            "total_found": data.get("total", len(records)),
            "summary": summary,
            "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    except requests.exceptions.HTTPError as e:
        return {"error": f"Agmarknet API HTTP error: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to fetch mandi prices: {str(e)}"}


def get_price_trend(crop: str, market: str = "") -> str:
    """
    Provides a brief market trend analysis for a crop based on current prices
    and general seasonal knowledge.

    Args:
        crop: The name of the crop (e.g., "tomato", "onion").
        market: Optional market or city name for localized context.

    Returns:
        A natural language string describing the price trend and selling advice.
    """
    price_data = get_mandi_price(crop, market)

    if "error" in price_data:
        return f"Could not fetch trend data: {price_data['error']}"

    records = price_data.get("records", [])
    if not records:
        return price_data.get("summary", f"No price data available for {crop}.")

    # Collect modal prices for trend analysis
    prices = []
    for r in records:
        try:
            prices.append(float(r["modal_price_per_quintal"]))
        except (ValueError, TypeError):
            pass

    if not prices:
        return price_data["summary"]

    avg_price = sum(prices) / len(prices)
    max_price = max(prices)
    min_price = min(prices)

    # Simple heuristic trend advice
    if max_price > avg_price * 1.2:
        trend = "prices are variable across markets — higher prices available in select mandis."
        advice = f"Consider transporting to {records[prices.index(max_price)]['market']} for better returns."
    elif avg_price > 2000:
        trend = "prices are currently high."
        advice = "This is a good time to sell if you have surplus stock."
    elif avg_price < 500:
        trend = "prices are currently low."
        advice = "Consider storage (if you have cold storage access) and wait for prices to recover, or explore direct-to-consumer channels."
    else:
        trend = "prices are at moderate levels."
        advice = "Monitor daily prices before selling. Check nearby mandis for better rates."

    return (
        f"Market analysis for {crop.capitalize()} ({market or 'All India'}): {trend} "
        f"Average modal price: ₹{avg_price:.0f}/quintal. "
        f"Range today: ₹{min_price:.0f} – ₹{max_price:.0f}/quintal. "
        f"{advice}"
    )
