#!/usr/bin/env python3
"""Generic social media format generator based on brand manuals."""
import sys
import argparse
from pathlib import Path

# Relative path configuration to avoid system dependencies
from config import OUTPUT_DIR, BRAND_MANUALS_DIR
from brand.loader import cargar_brand_manual
from brand.prompt_builder import construir_prompt, construir_prompt_carrusel, construir_prompt_thumbnail
from generators.image_generator import generar_imagen, guardar_imagen

def main():
    parser = argparse.ArgumentParser(description="Brand-based ad generator.")
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

    # 3. Definition of Assets (Standardized)
    # Brand manual used to personalize prompts dynamically
    posts = [
        {
            "tipo": "instagram_post",
            "prompt": "Elegant and austere design with dark background. Large text in golden serif typography. Premium style.",
            "ancho": 1080, "alto": 1080,
        },
        {
            "tipo": "instagram_story",
            "prompt": "Elegant vertical design. Dark background with subtle texture. Golden serif typography. Premium, austere style.",
            "ancho": 1080, "alto": 1920,
        },
        {
            "tipo": "instagram_carousel",
            "prompt": "Carousel cover. Dark background. Golden serif typography. Austere, elegant design, classic typography. Ample space.",
            "ancho": 1080, "alto": 1350,
        },
        {
            "tipo": "facebook_post",
            "prompt": "Elegant Facebook post. Dark background. Golden serif typography. Austere, professional, premium design.",
            "ancho": 1200, "alto": 630,
        },
        {
            "tipo": "linkedin_post",
            "prompt": "Professional LinkedIn post. Warm background. Dark text. Serif title. Austere, academic.",
            "ancho": 1200, "alto": 627,
        },
        {
            "tipo": "google_ads",
            "prompt": "Google Ads ad. Dark background. Large golden serif title. Clean, austere.",
            "ancho": 1200, "alto": 628,
        },
        {
            "tipo": "twitter_post",
            "prompt": "Twitter/X post. Dark background. Golden serif typography. Austere, direct, elegant.",
            "ancho": 1600, "alto": 900,
        },
        {
            "tipo": "tiktok_cover",
            "prompt": "TikTok cover. Dark background. Golden serif typography. Large centered text. Austere, elegant, high contrast.",
            "ancho": 1080, "alto": 1920,
        },
        {
            "tipo": "pinterest_pin",
            "prompt": "Vertical Pinterest pin. Dark background. Golden serif. Title at the top. Austere, elegant, classic typography.",
            "ancho": 1000, "alto": 1500,
        },
        {
            "tipo": "flyer_a4",
            "prompt": "Vertical A4 flyer. Warm background. Dark text. Institutional design. Austere, elegant.",
            "ancho": 2480, "alto": 3508,
        },
    ]

    print(f"Generating {len(posts)} assets for {marca['nombre']}...\n")

    for i, post in enumerate(posts, 1):
        print(f"[{i}/{len(posts)}] {post['tipo']}...")

        # The prompt builder now injects brand manual data
        prompt = construir_prompt(post["prompt"], marca)
        img = generar_imagen(prompt, ancho=post["ancho"], alto=post["alto"])

        nombre = f"{args.brand_id}_{post['tipo']}_{i:02d}.png"
        ruta = base_output / nombre
        guardar_imagen(img, ruta)
        print(f"  Saved: {ruta}")

    print(f"\n{'='*60}")
    print(f"  COMPLETED: {len(posts)} assets in {base_output}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
