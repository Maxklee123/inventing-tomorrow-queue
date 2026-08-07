#!/usr/bin/env python3
"""
inventing.tomorrow — Carousel Slide Renderer
================================================
Nimmt ein KI-generiertes Rohbild + Text und baut daraus fertige,
gebrandete Instagram-Carousel-Slides (1080x1350, 4:5 Format).
"""

import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

CANVAS_SIZE = (1080, 1350)

COLORS = {
    "bg_fallback": (10, 14, 20),
    "text_primary": (255, 255, 255),
    "text_secondary": (200, 210, 225),
    "accent": (0, 200, 255),
    "overlay_dark": (5, 8, 14),
    "pill_bg": (0, 200, 255),
    "pill_text": (5, 8, 14),
}

FONT_DIR = Path("/usr/share/fonts/truetype/google-fonts")
FONTS = {
    "black": FONT_DIR / "Poppins-Bold.ttf",
    "bold": FONT_DIR / "Poppins-Bold.ttf",
    "medium": FONT_DIR / "Poppins-Medium.ttf",
    "regular": FONT_DIR / "Poppins-Regular.ttf",
}

HANDLE = "@inventing.tomorrow"
MARGIN = 72


def load_font(weight, size):
    return ImageFont.truetype(str(FONTS[weight]), size)


def prepare_background(image_path):
    canvas = Image.new("RGB", CANVAS_SIZE, COLORS["bg_fallback"])
    if image_path and Path(image_path).exists():
        img = Image.open(image_path).convert("RGB")
        target_ratio = CANVAS_SIZE[0] / CANVAS_SIZE[1]
        w, h = img.size
        current_ratio = w / h
        if current_ratio > target_ratio:
            new_w = int(h * target_ratio)
            left = (w - new_w) // 2
            img = img.crop((left, 0, left + new_w, h))
        else:
            new_h = int(w / target_ratio)
            top = (h - new_h) // 2
            img = img.crop((0, top, w, top + new_h))
        img = img.resize(CANVAS_SIZE, Image.LANCZOS)
        img = ImageEnhance.Brightness(img).enhance(0.75)
        img = ImageEnhance.Contrast(img).enhance(1.05)
        canvas = img
    else:
        draw = ImageDraw.Draw(canvas)
        for y in range(CANVAS_SIZE[1]):
            t = y / CANVAS_SIZE[1]
            draw.line([(0, y), (CANVAS_SIZE[0], y)],
                      fill=(int(10 + t * 15), int(14 + t * 20), int(20 + t * 35)))
    return canvas


def add_gradient_overlay(canvas, position="bottom"):
    overlay = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    h = CANVAS_SIZE[1]
    band = int(h * 0.55)
    if position in ("bottom", "both"):
        for i in range(band):
            alpha = int(220 * (i / band) ** 1.4)
            draw.line([(0, h - band + i), (CANVAS_SIZE[0], h - band + i)],
                      fill=(*COLORS["overlay_dark"], alpha))
    if position in ("top", "both"):
        top_band = int(h * 0.28)
        for i in range(top_band):
            alpha = int(200 * (1 - i / top_band) ** 1.4)
            draw.line([(0, i), (CANVAS_SIZE[0], i)], fill=(*COLORS["overlay_dark"], alpha))
    return Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")


def wrap_text(text, font, max_width, draw):
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_pill(draw, text, x, y, font):
    pad_x, pad_y = 22, 12
    tw = draw.textlength(text, font=font)
    th = font.size
    draw.rounded_rectangle([x, y, x + tw + 2 * pad_x, y + th + 2 * pad_y],
                            radius=(th + 2 * pad_y) // 2, fill=COLORS["pill_bg"])
    draw.text((x + pad_x, y + pad_y - 2), text, font=font, fill=COLORS["pill_text"])


def draw_handle_watermark(draw, font):
    tw = draw.textlength(HANDLE, font=font)
    draw.text((CANVAS_SIZE[0] - MARGIN - tw, CANVAS_SIZE[1] - MARGIN - font.size),
               HANDLE, font=font, fill=COLORS["text_secondary"])


def draw_progress_dots(draw, index, total):
    dot_r, gap = 6, 18
    total_w = total * (2 * dot_r) + (total - 1) * gap
    x = (CANVAS_SIZE[0] - total_w) // 2
    y = MARGIN
    for i in range(total):
        fill = COLORS["accent"] if i == index else (90, 100, 115)
        draw.ellipse([x, y, x + 2 * dot_r, y + 2 * dot_r], fill=fill)
        x += 2 * dot_r + gap


def render_hook_slide(post, slide_count):
    canvas = prepare_background(post.get("image"))
    canvas = add_gradient_overlay(canvas, "both")
    draw = ImageDraw.Draw(canvas)
    draw_progress_dots(draw, 0, slide_count)
    draw_pill(draw, post["rubrik"].upper(), MARGIN, 130, load_font("bold", 30))
    hook_font = load_font("black", 76)
    max_w = CANVAS_SIZE[0] - 2 * MARGIN
    lines = wrap_text(post["hook"], hook_font, max_w, draw)
    line_height = 88
    y = CANVAS_SIZE[1] - MARGIN - 140 - len(lines) * line_height
    for line in lines:
        draw.text((MARGIN, y), line, font=hook_font, fill=COLORS["text_primary"])
        y += line_height
    draw.text((MARGIN, CANVAS_SIZE[1] - MARGIN - 90), "Swipe für die Fakten ->",
               font=load_font("medium", 34), fill=COLORS["accent"])
    draw_handle_watermark(draw, load_font("regular", 28))
    return canvas


def render_fact_slide(post, fact_text, index, slide_count):
    canvas = prepare_background(post.get("image"))
    canvas = add_gradient_overlay(canvas, "bottom")
    draw = ImageDraw.Draw(canvas)
    draw_progress_dots(draw, index, slide_count)
    draw.text((MARGIN, CANVAS_SIZE[1] - MARGIN - 420), f"{index:02d}",
               font=load_font("black", 120), fill=COLORS["accent"])
    fact_font = load_font("bold", 52)
    max_w = CANVAS_SIZE[0] - 2 * MARGIN
    lines = wrap_text(fact_text, fact_font, max_w, draw)
    line_height = 64
    y = CANVAS_SIZE[1] - MARGIN - 300 + (420 - len(lines) * line_height) // 2 - 60
    for line in lines:
        draw.text((MARGIN, y), line, font=fact_font, fill=COLORS["text_primary"])
        y += line_height
    draw_handle_watermark(draw, load_font("regular", 28))
    return canvas


def render_cta_slide(post, slide_count):
    canvas = Image.new("RGB", CANVAS_SIZE, COLORS["overlay_dark"])
    draw = ImageDraw.Draw(canvas)
    draw_progress_dots(draw, slide_count - 1, slide_count)
    title_font = load_font("black", 64)
    lines = wrap_text("Mehr Erfindungen & Zukunftskonzepte?", title_font,
                       CANVAS_SIZE[0] - 2 * MARGIN, draw)
    y = 480
    for line in lines:
        draw.text((MARGIN, y), line, font=title_font, fill=COLORS["text_primary"])
        y += 76
    handle_font = load_font("black", 54)
    tw = draw.textlength(HANDLE, font=handle_font)
    draw.rounded_rectangle([(CANVAS_SIZE[0] - tw) // 2 - 40, y + 60,
                             (CANVAS_SIZE[0] + tw) // 2 + 40, y + 60 + 110],
                            radius=55, outline=COLORS["accent"], width=4)
    draw.text(((CANVAS_SIZE[0] - tw) // 2, y + 90), HANDLE, font=handle_font, fill=COLORS["accent"])
    tip_font = load_font("medium", 32)
    tip = "Folgen für tägliche Fakten aus Technik & Zukunft"
    tw2 = draw.textlength(tip, font=tip_font)
    draw.text(((CANVAS_SIZE[0] - tw2) // 2, y + 220), tip, font=tip_font, fill=COLORS["text_secondary"])
    return canvas


def render_post_return_paths(post, output_root):
    facts = post["facts"]
    slide_count = 1 + len(facts) + 1
    out_dir = output_root / post["id"]
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    hook_slide = render_hook_slide(post, slide_count)
    p = out_dir / "01_hook.png"
    hook_slide.save(p, quality=95)
    paths.append(str(p))
    for i, fact in enumerate(facts, start=1):
        slide = render_fact_slide(post, fact, i, slide_count)
        p = out_dir / f"{i+1:02d}_fact.png"
        slide.save(p, quality=95)
        paths.append(str(p))
    cta_slide = render_cta_slide(post, slide_count)
    p = out_dir / f"{slide_count:02d}_cta.png"
    cta_slide.save(p, quality=95)
    paths.append(str(p))
    return paths


if __name__ == "__main__":
    posts_file = Path(sys.argv[1])
    posts = json.loads(posts_file.read_text(encoding="utf-8"))
    output_root = Path("output")
    output_root.mkdir(exist_ok=True)
    for post in posts:
        render_post_return_paths(post, output_root)
        print(f"✓ {post['id']} gerendert")
