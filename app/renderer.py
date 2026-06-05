from PIL import Image, ImageDraw, ImageFont

from config import WIDTH, HEIGHT, ICON_DIR

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


FONT_TEMP = load_font(FONT_BOLD_PATH, 34)
FONT_CITY = load_font(FONT_PATH, 12)
FONT_COND = load_font(FONT_BOLD_PATH, 18)
FONT_SMALL = load_font(FONT_PATH, 12)
FONT_TINY = load_font(FONT_PATH, 10)


def icon_for_condition(condition):
    c = condition.lower()

    if "clear" in c or "sun" in c:
        return "sun.png"
    if "partly" in c:
        return "partly_cloudy.png"
    if "cloud" in c:
        return "cloud.png"
    if "rain" in c or "drizzle" in c:
        return "rain.png"
    if "storm" in c or "thunder" in c:
        return "storm.png"
    if "snow" in c:
        return "snow.png"
    if "mist" in c or "fog" in c or "haze" in c:
        return "mist.png"

    return "default.png"


def draw_right(draw, text, font, right_x, y):
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    draw.text((right_x - width, y), text, font=font, fill=0)


def render_weather(data):
    image = Image.new("1", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), outline=0)

    temp = f'{data["temp"]}°C'
    city = str(data.get("city", "Unknown"))[:14]
    condition = str(data.get("condition", "Unknown"))[:16]
    updated_at = str(data.get("updated_at", "--:--"))[:5]

    draw.text((8, 4), temp, font=FONT_TEMP, fill=0)
    draw.text((8, 48), condition, font=FONT_COND, fill=0)
    draw.text((8, 82), f'H {data["high"]}°   L {data["low"]}°', font=FONT_SMALL, fill=0)
    draw.text((8, 104), f'Rain {data["rain"]}%  Wind {data["wind"]}km/h', font=FONT_TINY, fill=0)
    draw_right(draw, updated_at, FONT_TINY, WIDTH - 8, 104)

    draw_right(draw, city, FONT_CITY, WIDTH - 8, 10)

    icon_path = ICON_DIR / icon_for_condition(condition)

    try:
        icon = Image.open(icon_path).convert("1")
        icon.thumbnail((64, 64))
        image.paste(icon, (180, 32))
    except Exception:
        draw.rectangle((180, 32, 236, 88), outline=0)
        draw.text((202, 52), "?", font=FONT_COND, fill=0)

    return image


def render_status(title, lines):
    image = Image.new("1", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(image)

    draw.rectangle((0, 0, WIDTH - 1, HEIGHT - 1), outline=0)
    draw.rectangle((0, 0, WIDTH - 1, 24), fill=0)
    draw.text((8, 3), title[:22], font=FONT_COND, fill=255)

    y = 36
    for line in lines[:5]:
        draw.text((8, y), str(line)[:32], font=FONT_SMALL, fill=0)
        y += 18

    return image
