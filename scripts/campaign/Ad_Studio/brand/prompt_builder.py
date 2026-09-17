def build_prompt(description, marca, format=None, language="en"):
    colores = marca.get("colores", {})
    estilo = marca.get("estilo", "")
    tono = marca.get("tono", "")
    tipografia = marca.get("tipografia", {})
    prohibido = marca.get("prohibido", [])
    textos = marca.get("textos", {})
    fotos = marca.get("fotos", {})
    especialidades = marca.get("especialidades", [])

    parts = []

    parts.append(f"Create an image for {marca['nombre']}.")

    if description:
        parts.append(f"Content: {description}")

    if estilo:
        parts.append(f"Visual style: {estilo}")

    if tono:
        parts.append(f"Tone: {tono}")

    if colores:
        colores_str = ", ".join(
            f"{k}: {v}" for k, v in colores.items() if k in ["primario", "secundario", "acento"]
        )
        if colores_str:
            parts.append(f"Color palette: {colores_str}")

        if "fondo" in colores:
            parts.append(f"Background: {colores['fondo']}")

        if "texto" in colores:
            parts.append(f"Text color: {colores['texto']}")

    if tipografia:
        titulares = tipografia.get("titulares", "")
        if titulares:
            parts.append(f"Headline typography: {titulares}, bold, large, legible")

    if especialidades:
        areas = " · ".join(e["nombre"] if isinstance(e, dict) else e for e in especialidades)
        parts.append(f"Practice areas: {areas}")

    if format:
        parts.append(f"Format: {format.get('ancho')}x{format.get('alto')} px")
        if "orientacion" in format:
            parts.append(f"Orientation: {format['orientacion']}")
        if "guia_composicion" in format:
            parts.append(f"Composition: {format['guia_composicion']}")

        format_name = format.get("nombre", "")
        if format_name and format_name in textos:
            texto_format = textos[format_name]
            if isinstance(texto_format, dict):
                for k, v in texto_format.items():
                    if v:
                        parts.append(f"Format text ({k}): {v}")
            elif isinstance(texto_format, list):
                for slide_info in texto_format[:3]:
                    if isinstance(slide_info, dict):
                        titulo = slide_info.get("titulo", "")
                        if titulo:
                            parts.append(f"Slide {slide_info.get('slide', '?')}: {titulo}")

    if fotos:
        uso = fotos.get("uso_recomendado", {})
        if format and "nombre" in format:
            fmt = format["nombre"]
            if "carrusel" in fmt and "carrusel" in uso:
                parts.append(f"Photo usage: {uso['carrusel']}")
            elif "story" in fmt and "stories" in uso:
                parts.append(f"Photo usage: {uso['stories']}")
            elif "thumbnail" in fmt and "thumbnails" in uso:
                parts.append(f"Photo usage: {uso['thumbnails']}")
            elif "flyer" in fmt and "flyer" in uso:
                parts.append(f"Photo usage: {uso['flyer']}")

    if prohibido:
        parts.append("DO NOT include: " + ", ".join(prohibido))

    parts.append("No watermarks, no platform logos, professional high-quality image.")

    return " ".join(parts)


def build_carousel_prompt(titulo, puntos, marca, slides=5):
    prompts = []

    colores = marca.get("colores", {})
    estilo = marca.get("estilo", "")
    tono = marca.get("tono", "")

    prompt_portada = (
        f"Create a carousel cover for {marca['nombre']}. "
        f"Large and catchy title: '{titulo}'. "
        f"Style: {estilo}. Tone: {tono}. "
        f"Colors: primary {colores.get('primario', '#000')}, "
        f"secondary {colores.get('secundario', '#FFF')}. "
        f"Format 1080x1350 px. Modern, professional, no watermarks."
    )
    prompts.append({"slide": 1, "tipo": "portada", "prompt": prompt_portada})

    for i, punto in enumerate(puntos[:slides - 2], start=2):
        prompt_slide = (
            f"Create slide {i} of a carousel for {marca['nombre']}. "
            f"Title: '{punto}'. "
            f"One idea per slide, max 15 words. "
            f"Style: {estilo}. Colors: primary {colores.get('primario', '#000')}, "
            f"secondary {colores.get('secundario', '#FFF')}. "
            f"Format 1080x1350 px. Modern visual, no watermarks."
        )
        prompts.append({"slide": i, "tipo": "contenido", "prompt": prompt_slide})

    prompt_cta = (
        f"Create the final (CTA) slide of a carousel for {marca['nombre']}. "
        f"Invite to follow, share or visit. "
        f"Style: {estilo}. Colors: primary {colores.get('primario', '#000')}. "
        f"Format 1080x1350 px. Eye-catching, no watermarks."
    )
    prompts.append({"slide": slides, "tipo": "cta", "prompt": prompt_cta})

    return prompts


def build_thumbnail_prompt(titulo, marca, tono="profesional"):
    colores = marca.get("colores", {})
    estilo = marca.get("estilo", "")

    return (
        f"Create a YouTube thumbnail for {marca['nombre']}. "
        f"Large text title (3-5 words): '{titulo}'. "
        f"Style: {estilo}. Tone: {tono}. "
        f"Colors: primary {colores.get('primario', '#000')}, "
        f"accent {colores.get('acento', '#FF0000')}. "
        f"Format 1280x720 px. Face occupies 30-50% of the frame if there is a person. "
        f"Text readable on mobile. No watermarks, no YouTube logos."
    )
