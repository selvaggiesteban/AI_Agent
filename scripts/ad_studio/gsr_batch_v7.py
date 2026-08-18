#!/usr/bin/env python3
import sys, math, json
sys.path.insert(0, r"C:\Users\Esteban Selvaggi\Desktop\subagent-driven_development\scripts\ad_studio")

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from generators.image_generator import generar_con_pollinations
from config import OUTPUT_DIR
from typography import get_type_scale, get_line_height

FONTS_DIR = Path(r"C:\Users\Esteban Selvaggi\Desktop\subagent-driven_development\scripts\ad_studio\fonts")
ASSETS_DIR = Path(r"C:\Users\Esteban Selvaggi\Desktop\subagent-driven_development\scripts\ad_studio\assets")
BRAND_DIR = Path(r"C:\Users\Esteban Selvaggi\Desktop\subagent-driven_development\scripts\ad_studio\brand_manuals")
OUTPUT = OUTPUT_DIR / "gsr_abogados"
OUTPUT.mkdir(parents=True, exist_ok=True)

C_OSCURO = (29, 20, 18)
C_CLARO = (246, 230, 212)
C_DORADO = (197, 165, 90)
C_DORADO_SUAVE = (170, 145, 80)

ACENTOS = {
    'a': 'acute', 'e': 'acute', 'i': 'acute', 'o': 'acute', 'u': 'acute', 'n': 'tilde',
    'A': 'acute', 'E': 'acute', 'I': 'acute', 'O': 'acute', 'U': 'acute', 'N': 'tilde',
}


def lh(sz):
    return get_line_height(sz)


def get_font(sz):
    return ImageFont.truetype(str(FONTS_DIR / "Trust3A.ttf"), sz)


def load_brand():
    with open(BRAND_DIR / "gsr_abogados.json", "r", encoding="utf-8") as f:
        return json.load(f)


def load_logo(name, w):
    p = ASSETS_DIR / name
    if not p.exists():
        return None
    img = Image.open(p).convert("RGBA")
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
        print(f"  IA fallo: {e}")
        return Image.new("RGB", (w, h), C_OSCURO)


def add_border(draw, W, H, m=30):
    draw.rectangle([m, m, W - m, H - m], outline=C_DORADO_SUAVE, width=1)


def add_logo_top(draw, img, W, y=60, name="logo_gsr_blanco.png", max_w=400):
    logo = load_logo(name, min(max_w, W - 100))
    if logo:
        img.paste(logo, ((W - logo.width) // 2, y), logo)
        return y + logo.height + 15
    return y + 10


def add_footer(draw, W, H, font_size=11):
    f = ImageFont.truetype("arial.ttf", font_size)
    txt = "gsrabogados.com.ar  |  info@gsrabogados.com.ar"
    bbox = draw.textbbox((0, 0), txt, font=f)
    tw = bbox[2] - bbox[0]
    yf = H - 50
    draw.line([(W // 2 - 100, yf), (W // 2 + 100, yf)], fill=C_DORADO_SUAVE, width=1)
    draw.text(((W - tw) // 2, yf + 10), txt, fill=C_DORADO_SUAVE, font=f)


def sep(draw, y, W, w=80):
    draw.line([(W // 2 - w // 2, y), (W // 2 + w // 2, y)], fill=C_DORADO, width=1)


PROMPTS = {
    "square": "Dark elegant abstract background, deep brown and black tones, soft golden light rays, subtle fabric texture, moody atmospheric lighting, no text no logos no people, dark luxury aesthetic, cinematic, 4k",
    "vertical": "Vertical dark luxury background, deep brown tones, golden light rays from top, abstract legal atmosphere, no text no logos no people, cinematic, 4k",
    "horizontal": "Horizontal dark luxury background, deep brown and black tones, soft golden light, abstract architectural elements, no text no logos no people, cinematic, 4k",
    "wide": "Ultra wide dark luxury background, deep brown tones, golden accent lighting, abstract geometric patterns, no text no logos no people, cinematic, 4k",
    "flyer": "Elegant dark background for legal flyer, deep brown, golden accents, subtle paper texture, professional, no text no logos no people, 4k",
}


def gen_1_instagram_post(m):
    W, H = 1080, 1080
    sizes = get_type_scale(W, H)
    print("  [1/15] Instagram Post...")
    img = gen_bg(PROMPTS["square"], W, H)
    draw = ImageDraw.Draw(img)
    add_border(draw, W, H)
    y = add_logo_top(draw, img, W, y=80)
    sep(draw, y + 10, W, 100)
    y += 30
    t = m["textos"]["post_instagram"]
    ft = get_font(sizes["title"])
    fs = get_font(sizes["subtitle"])
    y = text_accent(draw, t["titulo"], y, ft, C_CLARO, W)
    sep(draw, y + 5, W, 60)
    y += 20
    y = text_accent(draw, t["subtitulo"], y, ft, C_CLARO, W)
    y += 15
    text_center(draw, t["cuerpo"], y, fs, C_DORADO, W)
    add_footer(draw, W, H)
    return img


def gen_2_instagram_story(m):
    W, H = 1080, 1920
    sizes = get_type_scale(W, H)
    print("  [2/15] Instagram Story...")
    img = gen_bg(PROMPTS["vertical"], W, H)
    draw = ImageDraw.Draw(img)
    add_border(draw, W, H, 40)
    slides = m["textos"]["historia_instagram"]
    ft = get_font(sizes["title"])
    fc = get_font(sizes["body"])
    y = 200
    for i, s in enumerate(slides):
        if i == 0:
            y = add_logo_top(draw, img, W, y=120)
            y += 30
        text_auto(draw, s["titulo"], y, ft, C_CLARO, W)
        y += lh(ft.size)
        y += 10
        text_center(draw, s["cuerpo"], y, fc, C_DORADO, W)
        y += lh(fc.size) + 40
        if i < len(slides) - 1:
            sep(draw, y, W, 60)
            y += 30
    add_footer(draw, W, H)
    return img


def gen_3_instagram_carousel(m):
    W, H = 1080, 1350
    sizes = get_type_scale(W, H)
    print("  [3/15] Instagram Carousel (5 slides)...")
    slides = m["textos"]["carrusel_instagram"]
    imgs = []
    for i, s in enumerate(slides):
        img = gen_bg(PROMPTS["square"], W, H)
        draw = ImageDraw.Draw(img)
        add_border(draw, W, H)
        y = add_logo_top(draw, img, W, y=50)
        ft = get_font(sizes["title"])
        fs = get_font(sizes["subtitle"])
        fc = get_font(sizes["body"])
        y += 40
        text_auto(draw, s["titulo"], y, ft, C_CLARO, W)
        y += lh(ft.size) + 15
        sep(draw, y, W, 60)
        y += 25
        if "subtitulo" in s:
            text_auto(draw, s["subtitulo"], y, fs, C_DORADO, W)
            y += lh(fs.size) + 15
        if "cuerpo" in s:
            text_center(draw, s["cuerpo"], y, fc, C_CLARO, W)
        n_slide = f"0{i + 1}" if i + 1 < 10 else str(i + 1)
        fn = get_font(sizes["detail"])
        draw.text((W - 60, H - 50), f"{n_slide}/05", fill=C_DORADO_SUAVE, font=fn)
        add_footer(draw, W, H)
        imgs.append(img)
    return imgs


def gen_4_youtube_thumbnail(m):
    W, H = 1280, 720
    sizes = get_type_scale(W, H)
    print("  [4/15] YouTube Thumbnail...")
    img = gen_bg(PROMPTS["horizontal"], W, H)
    draw = ImageDraw.Draw(img)
    add_border(draw, W, H, 20)
    t = m["textos"]["thumbnail_youtube"]
    ft = get_font(sizes["title"])
    fs = get_font(sizes["subtitle"])
    y = 180
    text_auto(draw, t["titulo_corto"], y, ft, C_CLARO, W)
    y += lh(ft.size) + 10
    text_center(draw, t["subtitulo"], y, fs, C_DORADO, W)
    logo = load_logo("logo_gsr_blanco.png", 250)
    if logo:
        img.paste(logo, ((W - logo.width) // 2, H - 120), logo)
    add_footer(draw, W, H)
    return img


def gen_5_youtube_banner(m):
    W, H = 2560, 1440
    sizes = get_type_scale(W, H)
    print("  [5/15] YouTube Banner...")
    img = gen_bg(PROMPTS["wide"], W, H)
    draw = ImageDraw.Draw(img)
    add_border(draw, W, H, 40)
    t = m["textos"]["banner_youtube"]
    ft = get_font(sizes["title"])
    fs = get_font(sizes["subtitle"])
    fc = get_font(sizes["body"])
    y = H // 2 - 80
    text_center(draw, t["canal"], y, ft, C_CLARO, W)
    y += lh(ft.size) + 15
    text_center(draw, t["descripcion"], y, fs, C_DORADO, W)
    y += lh(fs.size) + 25
    links = "  |  ".join(t["social_links"])
    text_center(draw, links, y, fc, C_DORADO_SUAVE, W)
    logo = load_logo("logo_gsr_blanco.png", 500)
    if logo:
        img.paste(logo, ((W - logo.width) // 2, 120), logo)
    return img


def gen_6_facebook_post(m):
    W, H = 1200, 630
    sizes = get_type_scale(W, H)
    print("  [6/15] Facebook Post...")
    img = gen_bg(PROMPTS["horizontal"], W, H)
    draw = ImageDraw.Draw(img)
    add_border(draw, W, H, 20)
    y = add_logo_top(draw, img, W, y=30, max_w=300)
    t = m["textos"]["facebook_post"]
    ft = get_font(sizes["title"])
    fc = get_font(sizes["body"])
    y += 15
    text_auto(draw, t["titulo"], y, ft, C_CLARO, W)
    y += lh(ft.size) + 10
    text_center(draw, t["cuerpo"], y, fc, C_DORADO, W)
    add_footer(draw, W, H)
    return img


def gen_7_facebook_ad(m):
    W, H = 1200, 628
    sizes = get_type_scale(W, H)
    print("  [7/15] Facebook Ad...")
    img = gen_bg(PROMPTS["horizontal"], W, H)
    draw = ImageDraw.Draw(img)
    add_border(draw, W, H, 20)
    y = add_logo_top(draw, img, W, y=25, max_w=250)
    t = m["textos"]["facebook_ad"]
    ft = get_font(sizes["title"])
    fs = get_font(sizes["subtitle"])
    y += 15
    text_center(draw, t["headline"], y, ft, C_CLARO, W)
    y += lh(ft.size) + 8
    text_center(draw, t["subheadline"], y, fs, C_DORADO, W)
    add_footer(draw, W, H)
    return img


def gen_8_linkedin_post(m):
    W, H = 1200, 627
    sizes = get_type_scale(W, H)
    print("  [8/15] LinkedIn Post...")
    img = gen_bg(PROMPTS["horizontal"], W, H)
    draw = ImageDraw.Draw(img)
    add_border(draw, W, H, 20)
    y = add_logo_top(draw, img, W, y=25, max_w=250)
    t = m["textos"]["post_linkedin"]
    ft = get_font(sizes["title"])
    fs = get_font(sizes["subtitle"])
    y += 15
    text_auto(draw, t["titulo"], y, ft, C_CLARO, W)
    y += lh(ft.size) + 10
    text_center(draw, t["dato_clave"], y, fs, C_DORADO, W)
    add_footer(draw, W, H)
    return img


def gen_9_linkedin_carousel(m):
    W, H = 1080, 1350
    sizes = get_type_scale(W, H)
    print("  [9/15] LinkedIn Carousel (5 slides)...")
    slides = m["textos"]["carrusel_linkedin"]
    imgs = []
    for i, s in enumerate(slides):
        img = gen_bg(PROMPTS["square"], W, H)
        draw = ImageDraw.Draw(img)
        add_border(draw, W, H)
        y = add_logo_top(draw, img, W, y=50)
        ft = get_font(sizes["title"])
        fs = get_font(sizes["subtitle"])
        fc = get_font(sizes["body"])
        y += 40
        text_auto(draw, s["titulo"], y, ft, C_CLARO, W)
        y += lh(ft.size) + 15
        sep(draw, y, W, 60)
        y += 25
        if "subtitulo" in s:
            text_auto(draw, s["subtitulo"], y, fs, C_DORADO, W)
            y += lh(fs.size) + 15
        if "cuerpo" in s:
            text_center(draw, s["cuerpo"], y, fc, C_CLARO, W)
        fn = get_font(sizes["detail"])
        draw.text((W - 60, H - 50), f"0{i + 1}/05", fill=C_DORADO_SUAVE, font=fn)
        add_footer(draw, W, H)
        imgs.append(img)
    return imgs


def gen_10_google_ads(m):
    W, H = 1200, 628
    sizes = get_type_scale(W, H)
    print("  [10/15] Google Ads...")
    img = gen_bg(PROMPTS["horizontal"], W, H)
    draw = ImageDraw.Draw(img)
    add_border(draw, W, H, 20)
    y = add_logo_top(draw, img, W, y=25, max_w=250)
    t = m["textos"]["google_ads"]
    ft = get_font(sizes["title"])
    fs = get_font(sizes["subtitle"])
    y += 15
    text_center(draw, t["headline"], y, ft, C_CLARO, W)
    y += lh(ft.size) + 10
    text_center(draw, t["descripcion"], y, fs, C_DORADO, W)
    add_footer(draw, W, H)
    return img


def gen_11_twitter(m):
    W, H = 1600, 900
    sizes = get_type_scale(W, H)
    print("  [11/15] Twitter/X Post...")
    img = gen_bg(PROMPTS["horizontal"], W, H)
    draw = ImageDraw.Draw(img)
    add_border(draw, W, H, 25)
    y = add_logo_top(draw, img, W, y=60, max_w=350)
    t = m["textos"]["twitter"]
    ft = get_font(sizes["title"])
    y += 30
    text_center(draw, t["texto"], y, ft, C_CLARO, W)
    add_footer(draw, W, H)
    return img


def gen_12_tiktok_cover(m):
    W, H = 1080, 1920
    sizes = get_type_scale(W, H)
    print("  [12/15] TikTok Cover...")
    img = gen_bg(PROMPTS["vertical"], W, H)
    draw = ImageDraw.Draw(img)
    add_border(draw, W, H, 40)
    t = m["textos"]["tiktok_cover"]
    ft = get_font(sizes["title"])
    fs = get_font(sizes["subtitle"])
    y = H // 2 - 80
    text_auto(draw, t["titulo"], y, ft, C_CLARO, W)
    y += lh(ft.size) + 15
    text_center(draw, t["subtitulo"], y, fs, C_DORADO, W)
    logo = load_logo("logo_gsr_blanco.png", 300)
    if logo:
        img.paste(logo, ((W - logo.width) // 2, y + lh(fs.size) + 40), logo)
    add_footer(draw, W, H)
    return img


def gen_13_pinterest(m):
    W, H = 1000, 1500
    sizes = get_type_scale(W, H)
    print("  [13/15] Pinterest Pin...")
    img = gen_bg(PROMPTS["vertical"], W, H)
    draw = ImageDraw.Draw(img)
    add_border(draw, W, H, 30)
    y = add_logo_top(draw, img, W, y=60, max_w=350)
    t = m["textos"]["pinterest_pin"]
    ft = get_font(sizes["title"])
    fc = get_font(sizes["body"])
    y += 20
    text_auto(draw, t["titulo"], y, ft, C_CLARO, W)
    y += lh(ft.size) + 15
    sep(draw, y, W, 60)
    y += 20
    text_center(draw, t["cuerpo"], y, fc, C_DORADO, W)
    add_footer(draw, W, H)
    return img


def gen_14_flyer(m):
    W, H = 2480, 3508
    sizes = get_type_scale(W, H)
    print("  [14/15] Flyer A4...")
    img = gen_bg(PROMPTS["flyer"], W, H)
    draw = ImageDraw.Draw(img)
    add_border(draw, W, H, 60)
    logo = load_logo("logo_gsr_oscuro.png", 800)
    if logo:
        img.paste(logo, ((W - logo.width) // 2, 120), logo)
        y = 120 + logo.height + 60
    else:
        y = 200
    t = m["textos"]["flyer_a4"]
    ft = get_font(sizes["title"])
    fs = get_font(sizes["subtitle"])
    fc = get_font(sizes["body"])
    fd = get_font(sizes["caption"])
    text_auto(draw, t["titulo"], y, ft, C_OSCURO, W)
    y += lh(ft.size) + 20
    text_center(draw, t["subtitulo"], y, fs, C_DORADO, W)
    y += lh(fs.size) + 40
    sep(draw, y, W, 200)
    y += 50
    text_center(draw, t["cuerpo"], y, fc, C_OSCURO, W)
    y += lh(fc.size) * 3 + 40
    for d in t["detalles"]:
        text_center(draw, d, y, fd, C_OSCURO, W)
        y += lh(fd.size) + 10
    add_footer(draw, W, H, font_size=24)
    return img


def gen_15_hero(m):
    W, H = 1920, 1080
    sizes = get_type_scale(W, H)
    print("  [15/15] Hero / Portada...")
    img = gen_bg(PROMPTS["wide"], W, H)
    draw = ImageDraw.Draw(img)
    add_border(draw, W, H, 30)
    logo = load_logo("logo_gsr_blanco.png", 600)
    if logo:
        img.paste(logo, ((W - logo.width) // 2, 100), logo)
    t = m["textos"]["hero"]
    ft = get_font(sizes["title"])
    fs = get_font(sizes["subtitle"])
    y = H // 2
    text_auto(draw, t["principal"], y, ft, C_CLARO, W)
    y += lh(ft.size) + 20
    sep(draw, y, W, 120)
    y += 25
    text_center(draw, t["bajada"], y, fs, C_DORADO, W)
    add_footer(draw, W, H)
    return img


GENERATORS = [
    ("gsr_instagram_post_v7", gen_1_instagram_post),
    ("gsr_instagram_story", gen_2_instagram_story),
    ("gsr_instagram_carousel", gen_3_instagram_carousel),
    ("gsr_youtube_thumbnail", gen_4_youtube_thumbnail),
    ("gsr_youtube_banner", gen_5_youtube_banner),
    ("gsr_facebook_post", gen_6_facebook_post),
    ("gsr_facebook_ad", gen_7_facebook_ad),
    ("gsr_linkedin_post", gen_8_linkedin_post),
    ("gsr_linkedin_carousel", gen_9_linkedin_carousel),
    ("gsr_google_ads", gen_10_google_ads),
    ("gsr_twitter_post", gen_11_twitter),
    ("gsr_tiktok_cover", gen_12_tiktok_cover),
    ("gsr_pinterest_pin", gen_13_pinterest),
    ("gsr_flyer_a4", gen_14_flyer),
    ("gsr_hero", gen_15_hero),
]


if __name__ == "__main__":
    marca = load_brand()
    print("=" * 60)
    print("  GSR Abogados - Batch Generation v7")
    print("  AI background + Pillow text + Trust 3A + Modular Scale 1.333")
    print("=" * 60)
    generated = []
    for name, gen_fn in GENERATORS:
        try:
            result = gen_fn(marca)
            if isinstance(result, list):
                for i, img in enumerate(result):
                    path = OUTPUT / f"{name}_{i + 1}.png"
                    img.save(path, "PNG")
                    generated.append(path)
                    print(f"    -> {path.name}")
            else:
                path = OUTPUT / f"{name}.png"
                result.save(path, "PNG")
                generated.append(path)
                print(f"    -> {path.name}")
        except Exception as e:
            print(f"  ERROR en {name}: {e}")
    print(f"\n{'=' * 60}")
    print(f"  Total: {len(generated)} imagenes generadas")
    print(f"  Directorio: {OUTPUT}")
    print(f"{'=' * 60}")
