#!/usr/bin/env python3
import logging
import re
import socket
import subprocess

from PIL import Image, ImageDraw, ImageFont

from config import LOG_DIR, STATE_DIR, WIDTH, HEIGHT, WAVESHARE_DRIVER
from display import display_image

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TEST_RENDER_FILE = STATE_DIR / "firstboot_test.png"


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


FONT_TITLE = load_font(FONT_BOLD_PATH, 18)
FONT_TEXT = load_font(FONT_PATH, 13)
FONT_SMALL = load_font(FONT_PATH, 11)


def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=LOG_DIR / "firstboot-display-test.log",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )


def run_command(args):
    try:
        result = subprocess.run(
            args,
            check=False,
            capture_output=True,
            text=True,
            timeout=4,
        )
    except Exception:
        return ""

    return result.stdout.strip()


def wifi_status():
    ssid = run_command(["nmcli", "-t", "-f", "ACTIVE,SSID", "dev", "wifi"])
    ssid = next(
        (
            line.split(":", 1)[1]
            for line in ssid.splitlines()
            if line.startswith("yes:")
        ),
        "",
    )
    wlan = run_command(["ip", "-4", "-o", "addr", "show", "wlan0"])
    match = re.search(r"\binet\s+(\d+\.\d+\.\d+\.\d+)/", wlan)

    ip = match.group(1) if match else ""
    connected = bool(ssid or ip)

    try:
        hostname = socket.gethostname()
    except Exception:
        hostname = "weather-display"

    if connected:
        return {
            "connected": True,
            "ssid": ssid or "connected",
            "ip": ip or "IP pending",
            "hostname": hostname,
        }

    return {
        "connected": False,
        "ssid": "not connected",
        "ip": "no IP address",
        "hostname": hostname,
    }


def draw_checker(draw, x, y, size, cells):
    cell = size // cells
    for row in range(cells):
        for col in range(cells):
            if (row + col) % 2 == 0:
                x0 = x + col * cell
                y0 = y + row * cell
                draw.rectangle((x0, y0, x0 + cell - 1, y0 + cell - 1), fill=0)
    draw.rectangle((x, y, x + size - 1, y + size - 1), outline=0)


def render_test(status):
    image = Image.new("1", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), outline=0)
    draw.rectangle((0, 0, WIDTH - 1, 24), fill=0)
    draw.text((8, 3), "Screen test", font=FONT_TITLE, fill=255)

    draw_checker(draw, 8, 34, 42, 6)
    draw.rectangle((58, 34, 86, 62), fill=0)
    draw.rectangle((58, 70, 86, 98), outline=0)
    draw.line((8, 110, 86, 110), fill=0, width=3)

    wifi_label = "WiFi: OK" if status["connected"] else "WiFi: NO"
    draw.text((100, 34), wifi_label, font=FONT_TITLE, fill=0)
    draw.text((100, 58), f'SSID: {status["ssid"][:18]}', font=FONT_TEXT, fill=0)
    draw.text((100, 78), f'IP: {status["ip"][:20]}', font=FONT_TEXT, fill=0)
    draw.text((100, 100), f'Driver: {WAVESHARE_DRIVER}', font=FONT_SMALL, fill=0)

    return image


def main():
    setup_logging()
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    status = wifi_status()
    image = render_test(status)
    image.save(TEST_RENDER_FILE)

    logging.info("First boot display test status: %s", status)
    display_image(image)
    logging.info("First boot display test shown")


if __name__ == "__main__":
    main()
