import json
from pathlib import Path


CAMPOS_REQUERIDOS = ["nombre", "colores", "tono", "estilo"]
CAMPOS_OPCIONALES = [
    "tipografia", "logo", "prohibido", "descripcion", "website", "redes",
    "hero", "frases_clave", "textos", "fotos", "especialidades", "abogados",
    "estructura_interdisciplinaria", "contacto", "imagen", "estructura"
]


def cargar_brand_manual(ruta):
    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(f"Brand manual no encontrado: {ruta}")

    with open(ruta, "r", encoding="utf-8") as f:
        marca = json.load(f)

    errores = []
    for campo in CAMPOS_REQUERIDOS:
        if campo not in marca:
            errores.append(f"Falta campo requerido: {campo}")

    if "colores" in marca:
        for color_key in ["primario", "secundario"]:
            if color_key not in marca["colores"]:
                errores.append(f"Falta color '{color_key}' en seccion colores")

    if errores:
        raise ValueError(f"Brand manual invalido:\n" + "\n".join(f"  - {e}" for e in errores))

    defaults = {
        "tipografia": {"titulares": "Arial Bold", "cuerpo": "Arial"},
        "logo": None,
        "prohibido": [],
        "descripcion": "",
        "website": "",
        "redes": {},
        "hero": {"principal": "", "bajada": ""},
        "frases_clave": [],
        "textos": {},
        "fotos": {},
        "especialidades": [],
        "abogados": [],
        "estructura_interdisciplinaria": "",
        "contacto": {},
        "imagen": {},
        "estructura": "",
    }
    for key, val in defaults.items():
        if key not in marca:
            marca[key] = val

    return marca


def crear_brand_manual_ejemplo():
    return {
        "nombre": "Pizzeria Don Carlos",
        "descripcion": "Pizzeria artesanal italiana fundada en 1985",
        "colores": {
            "primario": "#C41E3A",
            "secundario": "#FFD700",
            "acento": "#2E8B57",
            "fondo": "#FFFFFF",
            "texto": "#1A1A1A",
        },
        "tipografia": {
            "titulares": "Bebas Neue",
            "cuerpo": "Open Sans",
        },
        "logo": None,
        "tono": "casual, cordial, cercano",
        "estilo": "fotos de comida real, colores vibrantes, estilo italiano rustico",
        "prohibido": [
            "textos genericos",
            "colores neón",
            "fotos stock de gente sonriente",
        ],
        "website": "https://ejemplo-pizzeria.com",
        "redes": {
            "instagram": "@pizzeriadoncarlos",
            "facebook": "Pizzeria Don Carlos",
        },
    }


def guardar_brand_manual(marca, ruta):
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(marca, f, indent=2, ensure_ascii=False)
    return ruta
