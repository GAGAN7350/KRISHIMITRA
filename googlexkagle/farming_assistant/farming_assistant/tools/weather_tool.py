"""
Weather tool using OpenWeatherMap API.
Provides current weather conditions and irrigation advice for a given city.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5"


def get_current_weather(city: str) -> dict:
    """
    Returns the current weather conditions for a given city using the OpenWeatherMap API.

    Args:
        city: The name of the city or village to get weather for (e.g., "Hubli", "Bengaluru").

    Returns:
        A dictionary with temperature_celsius, humidity_percent, conditions,
        wind_speed_kmh, uv_description, and a summary string.
    """
    if not OPENWEATHER_API_KEY:
        return {"error": "OpenWeatherMap API key not configured."}

    try:
        url = f"{OPENWEATHER_BASE_URL}/weather"
        params = {
            "q": f"{city},IN",
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        conditions = data["weather"][0]["description"].capitalize()
        wind_speed = round(data["wind"]["speed"] * 3.6, 1)  # m/s → km/h

        summary = (
            f"Current weather in {city}: {conditions}. "
            f"Temperature: {temp}°C, Humidity: {humidity}%, Wind: {wind_speed} km/h."
        )

        return {
            "city": city,
            "temperature_celsius": temp,
            "humidity_percent": humidity,
            "conditions": conditions,
            "wind_speed_kmh": wind_speed,
            "summary": summary,
        }

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return {"error": f"City '{city}' not found. Try using a nearby larger city."}
        return {"error": f"Weather API error: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to fetch weather: {str(e)}"}


def get_irrigation_advice(city: str, crop: str) -> str:
    """
    Provides irrigation advice for a specific crop based on current weather in the given city.

    Args:
        city: The city or region where the farm is located.
        crop: The crop being grown (e.g., "tomato", "wheat", "rice").

    Returns:
        A natural language string with irrigation recommendations.
    """
    weather = get_current_weather(city)
    if "error" in weather:
        return f"Could not fetch weather for irrigation advice: {weather['error']}"

    temp = weather["temperature_celsius"]
    humidity = weather["humidity_percent"]
    conditions = weather["conditions"].lower()

    # Determine irrigation need based on weather
    is_rainy = any(w in conditions for w in ["rain", "drizzle", "shower", "thunderstorm"])
    is_hot = temp > 35
    is_dry = humidity < 40

    # Crop-specific water requirements (rough guide)
    water_heavy = ["rice", "sugarcane", "banana"]
    water_moderate = ["tomato", "cotton", "maize", "corn", "chili", "pepper"]
    water_light = ["wheat", "ragi", "jowar", "bajra", "sorghum", "groundnut", "soybean"]

    crop_lower = crop.lower()
    if any(c in crop_lower for c in water_heavy):
        base_need = "high"
    elif any(c in crop_lower for c in water_moderate):
        base_need = "moderate"
    else:
        base_need = "low"

    # Build advice
    if is_rainy:
        advice = (
            f"Rain is currently falling in {city}. Skip irrigation today for your {crop} crop. "
            f"Ensure proper field drainage to avoid waterlogging, especially since {crop} has {base_need} water needs."
        )
    elif is_hot and is_dry:
        advice = (
            f"It's hot ({temp}°C) and dry (humidity: {humidity}%) in {city}. "
            f"Your {crop} crop has {base_need} water needs — irrigate in the early morning (6–8 AM) or evening (5–7 PM) "
            f"to reduce evaporation. Drip irrigation is strongly recommended in these conditions."
        )
    elif is_hot:
        advice = (
            f"Temperature is high ({temp}°C) in {city}. "
            f"Water your {crop} during cooler parts of the day. "
            f"Moisture levels are adequate but monitor soil moisture daily."
        )
    else:
        advice = (
            f"Weather conditions in {city} are moderate ({temp}°C, {humidity}% humidity). "
            f"For {crop} (which has {base_need} water needs), maintain regular irrigation schedule. "
            f"Check soil moisture before irrigating — avoid over-watering."
        )

    return advice


def get_5day_forecast(city: str) -> dict:
    """
    Returns a 5-day weather forecast summary for a given city.

    Args:
        city: The name of the city (e.g., "Hubli", "Pune").

    Returns:
        A dictionary with a list of daily forecasts and an overall summary.
    """
    if not OPENWEATHER_API_KEY:
        return {"error": "OpenWeatherMap API key not configured."}

    try:
        url = f"{OPENWEATHER_BASE_URL}/forecast"
        params = {
            "q": f"{city},IN",
            "appid": OPENWEATHER_API_KEY,
            "units": "metric",
            "cnt": 40,  # 5 days × 8 readings/day
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Aggregate by day
        days = {}
        for entry in data["list"]:
            date = entry["dt_txt"].split(" ")[0]
            if date not in days:
                days[date] = {"temps": [], "conditions": []}
            days[date]["temps"].append(entry["main"]["temp"])
            days[date]["conditions"].append(entry["weather"][0]["description"])

        forecast = []
        for date, info in list(days.items())[:5]:
            avg_temp = round(sum(info["temps"]) / len(info["temps"]), 1)
            main_condition = max(set(info["conditions"]), key=info["conditions"].count).capitalize()
            forecast.append({"date": date, "avg_temp_celsius": avg_temp, "condition": main_condition})

        rain_days = [f["date"] for f in forecast if "rain" in f["condition"].lower()]
        rain_warning = (
            f"Rain expected on: {', '.join(rain_days)}. Plan outdoor activities accordingly."
            if rain_days else "No significant rain expected in the next 5 days."
        )

        return {"city": city, "forecast": forecast, "rain_warning": rain_warning}

    except Exception as e:
        return {"error": f"Failed to fetch forecast: {str(e)}"}
