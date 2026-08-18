#!/usr/bin/env python3
"""Genera los formatos restantes para GSR Abogados."""
import sys
sys.path.insert(0, r"C:\Users\Esteban Selvaggi\Desktop\subagent-driven_development\scripts\ad_studio")

from brand.loader import cargar_brand_manual
from brand.prompt_builder import construir_prompt
from generators.image_generator import generar_imagen, guardar_imagen
from config import OUTPUT_DIR

MARCA = cargar_brand_manual(r"C:\Users\Esteban Selvaggi\Desktop\subagent-driven_development\scripts\ad_studio\brand_manuals\gsr_abogados.json")
BASE = OUTPUT_DIR / "gsr_abogados"
BASE.mkdir(parents=True, exist_ok=True)

# Solo los que faltan
POSTS = [
    {"idx": 8, "tipo": "youtube_thumbnail", "prompt": "Miniatura YouTube profesional. Fondo oscuro #1D1412. Texto grande serif dorado #F6E6D4: 'DEFENSA PENAL'. Subtítulo: 'Estrategias de litigación'. Monograma GSR. Austero, elegante, alto contraste.", "ancho": 1280, "alto": 720},
    {"idx": 9, "tipo": "youtube_banner", "prompt": "Banner canal YouTube. Fondo oscuro #1D1412. Centro: 'GARCETE SUÁREZ RONCO' en serif dorada #F6E6D4. Abajo: 'ABOGADOS | DERECHO PENAL'. Línea dorada. Austero, institucional.", "ancho": 2560, "alto": 1440},
    {"idx": 10, "tipo": "facebook_post", "prompt": "Post Facebook elegante. Fondo oscuro #1D1412. Serif dorada #F6E6D4. Texto: 'Cada caso es único. Lo defendemos como tal.' Monograma GSR. Austero, premium.", "ancho": 1200, "alto": 630},
    {"idx": 11, "tipo": "facebook_ad", "prompt": "Anuncio Meta Ads. Fondo oscuro #1D1412. Título serif dorado: 'Estudio Jurídico Penal'. Subtítulo: 'Litigios complejos. Fuero ordinario y federal.' CTA: 'Consultanos'. Austero, elegante.", "ancho": 1200, "alto": 628},
    {"idx": 12, "tipo": "linkedin_post", "prompt": "Post LinkedIn profesional. Fondo cálido #F6E6D4. Texto oscuro #1D1412. Serif: 'La complejidad de las causas penales contemporáneas exige un análisis que trasciende lo estrictamente jurídico.' Austero, académico.", "ancho": 1200, "alto": 627},
    {"idx": 13, "tipo": "linkedin_carousel", "prompt": "Portada carrusel LinkedIn. Fondo oscuro #1D1412. Serif dorada #F6E6D4. Título: 'Estructura Interdisciplinaria en la Defensa Penal'. Subtítulo: 'Garcete Suarez Ronco Abogados'. Austero, profesional.", "ancho": 1080, "alto": 1350},
    {"idx": 14, "tipo": "google_ads", "prompt": "Anuncio Google Ads. Fondo oscuro #1D1412. Serif dorado grande: 'Abogados Penales Buenos Aires'. Subtítulo: 'Defensa penal. Fuero ordinario y federal.' CTA: 'Contactanos'. Limpio, austero.", "ancho": 1200, "alto": 628},
    {"idx": 15, "tipo": "twitter_post", "prompt": "Post Twitter/X. Fondo oscuro #1D1412. Serif dorada #F6E6D4. Texto grande: 'Protegemos tu patrimonio, tu reputación y tu libertad.' Monograma GSR. Austero, directo, elegante.", "ancho": 1600, "alto": 900},
    {"idx": 16, "tipo": "tiktok_cover", "prompt": "Portada TikTok. Fondo oscuro #1D1412. Serif dorada #F6E6D4. Texto grande centrado: 'DERECHO PENAL'. Subtítulo: 'Lo que necesitás saber'. Monograma GSR. Austero, elegante.", "ancho": 1080, "alto": 1920},
    {"idx": 17, "tipo": "pinterest_pin", "prompt": "Pin Pinterest vertical. Fondo oscuro #1D1412. Serif dorada #F6E6D4. Título: 'Guía de Derecho Penal'. Descripción: '4 áreas de práctica clave'. Datos del estudio. Austero, elegante.", "ancho": 1000, "alto": 1500},
    {"idx": 18, "tipo": "flyer_a4", "prompt": "Flyer A4 vertical. Fondo cálido #F6E6D4. Texto oscuro #1D1412. Arriba: monograma GSR. Título: 'GARCETE SUÁREZ RONCO ABOGADOS'. Áreas: Penal Ordinario, Federal, Económico, Ejecución. Contacto abajo. Austero, elegante.", "ancho": 2480, "alto": 3508},
]

print(f"Generando {len(POSTS)} piezas restantes...\n")

for post in POSTS:
    print(f"\n[{post['idx']}/18] {post['tipo']}...")
    prompt = construir_prompt(post["prompt"], MARCA)
    img = generar_imagen(prompt, ancho=post["ancho"], alto=post["alto"])
    nombre = f"gsr_{post['tipo']}_{post['idx']:02d}.png"
    ruta = BASE / nombre
    guardar_imagen(img, ruta)
    print(f"  Guardado: {ruta}")

print(f"\n{'='*60}")
print(f"  COMPLETADO")
print(f"{'='*60}")
