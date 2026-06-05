#!/usr/bin/env python3
import logging

from config import LOG_DIR
from location import manual_location_configured, update_boot_location


def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_DIR / "location.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def main():
    setup_logging()

    if manual_location_configured():
        logging.info("Manual location configured; skipping IP geolocation.")

    location = update_boot_location()
    logging.info("Boot location updated: %s", location)


if __name__ == "__main__":
    main()
