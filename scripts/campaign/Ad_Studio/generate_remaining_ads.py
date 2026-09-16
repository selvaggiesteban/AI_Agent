#!/usr/bin/env python3
"""
Generador de piezas complementarias de Ad Studio.
Soporta múltiples marcas y rutas relativas para portabilidad.
"""
import sys
import argparse
from pathlib import Path

# Importaciones del ecosistema ad_studio
from config import OUTPUT_DIR, BRAND_MANUALS_DIR
from brand.loader import cargar_brand_manual
from brand.prompt_builder import construir_prompt
from generators.image_generator import generar_imagen, guardar_imagen

def main():
    parser = argparse.ArgumentParser(description="Generador de piezas complementarias de Ad Studio.")
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

    # 3. Definición de Piezas Complementarias
    posts = [
        {"idx": 8, "tipo": "youtube_thumbnail", "prompt": "Miniatura YouTube profesional. Fondo oscuro. Texto grande serif dorado. Estilo austero, elegante, alto contraste.", "ancho": 1280, "alto": 720},
        {"idx": 9, "tipo": "youtube_banner", "prompt": "Banner canal YouTube. Fondo oscuro. Centro: nombre de marca en serif dorada. Abajo: especialidad. Línea dorada. Austero, institucional.", "ancho": 2560, "alto": 1440},
        {"idx": 10, "tipo": "facebook_post", "prompt": "Post Facebook elegante. Fondo oscuro. Serif dorada. Diseño austero, profesional, premium.", "ancho": 1200, "alto": 630},
        {"idx": 11, "tipo": "facebook_ad", "prompt": "Anuncio Meta Ads. Fondo oscuro. Título serif dorado. Subtítulo. CTA. Austero, elegante.", "ancho": 1200, "alto": 628},
        {"idx": 12, "tipo": "linkedin_post", "prompt": "Post LinkedIn profesional. Fondo cálido. Texto oscuro. Serif. Austero, académico.", "ancho": 1200, "alto": 627},
        {"idx": 13, "tipo": "linkedin_carousel", "prompt": "Portada carrusel LinkedIn. Fondo oscuro. Serif dorada. Título y subtítulo. Austero, profesional.", "ancho": 1080, "alto": 1350},
        {"idx": 14, "tipo": "google_ads", "prompt": "Anuncio Google Ads. Fondo oscuro. Serif dorado grande. Limpio, austero.", "ancho": 1200, "alto": 628},
        {"idx": 15, "tipo": "twitter_post", "prompt": "Post Twitter/X. Fondo oscuro. Tipografía serif dorada. Austero, directo, elegante.", "ancho": 1600, "alto": 900},
        {"idx": 16, "tipo": "tiktok_cover", "prompt": "Portada TikTok. Fondo oscuro. Tipografía serif dorada. Texto grande centrado. Austero, elegante.", "ancho": 1080, "alto": 1920},
        {"idx": 17, "tipo": "pinterest_pin", "prompt": "Pin Pinterest vertical. Fondo oscuro. Serif dorada. Título y descripción. Austero, elegante.", "ancho": 1000, "alto": 1500},
        {"idx": 18, "tipo": "flyer_a4", "prompt": "Flyer A4 vertical. Fondo cálido. Texto oscuro. Diseño institucional. Austero, elegante.", "ancho": 2480, "alto": 3508},
    ]

    print(f"Generando {len(posts)} piezas restantes para {marca['nombre']}...\n")

    for post in posts:
        print(f"[{post['idx']}/18] {post['tipo']}...")
        prompt = construir_prompt(post["prompt"], marca)
        img = generar_imagen(prompt, ancho=post["ancho"], alto=post["alto"])
        nombre = f"{args.brand_id}_{post['tipo']}_{post['idx']:02d}.png"
        ruta = base_output / nombre
        guardar_imagen(img, ruta)
        print(f"  Guardado: {ruta}")

    print(f"\n{'='*60}")
    print(f"  COMPLETADO: Piezas complementarias generadas en {base_output}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
