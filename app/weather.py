from datetime import datetime, timezone, timedelta

from config import OPEN_METEO_URL
from location import load_location
from net import get_json


def weather_code_to_text(code):
    return {
        0: "Clear",
        1: "Mainly Clear",
        2: "Partly Cloudy",
        3: "Cloudy",
        45: "Fog",
        48: "Fog",
        51: "Drizzle",
        53: "Drizzle",
        55: "Drizzle",
        61: "Rain",
        63: "Rain",
        65: "Rain",
        71: "Snow",
        73: "Snow",
        75: "Snow",
        80: "Rain",
        81: "Rain",
        82: "Rain",
        95: "Storm",
        96: "Storm",
        99: "Storm",
    }.get(code, "Unknown")


def fetch_weather():
    loc = load_location()

    params = {
        "latitude": loc["lat"],
        "longitude": loc["lon"],
        "current_weather": "true",
        "daily": "temperature_2m_max,temperature_2m_min",
        "timezone": "auto",
    }

    raw = get_json(OPEN_METEO_URL, params=params, timeout=15)

    current = raw["current_weather"]
    daily = raw["daily"]
    offset = timezone(timedelta(seconds=int(raw.get("utc_offset_seconds", 0))))
    updated_at = datetime.now(timezone.utc).astimezone(offset).strftime("%H:%M")

    return {
        "temp": round(current["temperature"]),
        "condition": weather_code_to_text(current["weathercode"]),
        "high": round(daily["temperature_2m_max"][0]),
        "low": round(daily["temperature_2m_min"][0]),
        "rain": 0,
        "wind": round(current["windspeed"]),
        "city": loc["city"],
        "updated_at": updated_at,
    }
