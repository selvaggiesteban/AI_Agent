"""
GSC Indexing Fixer — Automatización de IA para arreglar la indexación en Google Search Console.

Flujo (Perceive → Plan → Act → Evaluate) para TODOS los sitios de la cuenta
(selvaggi.esteban@gmail.com o la que devuelva la autenticación):

  1. Perceive:  sites.list → sitemaps.list → inspección URL homepage + URLs del sitemap.
  2. Plan:      clasifica cada URL (indexable / noindex / 404 / error servidor / etc.)
                y arma un plan de acción priorizado.
  3. Act:       (a) reenvía sitemaps con errores o pendientes;
                (b) solicita indexación (urlInspection.index) a las URLs elegibles,
                    respetando la cuota (~10-12 pedidos/día por propiedad).
  4. Evaluate:  genera reporte Markdown + JSON con "antes/después" y recomendaciones.

Uso:
  python gsc_indexing_fixer.py                  # modo real (pide indexación)
  python gsc_indexing_fixer.py --dry-run        # solo diagnóstico, sin enviar acciones
  python gsc_indexing_fixer.py --site https://example.com/   # un solo sitio
  python gsc_indexing_fixer.py --max-urls 50    # más URLs por sitio (default 25)
  python gsc_indexing_fixer.py --max-index-requests 8

Auth: OAuth del usuario (necesario para pedir indexación; el scope readonly no alcanza).
  - Primera ejecución: abre navegador para autorizar con selvaggi.esteban@gmail.com.
  - Client secret por defecto: docs/Esteban/campana/google/ (se usa el primero disponible)
    o la variable de entorno GSC_CLIENT_SECRET.
  - Token cacheado en token_gsc.json (al lado del script).
"""

import argparse
import json
import os
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import urlopen

try:
    import requests
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError as e:
    print(f"[ERROR] Faltan dependencias: {e}. Instalá: pip install google-api-python-client google-auth-oauthlib requests")
    sys.exit(1)

SCOPES = ["https://www.googleapis.com/auth/webmasters"]  # full: permite request indexing
SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
HERE = Path(__file__).resolve().parent
TOKEN_PATH = HERE / "token_gsc.json"
OUTPUT_DIR = HERE.parent.parent / "output"
DEFAULT_CLIENT_SECRET_DIR = HERE.parent.parent / "docs" / "Esteban" / "campana" / "google"

INDEXING_QUOTA_PER_SITE = 10
SLEEP_BETWEEN_INDEX_REQUESTS = 20  # segundos; Google limita ~2 pedidos/min
SITEMAP_HTTP_TIMEOUT = 15


# ─────────────────────────── AUTH ───────────────────────────

def find_client_secret() -> Path:
    env_path = os.getenv("GSC_CLIENT_SECRET")
    if env_path and Path(env_path).exists():
        return Path(env_path)
    if DEFAULT_CLIENT_SECRET_DIR.exists():
        candidates = sorted(DEFAULT_CLIENT_SECRET_DIR.glob("client_secret_*.json"))
        if candidates:
            return candidates[0]
    raise FileNotFoundError(
        "No se encontró client_secret de Google. Definí GSC_CLIENT_SECRET o colocá "
        f"un archivo client_secret_*.json en {DEFAULT_CLIENT_SECRET_DIR}"
    )


def get_credentials() -> Credentials:
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(str(find_client_secret()), SCOPES)
        creds = flow.run_local_server(port=0)
    TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")
    return creds


# ─────────────────────────── PERCEIVE ───────────────────────────

def list_sites(service):
    result = service.sites().list().execute()
    return [s["siteUrl"] for s in result.get("sites", [])]


def list_sitemaps(service, site):
    try:
        result = service.sitemaps().list(siteUrl=site).execute()
        return result.get("sitemap", [])
    except Exception as e:
        return [{"errors": f"list failed: {e}"}]


def fetch_sitemap_urls(site, limit):
    """Descarga el sitemap (o sitemap index) y devuelve hasta `limit` URLs."""
    urls = []
    to_visit = [urljoin(site, "/sitemap.xml")]
    visited = set()
    ns_strip = lambda tag: tag.split("}")[-1]

    while to_visit and len(urls) < limit:
        sm_url = to_visit.pop(0)
        if sm_url in visited:
            continue
        visited.add(sm_url)
        try:
            with urlopen(sm_url, timeout=SITEMAP_HTTP_TIMEOUT) as resp:
                root = ET.fromstring(resp.read())
        except Exception:
            continue
        for el in root:
            if ns_strip(el.tag) == "sitemap":
                loc = el.find("sm:loc", SITEMAP_NS)
                if loc is not None and loc.text:
                    to_visit.append(loc.text.strip())
            elif ns_strip(el.tag) == "url":
                loc = el.find("sm:loc", SITEMAP_NS)
                if loc is not None and loc.text:
                    urls.append(loc.text.strip())
                    if len(urls) >= limit:
                        break
    return urls


def inspect_url(service, url):
    body = {"inspectionUrl": url, "siteUrl": url.rsplit("/", 1)[0] + "/"}
    try:
        return service.urlInspection().index().inspect(body=body).execute()
    except Exception:
        # el siteUrl debe coincidir con la propiedad exacta (domain vs url-prefix)
        for candidate in (url.split("/")[0] + "//" + url.split("/")[2] + "/",):
            try:
                return service.urlInspection().index().inspect(
                    body={"inspectionUrl": url, "siteUrl": candidate}
                ).execute()
            except Exception:
                continue
    return None


def classify(inspection):
    """Devuelve (estado, accion, detalle) para una URL inspeccionada."""
    if not inspection:
        return ("desconocido", "reportar", "Inspección falló (verificar propiedad en GSC)")
    idx = inspection.get("indexStatusResult", {})
    coverage = (idx.get("coverageState") or "").lower()
    inspect_state = (idx.get("inspectionState") or "").lower()
    robots = (idx.get("robotsTxtState") or "").lower()
    fetch_state = (idx.get("pageFetchState") or "").upper()

    if "noindex" in coverage or robots == "noindex":
        return ("noindex", "ignorar", "Marcada noindex por diseño (ok si es intencional)")
    if fetch_state in ("4XX", "NOT_FOUND") or "not found" in coverage or "404" in coverage:
        return ("404", "arreglar_sitio", "URL rota: corregir redirect o quitar del sitemap")
    if fetch_state in ("5XX",) or "server error" in coverage:
        return ("error_5xx", "arreglar_sitio", "Error de servidor: revisar hosting/Cloudflare")
    if "redirect" in coverage:
        return ("redirect", "ignorar", "Redirección: asegurar que el destino esté canónico")
    if "not on google" in coverage or "no está en google" in coverage:
        if inspect_state == "eligible" or "eligible" in coverage:
            return ("indexable_no_indexada", "pedir_indexacion", "Elegible y no indexada → pedir indexación")
        return ("no_indexable", "reportar", "No indexable aún: revisar calidad/canonicalidad")
    if "duplicate" in coverage or "duplicada" in coverage:
        return ("duplicada", "ignorar", "Contenido duplicado: revisar canonical")
    if "indexed" in coverage:
        return ("indexada", "ok", "Ya está en Google")
    return ("otro", "reportar", f"Cobertura: {coverage or 'sin datos'}")


# ─────────────────────────── ACT ───────────────────────────

def submit_sitemap(service, site, sitemap_url):
    try:
        service.sitemaps().submit(siteUrl=site, feedpath=sitemap_url).execute()
        return True
    except Exception:
        return False


def request_indexing(service, url):
    body = {"inspectionUrl": url, "siteUrl": url.rsplit("/", 1)[0] + "/"}
    try:
        resp = service.urlInspection().index().submit(body=body).execute()
        return resp
    except Exception as e:
        return {"error": str(e)}


# ─────────────────────────── ORQUESTADOR ───────────────────────────

def process_site(service, site, max_urls, max_index_requests, dry_run, report):
    print(f"\n=== Sitio: {site} ===")
    site_report = {"site": site, "sitemaps": [], "urls": [], "acciones": []}

    # Sitemaps
    sitemaps = list_sitemaps(service, site)
    for sm in sitemaps:
        entry = {
            "path": sm.get("path"),
            "errors": sm.get("errors", 0),
            "warnings": sm.get("warnings", 0),
            "is_pending": sm.get("isPending", False),
            "last_submitted": sm.get("lastSubmitted"),
        }
        site_report["sitemaps"].append(entry)
        problematic = entry["errors"] > 0 or entry["is_pending"]
        if problematic and not dry_run:
            ok = submit_sitemap(service, site, entry["path"])
            site_report["acciones"].append(
                {"tipo": "reenviar_sitemap", "sitemap": entry["path"], "ok": ok}
            )
            print(f"  [sitemap] reenviado {entry['path']}: {'OK' if ok else 'FALLÓ'}")
        elif problematic:
            print(f"  [sitemap] PROBLEMA (dry-run): {entry['path']} errores={entry['errors']}")

    # Inspección homepage
    home = inspect_url(service, site)
    estado, accion, detalle = classify(home)
    print(f"  [home] {estado}: {detalle}")
    site_report["urls"].append({"url": site, "estado": estado, "detalle": detalle})

    # URLs del sitemap
    urls = fetch_sitemap_urls(site, max_urls)
    print(f"  URLs del sitemap a auditar: {len(urls)}")
    index_requests_left = 0 if dry_run else max_index_requests

    for url in urls:
        inspection = inspect_url(service, url)
        estado, accion, detalle = classify(inspection)
        site_report["urls"].append({"url": url, "estado": estado, "detalle": detalle})
        print(f"  [{estado}] {url}")

        if accion == "pedir_indexacion" and index_requests_left > 0:
            result = request_indexing(service, url)
            ok = "error" not in result
            site_report["acciones"].append(
                {"tipo": "pedir_indexacion", "url": url, "ok": ok, "resultado": result}
            )
            print(f"    → indexación solicitada: {'OK' if ok else result.get('error')}")
            index_requests_left -= 1
            time.sleep(SLEEP_BETWEEN_INDEX_REQUESTS)

    # Resumen por sitio
    counts = {}
    for u in site_report["urls"]:
        counts[u["estado"]] = counts.get(u["estado"], 0) + 1
    site_report["resumen"] = counts
    print(f"  Resumen: {counts}")
    report.append(site_report)
    return site_report


def write_reports(report, dry_run):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = "dryrun" if dry_run else "fix"

    json_path = OUTPUT_DIR / f"gsc_indexing_{suffix}_{stamp}.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [f"# Reporte de indexación GSC — {datetime.now():%d/%m/%Y %H:%M}",
          f"\nModo: {'DRY-RUN (solo diagnóstico)' if dry_run else 'CON ACCIONES'}\n"]
    for site_report in report:
        md.append(f"\n## {site_report['site']}")
        md.append(f"\n**Resumen:** {site_report.get('resumen', {})}")
        if site_report["sitemaps"]:
            md.append("\n### Sitemaps")
            for sm in site_report["sitemaps"]:
                md.append(f"- `{sm['path']}` — errores: {sm['errors']}, warnings: {sm['warnings']}, "
                          f"pendiente: {sm['is_pending']}")
        arreglar = [u for u in site_report["urls"] if u["estado"] in ("404", "error_5xx")]
        pedidas = [u for u in site_report["urls"] if u["estado"] == "indexable_no_indexada"]
        if pedidas:
            md.append(f"\n### Indexación solicitada / elegibles ({len(pedidas)})")
            for u in pedidas:
                md.append(f"- {u['url']}")
        if arreglar:
            md.append(f"\n### Requieren arreglo en el sitio ({len(arreglar)})")
            for u in arreglar:
                md.append(f"- `{u['estado']}` {u['url']} — {u['detalle']}")
        if site_report["acciones"]:
            md.append("\n### Acciones ejecutadas")
            for a in site_report["acciones"]:
                md.append(f"- {a['tipo']}: {a.get('url') or a.get('sitemap')} → "
                          f"{'OK' if a.get('ok') else 'FALLÓ'}")

    md.append("\n---\n**Recomendaciones generales (IA):**\n"
              "1. Priorizar URLs 404/5xx: arreglar en el sitio (redirect 301 o quitar del sitemap) y reenviar sitemap.\n"
              "2. Pedir indexación solo en páginas elegibles con contenido original (cuota limitada por día).\n"
              "3. Revisar noindex no intencionales en meta robots y header X-Robots-Tag.\n"
              "4. Re-ejecutar el script en 7 días para verificar el antes/después.")

    md_path = OUTPUT_DIR / f"gsc_indexing_{suffix}_{stamp}.md"
    md_path.write_text("\n".join(md), encoding="utf-8")
    print(f"\nReportes guardados:\n  - {json_path}\n  - {md_path}")


def main():
    parser = argparse.ArgumentParser(description="Arregla indexación en GSC de todos los sitios de la cuenta")
    parser.add_argument("--dry-run", action="store_true", help="Solo diagnosticar, no ejecutar acciones")
    parser.add_argument("--site", help="Procesar solo una propiedad (ej. https://lanuscomputacion.com/)")
    parser.add_argument("--max-urls", type=int, default=25, help="Máximo de URLs por sitio (default 25)")
    parser.add_argument("--max-index-requests", type=int, default=INDEXING_QUOTA_PER_SITE,
                        help="Máximo de pedidos de indexación por sitio (default 10)")
    args = parser.parse_args()

    print("Autenticando con Google…")
    creds = get_credentials()
    service = build("searchconsole", "v1", credentials=creds, cache_discovery=False)

    sites = [args.site] if args.site else list_sites(service)
    print(f"Sitios en la cuenta: {len(sites)}")

    report = []
    for site in sites:
        try:
            process_site(service, site, args.max_urls, args.max_index_requests, args.dry_run, report)
        except Exception as e:
            print(f"  [ERROR] {site}: {e}")
            report.append({"site": site, "error": str(e)})

    write_reports(report, args.dry_run)


if __name__ == "__main__":
    main()
