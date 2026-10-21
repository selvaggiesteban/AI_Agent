"""
matrices_fill.py — Preguntas almacenadas para rellenar y procesar las matrices CSV.

Pide cada columna como una pregunta (interactiva o por stdin piped), valida,
agrega la fila al CSV y regenera el HTML correspondiente con matrices_to_html.

Uso:
  python matrices_fill.py                              # menú interactivo
  python matrices_fill.py --matrix campaigns           # campañas de e-mail
  python matrices_fill.py --matrix weekly-seo          # auditorías SEO semanales
  python matrices_fill.py --matrix campaigns --dry-run # muestra la fila sin guardar

Matrices (CSV UTF-8, una fila por auditoría/campaña):
  docs/Esteban/campana/campanas_resumen.csv          → docs/campaigns.html
  docs/Esteban/campana/auditorias_seo_semanales.csv  → docs/weekly-SEO.html
"""

import argparse
import csv
import sys
from datetime import datetime
from pathlib import Path

AI_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = AI_ROOT / "docs" / "Esteban" / "campana"
DEFAULT_SENDER = "wwwlanuscomputacion@gmail.com"
HOY = datetime.now().strftime("%d/%m/%Y")

# ── PREGUNTAS ALMACENADAS (por matriz y columna) ──────────────────────────
# column → (pregunta, valor_por_defecto, tipo)  tipo: text | int | float
PREGUNTAS = {
    "campaigns": {
        "csv": SRC_DIR / "campanas_resumen.csv",
        "html": "docs/campaigns.html",
        "campos": {
            "Título": ("Título de la campaña", "", "text"),
            "Cobertura geográfica": ("Cobertura geográfica (ej. Nacional, AMBA)", "", "text"),
            "Lista": ("Lista de contactos (ej. NAC-OFERTAS-23102026)", "", "text"),
            "Canal": ("Canal", "E-mail", "text"),
            "Asunto": ("Asunto del e-mail", "", "text"),
            "Fecha": ("Fecha de envío (dd/mm/aaaa)", HOY, "text"),
            "Mensaje": ("Mensaje (preview del cuerpo)", "", "text"),
            "Estado": ("Estado (Pendiente / Planificada / Completada...)", "Pendiente", "text"),
            "Emails enviados": ("Emails enviados", "0", "int"),
            "Contactos únicos": ("Contactos únicos", "0", "int"),
            "Fallos": ("Fallos", "0", "int"),
            "Duración": ("Duración (hh:mm:ss)", "", "text"),
            "Cuentas usadas": ("Cuentas usadas", "0", "int"),
            "Enriched": ("Enriched (OK / Pendiente)", "Pendiente", "text"),
            "Log file": ("Log file (vacío si aún no existe)", "", "text"),
            "Remitente": ("Remitente Gmail", DEFAULT_SENDER, "text"),
            "Programación": ("Programación (dd/mm/aaaa hh:mm, vacío = sin programar)", "", "text"),
        },
    },
    "weekly-seo": {
        "csv": SRC_DIR / "auditorias_seo_semanales.csv",
        "html": "docs/weekly-SEO.html",
        "campos": {
            "Semana": ("Semana (ej. 42/2026)", "", "text"),
            "Fecha auditoría": ("Fecha de auditoría (dd/mm/aaaa)", HOY, "text"),
            "Sitio": ("Sitio (ej. https://lanuscomputacion.com/)", "", "text"),
            "Auditor": ("Auditor", "Esteban Selvaggi", "text"),
            "URLs revisadas": ("URLs revisadas", "0", "int"),
            "Indexadas": ("Indexadas", "0", "int"),
            "No indexadas": ("No indexadas", "0", "int"),
            "Errores 404": ("Errores 404", "0", "int"),
            "Errores 5xx": ("Errores 5xx", "0", "int"),
            "Sitemaps con errores": ("Sitemaps con errores", "0", "int"),
            "Clicks": ("Clicks (GSC)", "0", "int"),
            "Impresiones": ("Impresiones (GSC)", "0", "int"),
            "CTR": ("CTR (ej. 1,23%)", "0,00%", "text"),
            "Posición promedio": ("Posición promedio (GSC)", "0", "float"),
            "CWV Good %": ("Core Web Vitals Good %", "0", "float"),
            "Acciones correctivas": ("Acciones correctivas (qué se arregló)", "", "text"),
            "Estado": ("Estado (Pendiente / Completada)", "Pendiente", "text"),
            "Log file": ("Log file / evidencia", "", "text"),
        },
    },
}


def preguntar(nombre, pregunta, default, tipo):
    """Una pregunta por columna; stdin interactivo o piped. Devuelve el valor validado."""
    prompt = f"  {pregunta}" + (f" [{default}]" if default != "" else "") + ": "
    try:
        raw = input(prompt)
    except EOFError:
        raw = ""
    valor = raw.strip() or (default if default != "" else "")
    if valor == "" and default == "" and nombre in ("Título", "Sitio", "Semana", "Lista", "Asunto"):
        print(f"    ⚠ '{nombre}' es obligatorio.")
        return preguntar(nombre, pregunta, default, tipo)
    if tipo == "int":
        limpio = valor.replace(".", "")
        if limpio == "":
            limpio = "0"
        try:
            int(limpio)
            return limpio
        except ValueError:
            print(f"    ⚠ Se espera un número entero, se usa 0.")
            return "0"
    if tipo == "float":
        if valor == "":
            return "0"
        try:
            float(valor.replace(",", "."))
            return valor
        except ValueError:
            print(f"    ⚠ Se espera un número, se usa 0.")
            return "0"
    return valor


def procesar(matrix_key, dry_run):
    spec = PREGUNTAS[matrix_key]
    csv_path: Path = spec["csv"]
    campos = spec["campos"]

    with csv_path.open(encoding="utf-8-sig", newline="") as f:
        header = next(csv.reader(f))

    faltantes = [c for c in header if c not in campos]
    if faltantes:
        raise SystemExit(f"[ERROR] Columnas del CSV sin pregunta definida: {faltantes}")

    print(f"\n=== Rellenando matriz: {matrix_key} ({len(header)} columnas) ===")
    print(f"CSV: {csv_path}\n")
    fila = []
    for col in header:
        pregunta, default, tipo = campos[col]
        fila.append(preguntar(col, pregunta, default, tipo))

    print("\n--- Fila procesada ---")
    for col, val in zip(header, fila):
        print(f"  {col}: {val}")

    if dry_run:
        print("\n[DRY-RUN] No se guardó nada (CSV y HTML sin cambios).")
        return

    with csv_path.open("a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow(fila)
    print(f"\n✔ Fila agregada a {csv_path}")

    import matrices_to_html
    matrices_to_html.main()
    print(f"✔ HTML regenerado: {spec['html']}")


def main():
    parser = argparse.ArgumentParser(description="Rellena matrices CSV con preguntas y regenera los HTML")
    parser.add_argument("--matrix", choices=list(PREGUNTAS), help="Matriz a rellenar")
    parser.add_argument("--dry-run", action="store_true", help="Solo muestra la fila, no guarda")
    args = parser.parse_args()

    key = args.matrix
    if not key:
        print("Elegí la matriz:")
        for i, k in enumerate(PREGUNTAS, 1):
            print(f"  {i}) {k}")
        try:
            choice = input("> ").strip()
        except EOFError:
            choice = ""
        key = list(PREGUNTAS)[int(choice) - 1] if choice.isdigit() and 0 < int(choice) <= len(PREGUNTAS) else None
        if not key:
            raise SystemExit("Opción inválida.")

    procesar(key, args.dry_run)


if __name__ == "__main__":
    main()
