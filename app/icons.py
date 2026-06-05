#!/usr/bin/env python3
from PIL import Image, ImageDraw

from config import ICON_DIR

ICON_DIR.mkdir(parents=True, exist_ok=True)


def canvas():
    return Image.new("1", (64, 64), 255)


def save(img, name):
    img.save(ICON_DIR / name)


def sun():
    img = canvas()
    d = ImageDraw.Draw(img)
    d.ellipse((20, 20, 44, 44), outline=0, width=2)
    for line in [
        (32, 6, 32, 16),
        (32, 48, 32, 58),
        (6, 32, 16, 32),
        (48, 32, 58, 32),
        (12, 12, 18, 18),
        (46, 46, 52, 52),
        (46, 18, 52, 12),
        (12, 52, 18, 46),
    ]:
        d.line(line, fill=0, width=2)
    return img


def cloud():
    img = canvas()
    d = ImageDraw.Draw(img)
    d.ellipse((10, 24, 30, 46), outline=0, width=2)
    d.ellipse((24, 14, 48, 40), outline=0, width=2)
    d.ellipse((42, 24, 60, 46), outline=0, width=2)
    d.rounded_rectangle((16, 32, 54, 48), radius=7, outline=0, width=2)
    return img


def partly_cloudy():
    img = canvas()
    d = ImageDraw.Draw(img)

    d.arc((10, 10, 34, 34), start=0, end=360, fill=0, width=2)
    d.line((22, 2, 22, 10), fill=0, width=2)
    d.line((22, 34, 22, 42), fill=0, width=2)
    d.line((2, 22, 10, 22), fill=0, width=2)
    d.line((34, 22, 42, 22), fill=0, width=2)

    d.ellipse((18, 28, 36, 46), outline=0, width=2)
    d.ellipse((30, 20, 50, 42), outline=0, width=2)
    d.ellipse((44, 28, 60, 46), outline=0, width=2)
    d.rounded_rectangle((22, 34, 56, 48), radius=7, outline=0, width=2)

    return img


def rain():
    img = cloud()
    d = ImageDraw.Draw(img)
    d.line((22, 50, 18, 58), fill=0, width=2)
    d.line((34, 50, 30, 58), fill=0, width=2)
    d.line((46, 50, 42, 58), fill=0, width=2)
    return img


def storm():
    img = cloud()
    d = ImageDraw.Draw(img)
    d.line((34, 48, 28, 56), fill=0, width=2)
    d.line((28, 56, 36, 56), fill=0, width=2)
    d.line((36, 56, 30, 62), fill=0, width=2)
    return img


def snow():
    img = canvas()
    d = ImageDraw.Draw(img)
    d.line((32, 12, 32, 52), fill=0, width=2)
    d.line((12, 32, 52, 32), fill=0, width=2)
    d.line((18, 18, 46, 46), fill=0, width=2)
    d.line((46, 18, 18, 46), fill=0, width=2)
    return img


def mist():
    img = canvas()
    d = ImageDraw.Draw(img)
    d.arc((8, 14, 56, 24), start=0, end=180, fill=0, width=2)
    d.arc((4, 26, 48, 36), start=0, end=180, fill=0, width=2)
    d.arc((10, 38, 58, 48), start=0, end=180, fill=0, width=2)
    return img


def default():
    img = canvas()
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((12, 12, 52, 52), radius=8, outline=0, width=2)
    d.text((25, 22), "?", fill=0)
    return img


def main():
    save(sun(), "sun.png")
    save(cloud(), "cloud.png")
    save(partly_cloudy(), "partly_cloudy.png")
    save(rain(), "rain.png")
    save(storm(), "storm.png")
    save(snow(), "snow.png")
    save(mist(), "mist.png")
    save(default(), "default.png")


if __name__ == "__main__":
    main()
