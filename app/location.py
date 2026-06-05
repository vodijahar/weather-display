import json

from config import (
    STATE_DIR,
    LOCATION_FILE,
    WEATHER_LAT,
    WEATHER_LON,
    WEATHER_CITY,
    IP_LOCATION_URL,
)
from net import get_json


def manual_location_configured():
    return bool(WEATHER_LAT and WEATHER_LON)


def manual_location():
    try:
        lat = float(WEATHER_LAT)
        lon = float(WEATHER_LON)
    except ValueError as exc:
        raise RuntimeError("WEATHER_LAT and WEATHER_LON must be numeric.") from exc

    if not -90 <= lat <= 90:
        raise RuntimeError("WEATHER_LAT must be between -90 and 90.")
    if not -180 <= lon <= 180:
        raise RuntimeError("WEATHER_LON must be between -180 and 180.")

    return {
        "lat": lat,
        "lon": lon,
        "city": WEATHER_CITY or "Custom",
        "source": "manual",
    }


def save_json(path, data):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def load_location():
    if manual_location_configured():
        location = manual_location()
        save_json(LOCATION_FILE, location)
        return location

    if not LOCATION_FILE.exists():
        raise RuntimeError("Location file does not exist. Boot location lookup has not run.")

    return json.loads(LOCATION_FILE.read_text(encoding="utf-8"))


def lookup_location():
    if manual_location_configured():
        return manual_location()

    data = get_json(IP_LOCATION_URL, timeout=10)

    if data.get("status") != "success":
        raise RuntimeError(f"IP location lookup failed: {data}")

    return {
        "lat": data["lat"],
        "lon": data["lon"],
        "city": data["city"],
        "source": "ip",
    }


def update_boot_location():
    location = lookup_location()
    save_json(LOCATION_FILE, location)
    return location
