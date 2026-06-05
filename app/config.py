from pathlib import Path
import os

APP_DIR = Path("/opt/weather-display/app")
STATE_DIR = Path("/var/lib/weather-display")
LOG_DIR = Path("/var/log/weather-display")

LOCATION_FILE = STATE_DIR / "location.json"
LAST_WEATHER_FILE = STATE_DIR / "last_weather.json"
LAST_RENDER_FILE = STATE_DIR / "last_render.png"

ICON_DIR = APP_DIR / "icons"

WIDTH = 250
HEIGHT = 122

WAVESHARE_DRIVER = os.getenv("WAVESHARE_DRIVER", "V4").strip().upper()
DISPLAY_ROTATE = os.getenv("DISPLAY_ROTATE", "0").strip()

WEATHER_LAT = os.getenv("WEATHER_LAT", "").strip()
WEATHER_LON = os.getenv("WEATHER_LON", "").strip()
WEATHER_CITY = os.getenv("WEATHER_CITY", "").strip()

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
IP_LOCATION_URL = "http://ip-api.com/json/"
