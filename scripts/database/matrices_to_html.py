"""
matrices_to_html.py — Exporta las matrices CSV a documentos HTML sin estilos (una tabla por matriz).

Entradas (CSV, UTF-8):
  docs/Esteban/campana/campanas_resumen.csv          → campañas de e-mail
  docs/Esteban/campana/auditorias_seo_semanales.csv  → auditorías SEO semanales

Salidas (HTML, fuente Open Sans vía Google Fonts, sin otros estilos, celdas editables
en el navegador):
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
        "filtro_estado": True,
    },
    {
        "csv": SRC_DIR / "auditorias_seo_semanales.csv",
        "out": OUT_DIR / "weekly-SEO.html",
        "title": "Matriz de Auditorías SEO Semanales",
        "lang": "Auditorías SEO semanales (cobertura de indexación, sitemaps, GSC, CWV y acciones correctivas)",
        "fragmento": SRC_DIR / "gsc_monthly_report.html",
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

    # Filtro por Estado (solo matrices habilitadas): <select> + script mínimo
    filtro_html, script_html = "", ""
    if spec.get("filtro_estado") and "Estado" in header:
        idx = header.index("Estado")
        estados, hay_vacias = [], False
        for row in data:
            val = row[idx].strip() if idx < len(row) else ""
            if val:
                if val not in estados:
                    estados.append(val)
            else:
                hay_vacias = True
        opciones = ['<option value="*">Todos</option>']
        opciones += [f'<option value="{escape(e, quote=True)}">{escape(e)}</option>' for e in estados]
        if hay_vacias:
            opciones.append('<option value="">(vacío)</option>')
        filtro_html = (
            '  <p><label for="filtro-estado">Filtrar por Estado: </label>\n'
            f'    <select id="filtro-estado" onchange="filtrarPorEstado(this)">'
            f'{"".join(opciones)}</select></p>\n'
        )
        script_html = (
            "  <script>\n"
            "    function filtrarPorEstado(sel) {\n"
            f"      var idx = {idx};\n"
            "      var v = sel.value;\n"
            '      var filas = document.querySelectorAll("#matriz tbody tr");\n'
            "      for (var i = 0; i < filas.length; i++) {\n"
            "        var e = filas[i].cells[idx].textContent.trim();\n"
            "        filas[i].style.display = (v === '*' || e === v) ? '' : 'none';\n"
            "      }\n"
            "    }\n"
            "  </script>\n"
        )

    # Sección extra (ej.: reporte mensual de GSC) inyectada desde un fragmento HTML
    fragmento = ""
    if spec.get("fragmento"):
        if spec["fragmento"].exists():
            fragmento = spec["fragmento"].read_text(encoding="utf-8")
            if fragmento and not fragmento.endswith("\n"):
                fragmento += "\n"
        else:
            fragmento = (
                "  <h2>Período de tiempo — por mes natural (Google Search Console)</h2>\n"
                "  <p>Sin datos todavía: ejecutá "
                "<code>python scripts/seo/gsc_monthly_report.py</code> "
                "(autoriza con Google en el navegador la primera vez) y regenerá este HTML con "
                "<code>python scripts/database/matrices_to_html.py</code>.</p>\n"
            )

    return (
        "<!DOCTYPE html>\n"
        '<html lang="es">\n'
        "<head>\n"
        '  <meta charset="utf-8">\n'
        f"  <title>{escape(spec['title'])}</title>\n"
        '  <link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '  <link href="https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300..800;1,300..800&display=swap" rel="stylesheet">\n'
        "  <style>body { font-family: 'Open Sans', Arial, sans-serif; }</style>\n"
        "</head>\n"
        "<body>\n"
        f"  <h1>{escape(spec['title'])}</h1>\n"
        f"  <p>{escape(spec['lang'])} — fuente Open Sans, sin otros estilos. Editá las celdas "
        "en el navegador (contenteditable) y copiá los cambios al CSV correspondiente para conservarlos.</p>\n"
        f"{filtro_html}"
        '  <table id="matriz" border="1">\n'
        f"    <thead><tr>{th}</tr></thead>\n"
        "    <tbody>\n"
        + "".join(f"      {tr}\n" for tr in trs)
        + "    </tbody>\n"
        "  </table>\n"
        f"{fragmento}"
        f"{script_html}"
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
