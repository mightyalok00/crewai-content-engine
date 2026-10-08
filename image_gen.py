import logging
import os
import random
import re
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
COVERS_DIR = STATIC_DIR / "covers"
COVERS_DIR.mkdir(parents=True, exist_ok=True)

STYLE_PALETTES = {
    "3d_tech": {
        "name": "3D Glassmorphic Indigo",
        "primary_grad": ((99, 102, 241), (6, 182, 212)),  # Indigo to Cyan
        "accent": (56, 189, 248),
        "badge_bg": (30, 41, 59, 230),
        "badge_text": (147, 197, 253),
        "badge_title": "AI & TECHNICAL DEEP DIVE",
        "bg_dark": (10, 13, 20),
    },
    "cyberpunk": {
        "name": "Cyberpunk Neon Matrix",
        "primary_grad": ((236, 72, 153), (6, 182, 212)),  # Pink to Cyan
        "accent": (244, 114, 182),
        "badge_bg": (39, 13, 40, 230),
        "badge_text": (249, 168, 212),
        "badge_title": "CYBER MATRIX SPECIFICATION",
        "bg_dark": (13, 10, 24),
    },
    "emerald": {
        "name": "Quantum Emerald Intelligence",
        "primary_grad": ((16, 185, 129), (14, 165, 233)),  # Emerald to Sky
        "accent": (52, 211, 153),
        "badge_bg": (6, 44, 33, 230),
        "badge_text": (110, 231, 183),
        "badge_title": "QUANTUM INTELLIGENCE BRIEF",
        "bg_dark": (8, 20, 18),
    },
    "sunset": {
        "name": "Amber High Velocity",
        "primary_grad": ((245, 158, 11), (239, 68, 68)),  # Amber to Red
        "accent": (251, 191, 36),
        "badge_bg": (45, 26, 10, 230),
        "badge_text": (253, 230, 138),
        "badge_title": "HIGH PERFORMANCE ENGINEERING",
        "bg_dark": (20, 14, 10),
    },
}


def _get_font(size: int, bold: bool = False):
    """Load standard crisp system fonts or default font."""
    font_paths = [
        "C:\\Windows\\Fonts\\segoeuib.ttf" if bold else "C:\\Windows\\Fonts\\segoeui.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\tahomabd.ttf" if bold else "C:\\Windows\\Fonts\\tahoma.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except (OSError, ValueError) as err:
                logger.debug("Failed loading font %s: %s", path, err)
    return ImageFont.load_default()


def generate_glassmorphic_cover(
    topic: str,
    channel: str = "@krishnaik06",
    style_key: str = "3d_tech",
    width: int = 1200,
    height: int = 630,
) -> dict:
    """Render a sleek, high-resolution 1200x630 glassmorphic banner graphic."""
    palette = STYLE_PALETTES.get(style_key, STYLE_PALETTES["3d_tech"])
    c1, c2 = palette["primary_grad"]
    accent_color = palette["accent"]
    bg_color = palette["bg_dark"]

    # 1. Base Canvas
    img = Image.new("RGBA", (width, height), bg_color + (255,))
    draw = ImageDraw.Draw(img)

    # 2. Tech Grid Pattern
    grid_spacing = 40
    grid_color = (255, 255, 255, 10)
    for x in range(0, width, grid_spacing):
        draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
    for y in range(0, height, grid_spacing):
        draw.line([(0, y), (width, y)], fill=grid_color, width=1)

    # 3. Ambient Glow Orbs
    glow_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_overlay)

    # Top-Right Glow
    for r in range(320, 0, -8):
        alpha = int(50 * (1 - r / 320))
        glow_draw.ellipse(
            [(width - 120 - r, -80 - r), (width - 120 + r, -80 + r)],
            fill=c2 + (alpha,),
        )

    # Bottom-Left Glow
    for r in range(380, 0, -10):
        alpha = int(60 * (1 - r / 380))
        glow_draw.ellipse(
            [(-80 - r, height - 80 - r), (-80 + r, height - 80 + r)],
            fill=c1 + (alpha,),
        )

    # Center-Right Ambient Orb
    for r in range(220, 0, -6):
        alpha = int(40 * (1 - r / 220))
        glow_draw.ellipse(
            [(width - 280 - r, height // 2 - r), (width - 280 + r, height // 2 + r)],
            fill=c1 + (alpha,),
        )

    img = Image.alpha_composite(img, glow_overlay)
    draw = ImageDraw.Draw(img)

    # 4. Right-Side 3D Futuristic Glassmorphism Terminal Card
    card_overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    card_draw = ImageDraw.Draw(card_overlay)

    # Outer Glass Panel
    bg_card_coords = [(width - 440, 95), (width - 70, 535)]
    card_draw.rounded_rectangle(bg_card_coords, radius=24, fill=(18, 24, 38, 220), outline=c2 + (90,), width=2)

    # Card Header / Window Controls
    card_draw.ellipse([(width - 415, 125), (width - 403, 137)], fill=(239, 68, 68, 220))
    card_draw.ellipse([(width - 395, 125), (width - 383, 137)], fill=(245, 158, 11, 220))
    card_draw.ellipse([(width - 375, 125), (width - 363, 137)], fill=(16, 185, 129, 220))

    card_draw.line([(width - 440, 155), (width - 70, 155)], fill=(255, 255, 255, 25), width=1)

    # Decorative Code and Architectural Lines
    random.seed(42)
    for i in range(8):
        y_pos = 185 + i * 38
        line_len = random.randint(140, 310) if i != 2 else 320
        col = c1 if i % 2 == 0 else c2
        card_draw.rounded_rectangle(
            [(width - 415, y_pos), (width - 415 + line_len, y_pos + 14)],
            radius=6,
            fill=col + (140 if i in (0, 2, 4) else 75,),
        )

    # Floating Pulse Node
    card_draw.ellipse(
        [(width - 120, 115), (width - 92, 143)],
        fill=accent_color + (230,),
        outline=(255, 255, 255, 200),
        width=2,
    )

    img = Image.alpha_composite(img, card_overlay)
    draw = ImageDraw.Draw(img)

    # 5. Left Side Typography & Branding
    font_badge = _get_font(15, bold=True)
    font_title = _get_font(44, bold=True)
    font_sub = _get_font(21, bold=False)
    font_meta = _get_font(15, bold=False)

    margin_left = 75
    current_y = 90

    # Badge Pill
    badge_title = f"[ {palette['badge_title']} ]"
    badge_w = len(badge_title) * 10 + 30
    badge_h = 32
    draw.rounded_rectangle(
        [(margin_left, current_y), (margin_left + badge_w, current_y + badge_h)],
        radius=8,
        fill=palette["badge_bg"],
        outline=c1 + (180,),
        width=1,
    )
    draw.text((margin_left + 14, current_y + 7), badge_title, font=font_badge, fill=palette["badge_text"])

    current_y += 60

    # Auto-wrapped Title (Up to 3 lines) - Clean YouTube URLs if passed directly
    clean_topic = topic.strip()
    if clean_topic.startswith(("http://", "https://", "youtu.be", "www.youtube")) or "youtube.com" in clean_topic:
        try:
            from tools import extract_video_id, get_video_oembed_info
            vid = extract_video_id(clean_topic)
            if vid:
                vinfo = get_video_oembed_info(vid)
                if vinfo.get("title"):
                    clean_topic = vinfo["title"]
                    if not channel or channel == "@krishnaik06":
                        channel = vinfo.get("author_name", channel)
        except (ValueError, KeyError, TypeError, OSError) as err:
            logger.debug("Could not resolve video title for topic: %s", err)
            clean_topic = "YouTube Video Analysis"

    words = clean_topic.split()
    lines = []
    current_line = []

    for word in words:
        test_line = " ".join(current_line + [word])
        if len(test_line) > 24 and current_line:
            lines.append(" ".join(current_line))
            current_line = [word]
        else:
            current_line.append(word)
    if current_line:
        lines.append(" ".join(current_line))

    for line in lines[:3]:
        draw.text((margin_left, current_y), line, font=font_title, fill=(255, 255, 255))
        current_y += 56

    current_y += 18

    # Channel / Subtitle
    channel_clean = channel.strip() if channel else "@krishnaik06"
    if channel_clean.startswith(("http://", "https://", "youtu.be", "www.youtube")) or "youtube.com" in channel_clean:
        try:
            from tools import extract_video_id, get_video_oembed_info
            vid = extract_video_id(channel_clean)
            if vid:
                vinfo = get_video_oembed_info(vid)
                if vinfo.get("author_name"):
                    channel_clean = vinfo["author_name"]
        except (ValueError, KeyError, TypeError, OSError) as err:
            logger.debug("Could not resolve creator for channel: %s", err)
            channel_clean = "YouTube Creator"

    sub_text = f"Insights & Architecture from {channel_clean}"
    draw.text((margin_left, current_y), sub_text, font=font_sub, fill=accent_color)

    # Footer Divider & Branding
    footer_y = height - 70
    draw.line([(margin_left, footer_y), (margin_left + 580, footer_y)], fill=(255, 255, 255, 30), width=1)

    footer_text = "CrewAI Multi-Agent Studio Engine • Google AI Studio Edition"
    draw.text((margin_left, footer_y + 14), footer_text, font=font_meta, fill=(148, 163, 184))

    # Save outputs
    final_img = img.convert("RGB")
    slug = re.sub(r"[^\w]+", "-", clean_topic.lower())[:30].strip("-") or "cover"
    timestamp = int(time.time())
    file_name = f"cover-{slug}-{timestamp}.jpg"
    local_path = COVERS_DIR / file_name

    final_img.save(local_path, format="JPEG", quality=95)

    latest_path = STATIC_DIR / "latest_cover.jpg"
    final_img.save(latest_path, format="JPEG", quality=95)

    rel_url = f"/static/covers/{file_name}"
    return {
        "success": True,
        "image_url": rel_url,
        "local_path": str(local_path),
        "topic": topic,
        "channel": channel,
        "style_name": palette["name"],
        "style_key": style_key,
        "width": width,
        "height": height,
    }


def generate_cover_banner(
    topic: str,
    channel: str = "@krishnaik06",
    style_key: str = "3d_tech",
    custom_details: str = "",
    width: int = 1200,
    height: int = 630,
) -> dict:
    """Generate professional AI cover banner artwork."""
    return generate_glassmorphic_cover(
        topic=topic,
        channel=channel,
        style_key=style_key,
        width=width,
        height=height,
    )


if __name__ == "__main__":
    res = generate_cover_banner("AI vs ML vs Data Science", channel="@krishnaik06", style_key="3d_tech")
    print("Cover generated:", res)
