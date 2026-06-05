#!/usr/bin/env python3
import json
import logging

from config import STATE_DIR, LOG_DIR, LAST_WEATHER_FILE, LAST_RENDER_FILE
from display import display_image
from location import load_location
from renderer import render_status, render_weather
from weather import fetch_weather


def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_DIR / "weather.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def save_last_weather(data):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    LAST_WEATHER_FILE.write_text(
        json.dumps(data, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )


def main():
    setup_logging()
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    try:
        current = fetch_weather()
    except Exception as exc:
        logging.exception("Weather update failed")
        if LAST_RENDER_FILE.exists():
            logging.info("Keeping last successful render after update failure.")
            return

        try:
            loc = load_location()
            city = loc.get("city", "configured")
        except Exception:
            city = "unknown"

        image = render_status(
            "Weather Pending",
            [
                f"Location: {city}",
                type(exc).__name__[:30],
                str(exc)[:30],
            ],
        )
        image.save(LAST_RENDER_FILE)
        display_image(image)
        return

    image = render_weather(current)
    image.save(LAST_RENDER_FILE)

    display_image(image)
    save_last_weather(current)

    logging.info("Display updated: %s", current)


if __name__ == "__main__":
    main()
