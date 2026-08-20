from pathlib import Path
import os

# Detecta la raíz del proyecto dinámicamente basada en la ubicación de este archivo.
# Este archivo está en core/paths.py, por lo que la raíz es el padre del padre.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Definición de directorios principales para evitar rutas absolutas en el código
DATA_DIR = PROJECT_ROOT / "data"
INPUTS_DIR = DATA_DIR / "inputs"
OUTPUTS_DIR = PROJECT_ROOT / "outputs" if 'OUTPUT_ROOT' in locals() else DATA_DIR / "outputs"
LOGS_DIR = PROJECT_ROOT / "logs"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
CORE_DIR = PROJECT_ROOT / "core"
SKILLS_DIR = PROJECT_ROOT / "skills"

# Path to financial data CSV
FINANCIAL_DATA_PATH = Path(os.environ.get("FINANCIAL_DATA_PATH", r"C:\Users\Esteban Selvaggi\Desktop\Esteban\sesiones_consultoria_informatica.csv"))


def get_path(*args):
    """Utilidad para construir rutas relativas a la raíz del proyecto."""
    return PROJECT_ROOT.joinpath(*args)

# Para compatibilidad con scripts antiguos que esperan strings
PROJECT_ROOT_STR = str(PROJECT_ROOT)
