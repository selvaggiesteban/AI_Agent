#!/usr/bin/env python3
"""
High-quality final assets generator with global 1.3em line-height.
Supports multiple brands and relative paths for portability.
"""
import sys
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

# Ad Studio ecosystem imports
from config import OUTPUT_DIR, FONTS_DIR, ASSETS_DIR, BRAND_MANUALS_DIR
from brand.loader import cargar_brand_manual
from generators.image_generator import generar_con_pollinations

# === DEFAULT COLOR CONFIGURATION ===
C_OSCURO = (29, 20, 18)
C_CLARO = (246, 230, 212)
C_DORADO = (197, 165, 90)
C_DORADO_SUAVE = (170, 145, 80)

# === GLOBAL RULE: line-height 1.3em ===
LINE_HEIGHT = 1.3

def lh(font_size):
    """Calculates line-height in pixels: font_size * 1.3"""
    return int(font_size * LINE_HEIGHT)

def load_logo(brand_id, name, desired_width):
    """Load logo from the client's assets folder."""
    path = ASSETS_DIR / f"{brand_id}_{name}" if name == "logo_blanco.png" else ASSETS_DIR / name
    if not path.exists():
        path = ASSETS_DIR / brand_id / name
    if not path.exists():
        return None
    img = Image.open(path).convert("RGBA")
    ratio = desired_width / img.width
    return img.resize((desired_width, int(img.height * ratio)), Image.LANCZOS)

def draw_accent(draw, x_u_center, y_top, font_size, color):
    length = int(font_size * 0.22)
    thickness = max(2, int(font_size * 0.04))
    draw.line([(x_u_center - length // 2, y_top + int(font_size * 0.15)),
               (x_u_center + length // 2, y_top - int(font_size * 0.05))], fill=color, width=thickness)

def create_final_piece(brand_id, marca):
    W, H = 1080, 1080

    print(f"  [AI] Generating visual background for {marca['nombre']}...")
    prompt_fondo = (
        "Dark elegant abstract background, deep brown and black tones, "
        "soft golden light rays from top left corner, "
        "subtle fabric or curtain texture, "
        "moody atmospheric lighting, volumetric light, "
        "no text no letters no words no logos no people, "
        "dark luxury aesthetic, cinematic lighting, "
        "professional photography style, 4k quality"
    )
    try:
        img_ia = generar_con_pollinations(prompt_fondo, ancho=1080, alto=1080)
        img = img_ia.convert("RGB").resize((W, H), Image.LANCZOS)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.65)
    except Exception as e:
        print(f"  [AI] Failed: {e}")
        img = Image.new("RGB", (W, H), C_OSCURO)

    draw = ImageDraw.Draw(img)
    cx = W // 2

    # Golden frame
    m = 35
    draw.rectangle([m, m, W-m, H-m], outline=C_DORADO_SUAVE, width=1)

    # === REAL LOGO ===
    logo = load_logo(brand_id, "logo_blanco.png", desired_width=500)
    if logo:
        logo_x = cx - logo.width // 2
        logo_y = 90
        img.paste(logo, (logo_x, logo_y), logo)

    # Decorative line
    draw.line([(cx - 100, 225), (cx + 100, 225)], fill=C_DORADO_SUAVE, width=1)

    # === MAIN TEXT ===
    font_size_titulo = 68
    font_size_sub = 40
    try:
        font_titulo = ImageFont.truetype(str(FONTS_DIR / "Trust3A.ttf"), font_size_titulo)
        font_sub = ImageFont.truetype(str(FONTS_DIR / "Trust3A.ttf"), font_size_sub)
    except:
        font_titulo = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    y_cursor = 290

    # Dynamic text based on brand manual
    main_text = marca.get("textos", {}).get("post_final", "Each case is unique. We defend it as such.")

    # Split text into lines to handle line-height
    lines = main_text.split("\n")
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_titulo)
        tw = bbox[2] - bbox[0]
        draw.text((cx - tw//2, y_cursor), line, fill=C_CLARO, font=font_titulo)
        y_cursor += lh(font_size_titulo)

    # Separator
    y_sep = y_cursor + 10
    draw.line([(cx - 60, y_sep), (cx + 60, y_sep)], fill=C_DORADO, width=1)
    y_cursor = y_sep + 20

    # Subtitle
    sub = marca.get("textos", {}).get("post_final_sub", "We defend it as such.")
    bbox = draw.textbbox((0, 0), sub, font=font_sub)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw//2, y_cursor), sub, fill=C_DORADO, font=font_sub)
    y_cursor += lh(font_size_sub)

    # Decorative line
    y_linea_med = y_cursor + 15
    draw.line([(cx - 80, y_linea_med), (cx + 80, y_linea_med)], fill=C_DORADO_SUAVE, width=1)

    # Bottom label
    font_abog = ImageFont.truetype("arial.ttf", 16) if "arial.ttf" else ImageFont.load_default()
    label = marca.get("nombre", "LAWYERS").upper()
    bbox = draw.textbbox((0, 0), label, font=font_abog)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw//2, y_linea_med + 22), label, fill=C_DORADO, font=font_abog)

    # Footer
    y_footer = H - 110
    draw.line([(cx - 120, y_footer), (cx + 120, y_footer)], fill=C_DORADO_SUAVE, width=1)
    font_contacto = ImageFont.load_default()
    website = marca.get("website", "website.com")
    email = marca.get("contacto", {}).get("email", "info@email.com")
    line1 = f"{website}  |  {email}"
    bbox = draw.textbbox((0, 0), line1, font=font_contacto)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw//2, y_footer + 15), line1, fill=C_DORADO_SUAVE, font=font_contacto)

    return img

def main():
    parser = argparse.ArgumentParser(description="Ad Studio final assets generator.")
    parser.add_argument("brand_id", nargs="?", default="gsr_abogados", help="Brand ID")
    args = parser.parse_args()

    try:
        marca = cargar_brand_manual(BRAND_MANUALS_DIR / f"{args.brand_id}.json")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    output_dir = OUTPUT_DIR / args.brand_id
    output_dir.mkdir(parents=True, exist_ok=True)

    print("="*60)
    print(f"  {marca['nombre']} - Instagram Post FINAL")
    print("="*60)

    img = create_final_piece(args.brand_id, marca)
    path = output_dir / f"{args.brand_id}_instagram_post_FINAL.png"
    img.save(path, "PNG", quality=95)
    print(f"\n  Saved: {path}")

if __name__ == "__main__":
    main()
