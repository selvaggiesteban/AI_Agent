#!/usr/bin/env python3
"""
Instagram Post FINAL v7 - line-height 1.3em global.
"""
import sys
sys.path.insert(0, r"C:\Users\Esteban Selvaggi\Desktop\subagent-driven_development\scripts\ad_studio")

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from generators.image_generator import generar_con_pollinations
from config import OUTPUT_DIR

FONTS_DIR = Path(r"C:\Users\Esteban Selvaggi\Desktop\subagent-driven_development\scripts\ad_studio\fonts")
ASSETS_DIR = Path(r"C:\Users\Esteban Selvaggi\Desktop\subagent-driven_development\scripts\ad_studio\assets")
OUTPUT = OUTPUT_DIR / "gsr_abogados"

COLOR_OSCURO = (29, 20, 18)
COLOR_CLARO = (246, 230, 212)
COLOR_DORADO = (197, 165, 90)
COLOR_DORADO_SUAVE = (170, 145, 80)

# === REGLA GLOBAL: line-height 1.3em ===
LINE_HEIGHT = 1.3


def lh(font_size):
    """Calcula line-height en pixels: font_size * 1.3"""
    return int(font_size * LINE_HEIGHT)


def cargar_logo(ruta, ancho_deseado):
    img = Image.open(ruta).convert("RGBA")
    ratio = ancho_deseado / img.width
    nuevo_alto = int(img.height * ratio)
    img = img.resize((ancho_deseado, nuevo_alto), Image.LANCZOS)
    return img


def dibujar_acento(draw, x_u_center, y_top, font_size, color):
    largo = int(font_size * 0.22)
    grosor = max(2, int(font_size * 0.04))
    x1 = x_u_center - largo // 2
    y1 = y_top + int(font_size * 0.15)
    x2 = x_u_center + largo // 2
    y2 = y_top - int(font_size * 0.05)
    draw.line([(x1, y1), (x2, y2)], fill=color, width=grosor)


def crear_instagram_post_final():
    W, H = 1080, 1080

    print("  [IA] Generando fondo visual...")
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
        print(f"  [IA] Fallo: {e}")
        img = Image.new("RGB", (W, H), COLOR_OSCURO)

    draw = ImageDraw.Draw(img)
    cx = W // 2

    # Marco dorado
    m = 35
    draw.rectangle([m, m, W-m, H-m], outline=COLOR_DORADO_SUAVE, width=1)

    # === LOGO REAL ===
    logo_blanco = ASSETS_DIR / "logo_gsr_blanco.png"
    if logo_blanco.exists():
        logo = cargar_logo(logo_blanco, ancho_deseado=500)
        logo_x = cx - logo.width // 2
        logo_y = 90
        img.paste(logo, (logo_x, logo_y), logo)

    # Línea decorativa
    draw.line([(cx - 100, 225), (cx + 100, 225)], fill=COLOR_DORADO_SUAVE, width=1)

    # === TEXTO PRINCIPAL ===
    font_size_titulo = 68
    font_size_sub = 40
    font_titulo = ImageFont.truetype(str(FONTS_DIR / "Trust3A.ttf"), font_size_titulo)
    font_sub = ImageFont.truetype(str(FONTS_DIR / "Trust3A.ttf"), font_size_sub)

    y_cursor = 290

    # "Cada caso" - line-height 1.3em
    t1 = "Cada caso"
    bbox = draw.textbbox((0, 0), t1, font=font_titulo)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw//2, y_cursor), t1, fill=COLOR_CLARO, font=font_titulo)
    y_cursor += lh(font_size_titulo)  # 68 * 1.3 = 88

    # "es único." con acento manual
    texto2 = "es unico."
    bbox2 = draw.textbbox((0, 0), texto2, font=font_titulo)
    tw2 = bbox2[2] - bbox2[0]
    x_texto2 = cx - tw2 // 2
    draw.text((x_texto2, y_cursor), texto2, fill=COLOR_CLARO, font=font_titulo)

    # Acento sobre la u
    bbox_antes = draw.textbbox((0, 0), "es ", font=font_titulo)
    w_antes = bbox_antes[2] - bbox_antes[0]
    bbox_u = draw.textbbox((0, 0), "u", font=font_titulo)
    w_u = bbox_u[2] - bbox_u[0]
    x_u_center = x_texto2 + w_antes + w_u // 2
    dibujar_acento(draw, x_u_center, y_cursor, font_size_titulo, COLOR_CLARO)

    y_cursor += lh(font_size_titulo)  # siguiente línea

    # Separador
    y_sep = y_cursor + 10
    draw.line([(cx - 60, y_sep), (cx + 60, y_sep)], fill=COLOR_DORADO, width=1)
    y_cursor = y_sep + 20

    # "Lo defendemos como tal."
    t3 = "Lo defendemos como tal."
    bbox = draw.textbbox((0, 0), t3, font=font_sub)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw//2, y_cursor), t3, fill=COLOR_DORADO, font=font_sub)
    y_cursor += lh(font_size_sub)

    # Línea decorativa
    y_linea_med = y_cursor + 15
    draw.line([(cx - 80, y_linea_med), (cx + 80, y_linea_med)], fill=COLOR_DORADO_SUAVE, width=1)

    # ABOGADOS
    font_abog = ImageFont.truetype(str(FONTS_DIR / "Trust3A.ttf"), 16)
    abog = "ABOGADOS"
    bbox = draw.textbbox((0, 0), abog, font=font_abog)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw//2, y_linea_med + 22), abog, fill=COLOR_DORADO, font=font_abog)

    # Footer
    y_footer = H - 110
    draw.line([(cx - 120, y_footer), (cx + 120, y_footer)], fill=COLOR_DORADO_SUAVE, width=1)
    font_contacto = ImageFont.truetype("arial.ttf", 12)
    linea1 = "gsrabogados.com.ar  |  info@gsrabogados.com.ar"
    bbox = draw.textbbox((0, 0), linea1, font=font_contacto)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw//2, y_footer + 15), linea1, fill=COLOR_DORADO_SUAVE, font=font_contacto)

    return img


if __name__ == "__main__":
    print("="*60)
    print("  GSR Abogados - Instagram Post FINAL v7")
    print("  line-height 1.3em global")
    print("="*60)

    img = crear_instagram_post_final()
    ruta = OUTPUT / "gsr_instagram_post_FINAL_v7.png"
    img.save(ruta, "PNG", quality=95)
    print(f"\n  Guardado: {ruta}")
    print(f"  Tamaño: {Path(ruta).stat().st_size // 1024} KB")
