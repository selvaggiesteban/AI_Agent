"""
matrices_to_html.py — Exporta las matrices CSV a documentos HTML sin estilos (una tabla por matriz).

Entradas (CSV, UTF-8):
  docs/Esteban/campana/campanas_resumen.csv          → campañas de e-mail
  docs/Esteban/campana/auditorias_seo_semanales.csv  → auditorías SEO semanales

Salidas (HTML, sin CSS/JS, celdas editables en el navegador):
  docs/campaigns.html
  docs/weekly-SEO.html

Uso: python matrices_to_html.py   (re-ejecutar cuando cambien los CSV)
"""

import csv
from html import escape
from pathlib import Path

AI_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = AI_ROOT / "docs" / "Esteban" / "campana"
OUT_DIR = AI_ROOT / "docs"

MATRICES = [
    {
        "csv": SRC_DIR / "campanas_resumen.csv",
        "out": OUT_DIR / "campaigns.html",
        "title": "Matriz de Campañas de E-mail",
        "lang": "Campañas (Título, Cobertura, Lista, Canal, Asunto, Fecha, Mensaje, Estado, métricas, Remitente, Programación)",
    },
    {
        "csv": SRC_DIR / "auditorias_seo_semanales.csv",
        "out": OUT_DIR / "weekly-SEO.html",
        "title": "Matriz de Auditorías SEO Semanales",
        "lang": "Auditorías SEO semanales (cobertura de indexación, sitemaps, GSC, CWV y acciones correctivas)",
    },
]

EMPTY_ROWS = 5  # filas vacías al final para seguir actualizando desde el navegador


def read_csv_rows(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        rows = [row for row in reader if any(cell.strip() for cell in row)]
    if not rows:
        raise SystemExit(f"CSV vacío: {path}")
    return rows[0], rows[1:]


def to_html(spec: dict) -> str:
    header, data = read_csv_rows(spec["csv"])

    th = "".join(f"<th>{escape(h)}</th>" for h in header)
    trs = []
    for row in data:
        row = row + [""] * (len(header) - len(row))
        tds = "".join(f'<td contenteditable="true">{escape(c)}</td>' for c in row[: len(header)])
        trs.append(f"<tr>{tds}</tr>")
    for _ in range(EMPTY_ROWS):
        tds = "".join('<td contenteditable="true">&nbsp;</td>' for _ in header)
        trs.append(f"<tr>{tds}</tr>")

    return (
        "<!DOCTYPE html>\n"
        '<html lang="es">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        f"  <title>{escape(spec['title'])}</title>\n"
        "</head>\n"
        "<body>\n"
        f"  <h1>{escape(spec['title'])}</h1>\n"
        f"  <p>{escape(spec['lang'])} — sin estilos. Editá las celdas en el navegador "
        "(contenteditable) y copiá los cambios al CSV correspondiente para conservarlos.</p>\n"
        '  <table border="1">\n'
        f"    <thead><tr>{th}</tr></thead>\n"
        "    <tbody>\n"
        + "".join(f"      {tr}\n" for tr in trs)
        + "    </tbody>\n"
        "  </table>\n"
        "</body>\n"
        "</html>\n"
    )


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for spec in MATRICES:
        html = to_html(spec)
        spec["out"].write_text(html, encoding="utf-8")
        header, data = read_csv_rows(spec["csv"])
        print(f"OK {spec['out']}  ({len(header)} columnas, {len(data)} filas + {EMPTY_ROWS} vacías)")


if __name__ == "__main__":
    main()
