def construir_prompt(descripcion, marca, formato=None, idioma="es"):
    colores = marca.get("colores", {})
    estilo = marca.get("estilo", "")
    tono = marca.get("tono", "")
    tipografia = marca.get("tipografia", {})
    prohibido = marca.get("prohibido", [])
    textos = marca.get("textos", {})
    fotos = marca.get("fotos", {})
    especialidades = marca.get("especialidades", [])

    partes = []

    partes.append(f"Crea una imagen para {marca['nombre']}.")

    if descripcion:
        partes.append(f"Contenido: {descripcion}")

    if estilo:
        partes.append(f"Estilo visual: {estilo}")

    if tono:
        partes.append(f"Tono: {tono}")

    if colores:
        colores_str = ", ".join(
            f"{k}: {v}" for k, v in colores.items() if k in ["primario", "secundario", "acento"]
        )
        if colores_str:
            partes.append(f"Paleta de colores: {colores_str}")

        if "fondo" in colores:
            partes.append(f"Fondo: {colores['fondo']}")

        if "texto" in colores:
            partes.append(f"Color de texto: {colores['texto']}")

    if tipografia:
        titulares = tipografia.get("titulares", "")
        if titulares:
            partes.append(f"Tipografia de titulares: {titulares}, bold, grande, legible")

    if especialidades:
        areas = " · ".join(e["nombre"] if isinstance(e, dict) else e for e in especialidades)
        partes.append(f"Áreas de práctica: {areas}")

    if formato:
        partes.append(f"Formato: {formato.get('ancho')}x{formato.get('alto')} px")
        if "orientacion" in formato:
            partes.append(f"Orientacion: {formato['orientacion']}")
        if "guia_composicion" in formato:
            partes.append(f"Composicion: {formato['guia_composicion']}")

        formato_nombre = formato.get("nombre", "")
        if formato_nombre and formato_nombre in textos:
            texto_formato = textos[formato_nombre]
            if isinstance(texto_formato, dict):
                for k, v in texto_formato.items():
                    if v:
                        partes.append(f"Texto del formato ({k}): {v}")
            elif isinstance(texto_formato, list):
                for slide_info in texto_formato[:3]:
                    if isinstance(slide_info, dict):
                        titulo = slide_info.get("titulo", "")
                        if titulo:
                            partes.append(f"Slide {slide_info.get('slide', '?')}: {titulo}")

    if fotos:
        uso = fotos.get("uso_recomendado", {})
        if formato and "nombre" in formato:
            fmt = formato["nombre"]
            if "carrusel" in fmt and "carrusel" in uso:
                partes.append(f"Uso de fotos: {uso['carrusel']}")
            elif "story" in fmt and "stories" in uso:
                partes.append(f"Uso de fotos: {uso['stories']}")
            elif "thumbnail" in fmt and "thumbnails" in uso:
                partes.append(f"Uso de fotos: {uso['thumbnails']}")
            elif "flyer" in fmt and "flyer" in uso:
                partes.append(f"Uso de fotos: {uso['flyer']}")

    if prohibido:
        partes.append("NO incluir: " + ", ".join(prohibido))

    partes.append("Sin marcas de agua, sin logos de plataformas, imagen profesional de alta calidad.")

    return " ".join(partes)


def construir_prompt_carrusel(titulo, puntos, marca, slides=5):
    prompts = []

    colores = marca.get("colores", {})
    estilo = marca.get("estilo", "")
    tono = marca.get("tono", "")

    prompt_portada = (
        f"Crea la portada de un carrusel para {marca['nombre']}. "
        f"Titulo grande y llamativo: '{titulo}'. "
        f"Estilo: {estilo}. Tono: {tono}. "
        f"Colores: primario {colores.get('primario', '#000')}, "
        f"secundario {colores.get('secundario', '#FFF')}. "
        f"Formato 1080x1350 px. Moderno, profesional, sin marcas de agua."
    )
    prompts.append({"slide": 1, "tipo": "portada", "prompt": prompt_portada})

    for i, punto in enumerate(puntos[:slides - 2], start=2):
        prompt_slide = (
            f"Crea el slide {i} de un carrusel para {marca['nombre']}. "
            f"Titulo: '{punto}'. "
            f"Una idea por slide, texto maximo 15 palabras. "
            f"Estilo: {estilo}. Colores: primario {colores.get('primario', '#000')}, "
            f"secundario {colores.get('secundario', '#FFF')}. "
            f"Formato 1080x1350 px. Visual moderno, sin marcas de agua."
        )
        prompts.append({"slide": i, "tipo": "contenido", "prompt": prompt_slide})

    prompt_cta = (
        f"Crea el slide final (CTA) de un carrusel para {marca['nombre']}. "
        f"Invita a seguir, compartir o visitar. "
        f"Estilo: {estilo}. Colores: primario {colores.get('primario', '#000')}. "
        f"Formato 1080x1350 px. Llamativo, sin marcas de agua."
    )
    prompts.append({"slide": slides, "tipo": "cta", "prompt": prompt_cta})

    return prompts


def construir_prompt_thumbnail(titulo, marca, tono="profesional"):
    colores = marca.get("colores", {})
    estilo = marca.get("estilo", "")

    return (
        f"Crea una miniatura de YouTube para {marca['nombre']}. "
        f"Titulo en texto grande (3-5 palabras): '{titulo}'. "
        f"Estilo: {estilo}. Tono: {tono}. "
        f"Colores: primario {colores.get('primario', '#000')}, "
        f"acento {colores.get('acento', '#FF0000')}. "
        f"Formato 1280x720 px. Cara ocupa 30-50% del frame si hay persona. "
        f"Texto legible en movil. Sin marcas de agua, sin logos de YouTube."
    )
