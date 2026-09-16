#!/usr/bin/env python3
"""Generador genérico de formatos de redes sociales basado en manuales de marca."""
import sys
import argparse
from pathlib import Path

# Configuración de rutas relativas para evitar dependencias de sistema
from config import OUTPUT_DIR, BRAND_MANUALS_DIR
from brand.loader import cargar_brand_manual
from brand.prompt_builder import construir_prompt, construir_prompt_carrusel, construir_prompt_thumbnail
from generators.image_generator import generar_imagen, guardar_imagen

def main():
    parser = argparse.ArgumentParser(description="Generador de anuncios basado en marca.")
    parser.add_argument(
        "brand_id",
        nargs="?",
        default="gsr_abogados",
        help="ID del manual de marca (nombre del archivo JSON sin .json)"
    )
    args = parser.parse_args()

    # 1. Carga del Manual de Marca
    manual_path = BRAND_MANUALS_DIR / f"{args.brand_id}.json"
    try:
        marca = cargar_brand_manual(manual_path)
        print(f"✅ Marca cargada: {marca['nombre']}")
    except Exception as e:
        print(f"❌ Error cargando marca {args.brand_id}: {e}")
        sys.exit(1)

    # 2. Configuración de Salida
    base_output = OUTPUT_DIR / args.brand_id
    base_output.mkdir(parents=True, exist_ok=True)

    # 3. Definición de Piezas (Estandarizadas)
    # Se utiliza el manual de marca para personalizar los prompts dinámicamente
    posts = [
        {
            "tipo": "instagram_post",
            "prompt": "Diseño elegante y austero con fondo oscuro. Texto grande en tipografía serif dorada. Estilo premium.",
            "ancho": 1080, "alto": 1080,
        },
        {
            "tipo": "instagram_story",
            "prompt": "Diseño vertical elegante. Fondo oscuro con textura sutil. Tipografía serif dorada. Estilo premium, austero.",
            "ancho": 1080, "alto": 1920,
        },
        {
            "tipo": "instagram_carousel",
            "prompt": "Portada de carrusel. Fondo oscuro. Tipografía serif dorada. Diseño austero, elegante, tipografía clásica. Espacio amplio.",
            "ancho": 1080, "alto": 1350,
        },
        {
            "tipo": "facebook_post",
            "prompt": "Post Facebook elegante. Fondo oscuro. Tipografía serif dorada. Diseño austero, profesional, premium.",
            "ancho": 1200, "alto": 630,
        },
        {
            "tipo": "linkedin_post",
            "prompt": "Post LinkedIn profesional. Fondo cálido. Texto oscuro. Título serif. Austero, académico.",
            "ancho": 1200, "alto": 627,
        },
        {
            "tipo": "google_ads",
            "prompt": "Anuncio Google Ads. Fondo oscuro. Título serif dorado grande. Limpio, austero.",
            "ancho": 1200, "alto": 628,
        },
        {
            "tipo": "twitter_post",
            "prompt": "Post Twitter/X. Fondo oscuro. Tipografía serif dorada. Austero, directo, elegante.",
            "ancho": 1600, "alto": 900,
        },
        {
            "tipo": "tiktok_cover",
            "prompt": "Portada TikTok. Fondo oscuro. Tipografía serif dorada. Texto grande centrado. Austero, elegante, alto contraste.",
            "ancho": 1080, "alto": 1920,
        },
        {
            "tipo": "pinterest_pin",
            "prompt": "Pin Pinterest vertical. Fondo oscuro. Serif dorada. Título arriba. Austero, elegante, tipografía clásica.",
            "ancho": 1000, "alto": 1500,
        },
        {
            "tipo": "flyer_a4",
            "prompt": "Flyer A4 vertical. Fondo cálido. Texto oscuro. Diseño institucional. Austero, elegante.",
            "ancho": 2480, "alto": 3508,
        },
    ]

    print(f"Generando {len(posts)} piezas para {marca['nombre']}...\n")

    for i, post in enumerate(posts, 1):
        print(f"[{i}/{len(posts)}] {post['tipo']}...")

        # El prompt builder ahora inyecta los datos del manual de marca
        prompt = construir_prompt(post["prompt"], marca)
        img = generar_imagen(prompt, ancho=post["ancho"], alto=post["alto"])

        nombre = f"{args.brand_id}_{post['tipo']}_{i:02d}.png"
        ruta = base_output / nombre
        guardar_imagen(img, ruta)
        print(f"  Guardado: {ruta}")

    print(f"\n{'='*60}")
    print(f"  COMPLETADO: {len(posts)} piezas en {base_output}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
