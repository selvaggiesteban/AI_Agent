#!/usr/bin/env python3
"""Genera todos los formatos de redes sociales para GSR Abogados."""
import sys
sys.path.insert(0, r"C:\Users\Esteban Selvaggi\Desktop\subagent-driven_development\scripts\ad_studio")

from brand.loader import cargar_brand_manual
from brand.prompt_builder import construir_prompt, construir_prompt_carrusel, construir_prompt_thumbnail
from generators.image_generator import generar_imagen, guardar_imagen
from config import OUTPUT_DIR

MARCA = cargar_brand_manual(r"C:\Users\Esteban Selvaggi\Desktop\subagent-driven_development\scripts\ad_studio\brand_manuals\gsr_abogados.json")
BASE = OUTPUT_DIR / "gsr_abogados"
BASE.mkdir(parents=True, exist_ok=True)

POSTS = [
    # 1. Instagram Post
    {
        "tipo": "instagram_post",
        "prompt": "Diseño elegante y austero con fondo oscuro #1D1412. Texto grande en tipografía serif dorada #F6E6D4: 'Cada caso es único. Lo defendemos como tal.' Monograma GSR sutil en esquina inferior. Mucho espacio en blanco. Estilo jurídico premium.",
        "ancho": 1080, "alto": 1080,
    },
    # 2. Instagram Story
    {
        "tipo": "instagram_story",
        "prompt": "Diseño vertical elegante. Fondo oscuro #1D1412 con textura sutil. Tipografía serif dorada #F6E6D4. Texto: 'Estudio Jurídico Penal' arriba, 'GARCETE SUÁREZ RONCO' al medio en letras grandes, 'ABOGADOS' abajo. Línea dorada decorativa sutil. Estilo premium, austero.",
        "ancho": 1080, "alto": 1920,
    },
    # 3. Instagram Carousel - Portada
    {
        "tipo": "instagram_carousel",
        "prompt": "Portada de carrusel. Fondo oscuro #1D1412. Tipografía serif dorada #F6E6D4. Título grande: 'Derecho Penal: Lo que necesitás saber'. Monograma GSR arriba. Diseño austero, elegante, tipografía clásica. Espacio amplio.",
        "ancho": 1080, "alto": 1350,
    },
    # 4. Instagram Carousel - Slide 2
    {
        "tipo": "instagram_carousel",
        "prompt": "Slide de carrusel. Fondo cálido #F6E6D4. Texto oscuro #1D1412 en tipografía serif. Título: '01. Derecho Penal Ordinario'. Descripción breve: 'Soluciones legales inmediatas ante causas penales complejas.' Diseño limpio, jerarquía clara, austero.",
        "ancho": 1080, "alto": 1350,
    },
    # 5. Instagram Carousel - Slide 3
    {
        "tipo": "instagram_carousel",
        "prompt": "Slide de carrusel. Fondo cálido #F6E6D4. Texto oscuro #1D1412 en tipografía serif. Título: '02. Derecho Penal Federal'. Descripción: 'Estrategias efectivas frente a investigaciones complejas del fuero federal.' Diseño limpio, austero.",
        "ancho": 1080, "alto": 1350,
    },
    # 6. Instagram Carousel - Slide 4
    {
        "tipo": "instagram_carousel",
        "prompt": "Slide de carrusel. Fondo cálido #F6E6D4. Texto oscuro #1D1412 en tipografía serif. Título: '03. Derecho Penal Económico'. Descripción: 'Blindaje legal corporativo ante delitos fiscales y financieros.' Diseño limpio, austero.",
        "ancho": 1080, "alto": 1350,
    },
    # 7. Instagram Carousel - CTA
    {
        "tipo": "instagram_carousel",
        "prompt": "Slide final CTA. Fondo oscuro #1D1412. Tipografía serif dorada #F6E6D4. Texto: '¿Necesitás asesoramiento penal?'. Botón dorado: 'Consultanos'. Datos de contacto abajo. Monograma GSR. Elegante, austero.",
        "ancho": 1080, "alto": 1350,
    },
    # 8. YouTube Thumbnail
    {
        "tipo": "youtube_thumbnail",
        "prompt": "Miniatura YouTube profesional. Fondo oscuro #1D1412. Texto grande serif dorado #F6E6D4: 'DEFENSA PENAL'. Subtítulo: 'Estrategias de litigación'. Monograma GSR. Estilo austero, elegante, alto contraste. Sin personas.",
        "ancho": 1280, "alto": 720,
    },
    # 9. YouTube Banner
    {
        "tipo": "youtube_banner",
        "prompt": "Banner de canal YouTube. Fondo oscuro #1D1412. Centro: 'GARCETE SUÁREZ RONCO' en serif dorada #F6E6D4. Abajo: 'ABOGADOS | DERECHO PENAL'. Línea dorada decorativa. Estilo austero, institucional, elegante.",
        "ancho": 2560, "alto": 1440,
    },
    # 10. Facebook Post
    {
        "tipo": "facebook_post",
        "prompt": "Post Facebook elegante. Fondo oscuro #1D1412. Tipografía serif dorada #F6E6D4. Texto: 'Cada caso es único. Lo defendemos como tal.' Línea dorada sutil. Monograma GSR. Diseño austero, profesional, premium.",
        "ancho": 1200, "alto": 630,
    },
    # 11. Facebook Ad
    {
        "tipo": "facebook_ad",
        "prompt": "Anuncio Meta Ads. Fondo oscuro #1D1412. Título serif dorado: 'Estudio Jurídico Penal'. Subtítulo: 'Litigios complejos. Fuero ordinario y federal.' CTA: 'Consultanos ahora'. Datos: gsrabogados.com.ar. Austero, elegante, sin fotos.",
        "ancho": 1200, "alto": 628,
    },
    # 12. LinkedIn Post
    {
        "tipo": "linkedin_post",
        "prompt": "Post LinkedIn profesional. Fondo cálido #F6E6D4. Texto oscuro #1D1412. Título serif: 'La complejidad de las causas penales contemporáneas exige un análisis que trasciende lo estrictamente jurídico.' Nombre del estudio abajo. Austero, académico.",
        "ancho": 1200, "alto": 627,
    },
    # 13. LinkedIn Carousel - Portada
    {
        "tipo": "linkedin_carousel",
        "prompt": "Portada carrusel LinkedIn. Fondo oscuro #1D1412. Serif dorada #F6E6D4. Título: 'Estructura Interdisciplinaria en la Defensa Penal'. Subtítulo: 'Garcete Suarez Ronco Abogados'. Austero, profesional, elegante.",
        "ancho": 1080, "alto": 1350,
    },
    # 14. Google Ads
    {
        "tipo": "google_ads",
        "prompt": "Anuncio Google Ads. Fondo oscuro #1D1412. Título serif dorado grande: 'Abogados Penales Buenos Aires'. Subtítulo: 'Defensa penal. Fuero ordinario y federal.' CTA: 'Contactanos'. gsrabogados.com.ar. Limpio, austero.",
        "ancho": 1200, "alto": 628,
    },
    # 15. Twitter/X Post
    {
        "tipo": "twitter_post",
        "prompt": "Post Twitter/X. Fondo oscuro #1D1412. Tipografía serif dorada #F6E6D4. Texto grande: 'Protegemos tu patrimonio, tu reputación y tu libertad.' Línea dorada sutil. Monograma GSR. Austero, directo, elegante.",
        "ancho": 1600,
        "alto": 900,
    },
    # 16. TikTok Cover
    {
        "tipo": "tiktok_cover",
        "prompt": "Portada TikTok. Fondo oscuro #1D1412. Tipografía serif dorada #F6E6D4. Texto grande centrado: 'DERECHO PENAL'. Subtítulo: 'Lo que necesitás saber'. Monograma GSR. Austero, elegante, alto contraste.",
        "ancho": 1080,
        "alto": 1920,
    },
    # 17. Pinterest Pin
    {
        "tipo": "pinterest_pin",
        "prompt": "Pin Pinterest vertical. Fondo oscuro #1D1412. Serif dorada #F6E6D4. Título arriba: 'Guía de Derecho Penal'. Descripción: '4 áreas de práctica clave'. Datos del estudio abajo. Austero, elegante, tipografía clásica.",
        "ancho": 1000,
        "alto": 1500,
    },
    # 18. Flyer A4
    {
        "tipo": "flyer_a4",
        "prompt": "Flyer A4 vertical. Fondo cálido #F6E6D4. Texto oscuro #1D1412. Arriba: monograma GSR. Título grande serif: 'GARCETE SUÁREZ RONCO ABOGADOS'. Línea dorada. Áreas de práctica: Penal Ordinario, Federal, Económico, Ejecución Penal. Datos de contacto abajo. Austero, elegante, institucional.",
        "ancho": 2480,
        "alto": 3508,
    },
]

print(f"Generando {len(POSTS)} piezas para GSR Abogados...\n")

for i, post in enumerate(POSTS, 1):
    print(f"\n[{i}/{len(POSTS)}] {post['tipo']}...")

    prompt = construir_prompt(post["prompt"], MARCA)
    img = generar_imagen(prompt, ancho=post["ancho"], alto=post["alto"])

    nombre = f"gsr_{post['tipo']}_{i:02d}.png"
    ruta = BASE / nombre
    guardar_imagen(img, ruta)
    print(f"  Guardado: {ruta}")

print(f"\n{'='*60}")
print(f"  COMPLETADO: {len(POSTS)} piezas en {BASE}")
print(f"{'='*60}")
