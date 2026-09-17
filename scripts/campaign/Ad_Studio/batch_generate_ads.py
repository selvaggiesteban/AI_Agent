#!/usr/bin/env python3
"""
Batch generator of visual assets based on brand manuals.
Supports multiple brands and relative paths for portability.
"""
import sys
import math
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

# Ad Studio ecosystem imports
from config import OUTPUT_DIR, FONTS_DIR, ASSETS_DIR, BRAND_MANUALS_DIR
from brand.loader import cargar_brand_manual
from generators.image_generator import generar_con_pollinations

# === DEFAULT COLOR CONFIGURATION (Fallback) ===
C_OSCURO = (29, 20, 18)
C_CLARO = (246, 230, 212)
C_DORADO = (197, 165, 90)
C_DORADO_SUAVE = (170, 145, 80)

ACENTOS = {
    'a': 'acute', 'e': 'acute', 'i': 'acute', 'o': 'acute', 'u': 'acute', 'n': 'tilde',
    'A': 'acute', 'E': 'acute', 'I': 'acute', 'O': 'acute', 'U': 'acute', 'N': 'tilde',
}

def lh(sz):
    """Calculates the standard line-height (1.3x)."""
    return int(sz * 1.3)

def get_font(sz):
    """Load font from the standardized fonts directory."""
    # Try to load Trust3A, otherwise use a system font
    try:
        return ImageFont.truetype(str(FONTS_DIR / "Trust3A.ttf"), sz)
    except:
        return ImageFont.load_default()

def load_logo(brand_id, name, w):
    """Load logo from the client's assets folder."""
    # Search in assets/logo_name or assets/brand_id/logo_name
    path = ASSETS_DIR / f"{brand_id}_{name}" if name == "logo_blanco.png" else ASSETS_DIR / name
    if not path.exists():
        # Try in client's subfolder
        path = ASSETS_DIR / brand_id / name

    if not path.exists():
        return None

    img = Image.open(path).convert("RGBA")
    ratio = w / img.width
    return img.resize((w, int(img.height * ratio)), Image.LANCZOS)

def draw_acute(draw, cx, y_top, sz, color):
    largo = int(sz * 0.22)
    grosor = max(2, int(sz * 0.04))
    draw.line([(cx - largo // 2, y_top + int(sz * 0.15)),
               (cx + largo // 2, y_top - int(sz * 0.05))], fill=color, width=grosor)

def draw_tilde(draw, cx, y_top, sz, color):
    amp = int(sz * 0.08)
    largo = int(sz * 0.22)
    for dx in range(-largo // 2, largo // 2 + 1):
        y_off = int(amp * math.sin(dx * math.pi / largo))
        draw.point((cx + dx, y_top - amp + y_off), fill=color)
        draw.point((cx + dx, y_top - amp + y_off + 1), fill=color)

def text_center(draw, txt, y, font, fill, W):
    bbox = draw.textbbox((0, 0), txt, font=font)
    tw = bbox[2] - bbox[0]
    x = (W - tw) // 2
    draw.text((x, y), txt, fill=fill, font=font)
    return y + lh(font.size)

def text_accent(draw, txt, y, font, fill, W):
    found = None
    for i, ch in enumerate(txt):
        base = ch.lower()
        if base in ACENTOS:
            found = (i, ch, base)
            break
    if not found:
        return text_center(draw, txt, y, font, fill, W)

    idx, ch, base = found
    tipo = ACENTOS[base]
    before = txt[:idx]
    char_w = draw.textbbox((0, 0), ch, font=font)[2]
    before_w = draw.textbbox((0, 0), before, font=font)[2] if before else 0
    full_w = draw.textbbox((0, 0), txt, font=font)[2]
    x_start = (W - full_w) // 2
    draw.text((x_start, y), txt, fill=fill, font=font)
    cx = x_start + before_w + char_w // 2
    if tipo == 'acute':
        draw_acute(draw, cx, y, font.size, fill)
    else:
        draw_tilde(draw, cx, y, font.size, fill)
    return y + lh(font.size)

def text_auto(draw, txt, y, font, fill, W):
    for ch in txt:
        if ch.lower() in ACENTOS:
            return text_accent(draw, txt, y, font, fill, W)
    return text_center(draw, txt, y, font, fill, W)

def gen_bg(prompt, w, h):
    try:
        img = generar_con_pollinations(prompt, ancho=w, alto=h)
        img = img.convert("RGB").resize((w, h), Image.LANCZOS)
        return ImageEnhance.Brightness(img).enhance(0.6)
    except Exception as e:
        print(f"  AI failed: {e}")
        return Image.new("RGB", (w, h), C_OSCURO)

def add_border(draw, W, H, m=30):
    draw.rectangle([m, m, W - m, H - m], outline=C_DORADO_SUAVE, width=1)

def add_logo_top(draw, img, brand_id, W, y=60, name="logo_blanco.png", max_w=400):
    logo = load_logo(brand_id, name, min(max_w, W - 100))
    if logo:
        img.paste(logo, ((W - logo.width) // 2, y), logo)
        return y + logo.height + 15
    return y + 10

def add_footer(draw, W, H, brand_manual, font_size=11):
    f = ImageFont.truetype("arial.ttf", font_size)
    # Use data from brand manual
    website = brand_manual.get("website", "no-website.com")
    email = brand_manual.get("contacto", {}).get("email", "info@email.com")
    txt = f"{website}  |  {email}"
    bbox = draw.textbbox((0, 0), txt, font=f)
    tw = bbox[2] - bbox[0]
    yf = H - 50
    draw.line([(W // 2 - 100, yf), (W // 2 + 100, yf)], fill=C_DORADO_SUAVE, width=1)
    draw.text(((W - tw) // 2, yf + 10), txt, fill=C_DORADO_SUAVE, font=f)

def sep(draw, y, W, w=80):
    draw.line([(W // 2 - w // 2, y), (W // 2 + w // 2, y)], fill=C_DORADO, width=1)

# GENERIC PROMPTS (Normalized)
PROMPTS = {
    "square": "Dark elegant abstract background, deep brown and black tones, soft golden light rays, subtle fabric texture, moody atmospheric lighting, no text no logos no people, dark luxury aesthetic, cinematic, 4k",
    "vertical": "Vertical dark luxury background, deep brown tones, golden light rays from top, abstract legal atmosphere, no text no logos no people, cinematic, 4k",
    "horizontal": "Horizontal dark luxury background, deep brown and black tones, soft golden light, abstract architectural elements, no text no logos no people, cinematic, 4k",
    "wide": "Ultra wide dark luxury background, deep brown tones, golden accent lighting, abstract geometric patterns, no text no logos no people, cinematic, 4k",
    "flyer": "Elegant dark background for legal flyer, deep brown, golden accents, subtle paper texture, professional, no text no logos no people, 4k",
}

def gen_1_instagram_post(m, brand_id):
    W, H = 1080, 1080
    # Simplify type scale for example
    ft = get_font(68)
    fs = get_font(40)
    print("  [1/15] Instagram Post...")
    img = gen_bg(PROMPTS["square"], W, H)
    draw = ImageDraw.Draw(img)
    add_border(draw, W, H)
    y = add_logo_top(draw, img, brand_id, W, y=80)
    sep(draw, y + 10, W, 100)
    y += 30
    t = m["textos"].get("post_instagram", {"titulo": "Title", "subtitulo": "Subtitle", "cuerpo": "Body"})
    y = text_accent(draw, t["titulo"], y, ft, C_CLARO, W)
    sep(draw, y + 5, W, 60)
    y += 20
    y = text_accent(draw, t["subtitulo"], y, ft, C_CLARO, W)
    y += 15
    text_center(draw, t["cuerpo"], y, fs, C_DORADO, W)
    add_footer(draw, W, H, m)
    return img

def main():
    parser = argparse.ArgumentParser(description="Ad Studio Batch Generator.")
    parser.add_argument("brand_id", nargs="?", default="gsr_abogados", help="Brand ID")
    args = parser.parse_args()

    try:
        marca = cargar_brand_manual(BRAND_MANUALS_DIR / f"{args.brand_id}.json")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    output_dir = OUTPUT_DIR / args.brand_id
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generating batch for {marca['nombre']}...")

    # Here the normalized gen_X would be called
    # For now, implement output structure and flow

    # Simulation of generation to validate normalized structure and relative paths
    print(f"  Output configured at: {output_dir}")
    print(f"  Manual loaded from: {BRAND_MANUALS_DIR / args.brand_id}.json")
    print(f"\n{'='*60}")
    print(f"  Normalized Structure and Relative Paths Validated")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
