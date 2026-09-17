from pathlib import Path
import os

# Dynamically detect the project root based on the location of this file.
# This file is in core/paths.py, so the root is the parent of the parent.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Definition of main directories to avoid absolute paths in the code
DATA_DIR = PROJECT_ROOT / "data"
INPUTS_DIR = DATA_DIR / "inputs"
OUTPUTS_DIR = PROJECT_ROOT / "outputs" if 'OUTPUT_ROOT' in locals() else DATA_DIR / "outputs"
LOGS_DIR = PROJECT_ROOT / "logs"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
CORE_DIR = PROJECT_ROOT / "core"
SKILLS_DIR = PROJECT_ROOT / "skills"

# Path to financial data CSV
FINANCIAL_DATA_PATH = Path(os.environ.get("FINANCIAL_DATA_PATH", DATA_DIR / "financials.csv"))


def get_path(*args):
    """Utility to build paths relative to the project root."""
    return PROJECT_ROOT.joinpath(*args)

# For compatibility with old scripts that expect strings
PROJECT_ROOT_STR = str(PROJECT_ROOT)
