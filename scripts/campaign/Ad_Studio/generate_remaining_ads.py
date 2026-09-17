#!/usr/bin/env python3
"""
Ad Studio complementary assets generator.
Supports multiple brands and relative paths for portability.
"""
import sys
import argparse
from pathlib import Path

# Ad Studio ecosystem imports
from config import OUTPUT_DIR, BRAND_MANUALS_DIR
from brand.loader import cargar_brand_manual
from brand.prompt_builder import construir_prompt
from generators.image_generator import generar_imagen, guardar_imagen

def main():
    parser = argparse.ArgumentParser(description="Ad Studio complementary assets generator.")
    parser.add_argument(
        "brand_id",
        nargs="?",
        default="gsr_abogados",
        help="Brand manual ID (JSON filename without .json)"
    )
    args = parser.parse_args()

    # 1. Brand Manual Loading
    manual_path = BRAND_MANUALS_DIR / f"{args.brand_id}.json"
    try:
        marca = cargar_brand_manual(manual_path)
        print(f"✅ Brand loaded: {marca['nombre']}")
    except Exception as e:
        print(f"❌ Error loading brand {args.brand_id}: {e}")
        sys.exit(1)

    # 2. Output Configuration
    base_output = OUTPUT_DIR / args.brand_id
    base_output.mkdir(parents=True, exist_ok=True)

    # 3. Definition of Complementary Assets
    posts = [
        {"idx": 8, "tipo": "youtube_thumbnail", "prompt": "Professional YouTube thumbnail. Dark background. Large golden serif text. Austere, elegant, high contrast style.", "ancho": 1280, "alto": 720},
        {"idx": 9, "tipo": "youtube_banner", "prompt": "YouTube channel banner. Dark background. Center: brand name in golden serif. Bottom: specialty. Golden line. Austere, institutional.", "ancho": 2560, "alto": 1440},
        {"idx": 10, "tipo": "facebook_post", "prompt": "Elegant Facebook post. Dark background. Golden serif. Austere, professional, premium design.", "ancho": 1200, "alto": 630},
        {"idx": 11, "tipo": "facebook_ad", "prompt": "Meta Ads ad. Dark background. Golden serif title. Subtitle. CTA. Austere, elegant.", "ancho": 1200, "alto": 628},
        {"idx": 12, "tipo": "linkedin_post", "prompt": "Professional LinkedIn post. Warm background. Dark text. Serif. Austere, academic.", "ancho": 1200, "alto": 627},
        {"idx": 13, "tipo": "linkedin_carousel", "prompt": "LinkedIn carousel cover. Dark background. Golden serif. Title and subtitle. Austere, professional.", "ancho": 1080, "alto": 1350},
        {"idx": 14, "tipo": "google_ads", "prompt": "Google Ads ad. Dark background. Large golden serif. Clean, austere.", "ancho": 1200, "alto": 628},
        {"idx": 15, "tipo": "twitter_post", "prompt": "Twitter/X post. Dark background. Golden serif typography. Austere, direct, elegant.", "ancho": 1600, "alto": 900},
        {"idx": 16, "tipo": "tiktok_cover", "prompt": "TikTok cover. Dark background. Golden serif typography. Large centered text. Austere, elegant.", "ancho": 1080, "alto": 1920},
        {"idx": 17, "tipo": "pinterest_pin", "prompt": "Vertical Pinterest pin. Dark background. Golden serif. Title and description. Austere, elegant.", "ancho": 1000, "alto": 1500},
        {"idx": 18, "tipo": "flyer_a4", "prompt": "Vertical A4 flyer. Warm background. Dark text. Institutional design. Austere, elegant.", "ancho": 2480, "alto": 3508},
    ]

    print(f"Generating {len(posts)} remaining assets for {marca['nombre']}...\n")

    for post in posts:
        print(f"[{post['idx']}/18] {post['tipo']}...")
        prompt = construir_prompt(post["prompt"], marca)
        img = generar_imagen(prompt, ancho=post["ancho"], alto=post["alto"])
        nombre = f"{args.brand_id}_{post['tipo']}_{post['idx']:02d}.png"
        ruta = base_output / nombre
        guardar_imagen(img, ruta)
        print(f"  Saved: {ruta}")

    print(f"\n{'='*60}")
    print(f"  COMPLETED: Complementary assets generated in {base_output}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
