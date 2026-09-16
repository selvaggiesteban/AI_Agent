from pathlib import Path

# Ruta base del módulo ad_studio
BASE_DIR = Path(__file__).parent

# Directorio de salida para todas las imágenes generadas
OUTPUT_DIR = BASE_DIR / "output"

# Directorio donde se almacenan los manuales de marca (JSON)
BRAND_MANUALS_DIR = BASE_DIR / "brand_manuals"

# Directorio de assets globales
ASSETS_DIR = BASE_DIR / "assets"

# Directorio de fuentes
FONTS_DIR = BASE_DIR / "fonts"
