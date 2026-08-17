# Copyright (C) 2025 Esteban Selvaggi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Services Pipeline — Orquestador del ciclo de vida del cliente.

Fases:
  1. Contrato    — Genera contrato desde datos de DB
  2. Setup Web   — Landing / Astro / MedusaJS
  3. SEO         — Análisis + contenido (stub GSC/GA)
  4. Ads         — Google Ads + Meta Ads (stub)
  5. Contenido   — Canva / assets visuales (stub)
  6. Entrega     — Screenshots + paquete
  7. Seguimiento — Trello + Calendar + Meet
  8. Financiero  — Wrapper accountly
  9. Telemetry   — Logs JSON transversales

Uso:
  python -m core.services --all --cliente "Pablo"
  python -m core.services --contrato --cliente "Kevin"
  python -m core.services --setup_web landing --cliente "Mora"
  python -m core.services --seo --mode analyze --cliente "Esteban"
  python -m core.services --ads --platform google --cliente "Pablo"
  python -m core.services --entregar --cliente "Pablo"
  python -m core.services --seguimiento --cliente "Pablo"
  python -m core.services --financiero
  python -m core.services --status
  python -m core.services --all --dry-run --cliente "Test"
"""

import sys
import os
import json
import sqlite3
import shutil
import subprocess
import logging
import csv
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from core.config import (
    DB_PATH,
    DATA_OUTPUTS_DIR,
    LOG_EXECUTION_DIR,
    GOOGLE_CREDS_DIR,
    TRELLO_API_KEY,
    TRELLO_TOKEN,
    GEMINI_API_KEY,
)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_DIR = ROOT_DIR / "logs" / "pipeline"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("services")
logger.setLevel(logging.INFO)

_console = logging.StreamHandler()
_console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S"))
logger.addHandler(_console)

_file_handler = logging.FileHandler(LOG_DIR / "services.log", encoding="utf-8")
_file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(_file_handler)


# ---------------------------------------------------------------------------
# Telemetry helper
# ---------------------------------------------------------------------------
TELEMETRY_PATH = LOG_DIR / "services_execution_log.json"


def _load_telemetry() -> List[Dict]:
    if TELEMETRY_PATH.exists():
        try:
            return json.loads(TELEMETRY_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []


def _save_telemetry(entries: List[Dict]) -> None:
    TELEMETRY_PATH.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")


def _log_event(event_type: str, cliente: str, detail: Dict[str, Any]) -> None:
    entries = _load_telemetry()
    entries.append({
        "ts": datetime.now().isoformat(),
        "pipeline": "services",
        "event": event_type,
        "cliente": cliente,
        **detail,
    })
    _save_telemetry(entries)
    logger.info("Telemetry: %s — %s", event_type, cliente)


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def _db_query(query: str, params: tuple = (), fetch: bool = True) -> list:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        if fetch:
            return [dict(row) for row in cur.fetchall()]
        conn.commit()
        return []
    finally:
        conn.close()


def _get_cliente_data(cliente: str) -> Optional[Dict]:
    rows = _db_query(
        "SELECT * FROM main WHERE title LIKE ? OR primary_email LIKE ? LIMIT 1",
        (f"%{cliente}%", f"%{cliente}%"),
    )
    return rows[0] if rows else None


# ---------------------------------------------------------------------------
# Phase 1: Contrato
# ---------------------------------------------------------------------------

def phase_contrato(cliente: str, dry_run: bool = False) -> Dict:
    logger.info("=== FASE 1: Contrato — %s ===", cliente)
    data = _get_cliente_data(cliente)
    if not data:
        logger.warning("Cliente '%s' no encontrado en DB. Se usa modo genérico.", cliente)
        data = {"title": cliente, "primary_email": "", "phone": "", "address": "", "sector": ""}

    template_path = ROOT_DIR / "scripts" / "templates" / "contrato_prestacion_servicios.md"
    if not template_path.exists():
        logger.error("Plantilla de contrato no encontrada: %s", template_path)
        return {"ok": False, "error": "template_missing"}

    template = template_path.read_text(encoding="utf-8")

    # Rellenar campos del CONTRATANTE desde DB
    nombre = data.get("title", cliente)
    domicilio = data.get("address", "")
    email = data.get("primary_email", "")
    telefono = data.get("phone", "")
    ciudad = data.get("city", "")
    provincia = data.get("province", "")
    sector = data.get("sector", "")

    template = template.replace(
        "CONTRATANTE: ..........................................................",
        f"CONTRATANTE: {nombre}",
    )
    template = template.replace(
        "D.N.I. ...................................",
        f"D.N.I. [COMPLETAR — datos no disponibles en DB]",
    )
    template = template.replace(
        "CUIT/CUIL ...................................",
        f"CUIT/CUIL [COMPLETAR — datos no disponibles en DB]",
    )
    template = template.replace(
        "con domicilio en .........................................................., en adelante",
        f"con domicilio en {domicilio or '[COMPLETAR]'}, en adelante",
    )
    # Fill date
    from datetime import datetime
    today = datetime.now()
    template = template.replace(
        "a los ....... días del mes de ........................... de 20....",
        f"a los {today.day} días del mes de {today.strftime('%B')} de {today.year}",
    )
    # Fill Anexo I with sector info if available
    if sector:
        template = template.replace(
            "Descripción del proyecto:\n> .................................................................................",
            f"Descripción del proyecto:\n> Servicios de {sector.lower()} para {nombre}",
        )

    # Add contact info as comment at the end
    contact_info = f"\n\n---\n> **Datos de contacto del CONTRATANTE (extraídos de DB):**\n"
    if email:
        contact_info += f"> - Email: {email}\n"
    if telefono:
        contact_info += f"> - Teléfono: {telefono}\n"
    if ciudad:
        contact_info += f"> - Ciudad: {ciudad}\n"
    if provincia:
        contact_info += f"> - Provincia: {provincia}\n"
    contact_info += f"> - Sector: {sector or 'No especificado'}\n"
    contact_info += "> - **NOTA:** DNI y CUIT deben ser completados por el cliente antes de firmar.\n"
    template += contact_info

    out_dir = DATA_OUTPUTS_DIR / "contratos"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = cliente.lower().replace(" ", "_").replace(".", "")
    out_path = out_dir / f"{slug}_contrato.md"

    if dry_run:
        logger.info("[DRY-RUN] Contrato generado para: %s", cliente)
        return {"ok": True, "path": str(out_path), "dry_run": True}

    out_path.write_text(template, encoding="utf-8")
    logger.info("Contrato generado: %s", out_path)
    _log_event("contrato", cliente, {"path": str(out_path)})
    return {"ok": True, "path": str(out_path)}


# ---------------------------------------------------------------------------
# Phase 2: Setup Web
# ---------------------------------------------------------------------------

def _setup_landing(cliente: str, data: Dict, dry_run: bool) -> Dict:
    logger.info("  → Setup Landing Page para %s", cliente)

    landing_gen = ROOT_DIR / "scripts" / "web_designer" / "landing-page-generator" / "landing-page-generator.py"
    if not landing_gen.exists():
        logger.error("landing-page-generator.py no encontrado")
        return {"ok": False, "error": "script_missing"}

    out_dir = DATA_OUTPUTS_DIR / "landing" / cliente.lower().replace(" ", "_")
    out_dir.mkdir(parents=True, exist_ok=True)

    if dry_run:
        logger.info("  [DRY-RUN] Landing page would be generated for %s", cliente)
        return {"ok": True, "dry_run": True}

    # Copy the template and inject client data via a brief file
    brief_path = out_dir / "brief.json"
    brief = {
        "title": data.get("title", cliente),
        "category": data.get("sector", ""),
        "phone": data.get("phone", ""),
        "address": data.get("address", ""),
        "city": data.get("city", ""),
        "website": (data.get("urls") or "").split(",")[0].strip() if data.get("urls") else "",
    }
    brief_path.write_text(json.dumps(brief, indent=2, ensure_ascii=False), encoding="utf-8")

    # Invoke landing-page-generator with the brief
    try:
        result = subprocess.run(
            [sys.executable, str(landing_gen), "--brief", str(brief_path), "--output", str(out_dir)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(ROOT_DIR),
        )
        if result.returncode != 0:
            logger.warning("  landing-page-generator warnings: %s", result.stderr[:500])
        logger.info("  Landing page generada en: %s", out_dir)
        _log_event("setup_landing", cliente, {"path": str(out_dir)})
        return {"ok": True, "path": str(out_dir)}
    except subprocess.TimeoutExpired:
        logger.error("  Timeout ejecutando landing-page-generator")
        return {"ok": False, "error": "timeout"}
    except Exception as e:
        logger.error("  Error ejecutando landing-page-generator: %s", e)
        return {"ok": False, "error": str(e)}


def _setup_astro(cliente: str, data: Dict, dry_run: bool) -> Dict:
    logger.info("  → Setup Sitio Astro para %s", cliente)
    template_dir = ROOT_DIR / "scripts" / "web_designer" / "example"
    if not template_dir.exists():
        logger.error("Template Astro no encontrado en %s", template_dir)
        return {"ok": False, "error": "template_missing"}

    slug = cliente.lower().replace(" ", "_")
    out_dir = DATA_OUTPUTS_DIR / "sites" / slug

    if dry_run:
        logger.info("  [DRY-RUN] Sitio Astro would be cloned for %s", cliente)
        return {"ok": True, "dry_run": True}

    if out_dir.exists():
        logger.info("  Directorio ya existe: %s — se omite clonado", out_dir)
    else:
        shutil.copytree(template_dir, out_dir, ignore=shutil.ignore_patterns("node_modules", ".astro", "dist"))
        logger.info("  Template Astro clonado en: %s", out_dir)

    # Personalizar content
    content_dir = out_dir / "src" / "content" / "blog"
    if content_dir.exists():
        brief = {
            "title": data.get("title", cliente),
            "sector": data.get("sector", ""),
            "phone": data.get("phone", ""),
        }
        (out_dir / "brief.json").write_text(json.dumps(brief, indent=2, ensure_ascii=False), encoding="utf-8")

    _log_event("setup_astro", cliente, {"path": str(out_dir)})
    return {"ok": True, "path": str(out_dir)}


def _setup_medusa(cliente: str, data: Dict, dry_run: bool) -> Dict:
    logger.info("  → Setup MedusaJS para %s", cliente)
    slug = cliente.lower().replace(" ", "_")
    out_dir = DATA_OUTPUTS_DIR / "stores" / slug

    if dry_run:
        logger.info("  [DRY-RUN] MedusaJS would be scaffolded for %s", cliente)
        return {"ok": True, "dry_run": True}

    if out_dir.exists():
        logger.info("  Directorio MedusaJS ya existe: %s", out_dir)
        return {"ok": True, "path": str(out_dir), "note": "already_exists"}

    try:
        result = subprocess.run(
            ["npx", "create-medusa-app@latest", str(out_dir), "--skip-db"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=str(ROOT_DIR),
        )
        if result.returncode != 0:
            logger.error("  Error scaffolding MedusaJS: %s", result.stderr[:500])
            return {"ok": False, "error": result.stderr[:500]}

        logger.info("  MedusaJS scaffoldered en: %s", out_dir)
        _log_event("setup_medusa", cliente, {"path": str(out_dir)})
        return {"ok": True, "path": str(out_dir)}
    except subprocess.TimeoutExpired:
        logger.error("  Timeout scaffolding MedusaJS")
        return {"ok": False, "error": "timeout"}
    except FileNotFoundError:
        logger.error("  npx no encontrado. Instalá Node.js primero.")
        return {"ok": False, "error": "npx_not_found"}


def phase_setup_web(cliente: str, web_type: str = "landing", dry_run: bool = False) -> Dict:
    logger.info("=== FASE 2: Setup Web (%s) — %s ===", web_type, cliente)
    data = _get_cliente_data(cliente) or {"title": cliente}

    if web_type == "landing":
        return _setup_landing(cliente, data, dry_run)
    elif web_type == "astro":
        return _setup_astro(cliente, data, dry_run)
    elif web_type == "medusa":
        return _setup_medusa(cliente, data, dry_run)
    else:
        logger.error("Tipo de sitio desconocido: %s", web_type)
        return {"ok": False, "error": f"unknown_type:{web_type}"}


# ---------------------------------------------------------------------------
# Phase 3: SEO
# ---------------------------------------------------------------------------

def phase_seo(cliente: str, mode: str = "content", dry_run: bool = False) -> Dict:
    logger.info("=== FASE 3: SEO (%s) — %s ===", mode, cliente)
    data = _get_cliente_data(cliente) or {"title": cliente, "urls": ""}

    seo_gen = ROOT_DIR / "scripts" / "seo_manager" / "seo-content-generator" / "seo_content_generator.py"
    if not seo_gen.exists():
        logger.error("seo_content_generator.py no encontrado")
        return {"ok": False, "error": "script_missing"}

    out_dir = DATA_OUTPUTS_DIR / "seo" / cliente.lower().replace(" ", "_")
    out_dir.mkdir(parents=True, exist_ok=True)

    if dry_run:
        logger.info("  [DRY-RUN] SEO analysis would run for %s", cliente)
        return {"ok": True, "dry_run": True}

    site_url = (data.get("urls") or "").split(",")[0].strip() if data.get("urls") else ""

    if mode == "analyze" and site_url:
        # Existing site mode
        try:
            result = subprocess.run(
                [
                    sys.executable, str(seo_gen),
                    "--urls", site_url,
                    "--output", str(out_dir / "reporte.md"),
                    "--excel", str(out_dir / "reporte.xlsx"),
                ],
                capture_output=True,
                text=True,
                timeout=600,
                cwd=str(ROOT_DIR),
            )
            if result.returncode != 0:
                logger.warning("  SEO analyzer warnings: %s", result.stderr[:500])
            _log_event("seo_analyze", cliente, {"path": str(out_dir), "url": site_url})
            return {"ok": True, "path": str(out_dir)}
        except subprocess.TimeoutExpired:
            logger.error("  Timeout en SEO analyzer")
            return {"ok": False, "error": "timeout"}
    else:
        # New site mode — generate content plan
        logger.info("  Modo contenido SEO (stub — requiere brief del cliente)")
        _log_event("seo_content", cliente, {"mode": "content", "path": str(out_dir)})
        return {"ok": True, "path": str(out_dir), "note": "stub_requires_brief"}


# ---------------------------------------------------------------------------
# Phase 4: Ads
# ---------------------------------------------------------------------------

def phase_ads(cliente: str, platform: str = "google", dry_run: bool = False) -> Dict:
    logger.info("=== FASE 4: Ads (%s) — %s ===", platform, cliente)
    data = _get_cliente_data(cliente) or {"title": cliente, "urls": ""}

    out_dir = DATA_OUTPUTS_DIR / "ads" / cliente.lower().replace(" ", "_")
    out_dir.mkdir(parents=True, exist_ok=True)

    if dry_run:
        logger.info("  [DRY-RUN] Ads strategy would be generated for %s on %s", cliente, platform)
        return {"ok": True, "dry_run": True}

    if platform == "google":
        ads_strat = ROOT_DIR / "scripts" / "ads_manager" / "ads_strategist.py"
        if not ads_strat.exists():
            logger.error("ads_strategist.py no encontrado")
            return {"ok": False, "error": "script_missing"}

        site_url = (data.get("urls") or "").split(",")[0].strip() if data.get("urls") else ""
        if not site_url:
            logger.warning("  No se encontró URL del sitio para %s", cliente)
            return {"ok": False, "error": "no_site_url"}

        try:
            result = subprocess.run(
                [sys.executable, str(ads_strat), site_url, "--output", str(out_dir)],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(ROOT_DIR),
            )
            if result.returncode != 0:
                logger.warning("  Ads strategist warnings: %s", result.stderr[:500])
            _log_event("ads_google", cliente, {"path": str(out_dir), "url": site_url})
            return {"ok": True, "path": str(out_dir)}
        except subprocess.TimeoutExpired:
            logger.error("  Timeout en ads_strategist")
            return {"ok": False, "error": "timeout"}

    elif platform == "meta":
        # Meta Ads stub — requiere facebook-business SDK + credenciales
        logger.info("  Meta Ads stub — requiere facebook-business SDK y credenciales de Meta")
        _log_event("ads_meta_stub", cliente, {"path": str(out_dir)})
        return {"ok": True, "path": str(out_dir), "note": "stub_requires_meta_credentials"}

    else:
        logger.error("Plataforma desconocida: %s", platform)
        return {"ok": False, "error": f"unknown_platform:{platform}"}


# ---------------------------------------------------------------------------
# Phase 5: Contenido Audiovisual
# ---------------------------------------------------------------------------

def phase_contenido(cliente: str, dry_run: bool = False) -> Dict:
    logger.info("=== FASE 5: Contenido Audiovisual — %s ===", cliente)
    data = _get_cliente_data(cliente) or {"title": cliente}

    out_dir = DATA_OUTPUTS_DIR / "content" / cliente.lower().replace(" ", "_")
    out_dir.mkdir(parents=True, exist_ok=True)

    if dry_run:
        logger.info("  [DRY-RUN] Content assets would be generated for %s", cliente)
        return {"ok": True, "dry_run": True}

    # Canva stub — requiere Canva Connect API (beta)
    logger.info("  Canva stub — requiere Canva Connect API")
    brief = {
        "cliente": data.get("title", cliente),
        "sector": data.get("sector", ""),
        "colores": "por definir",
        "estilo": "profesional",
    }
    (out_dir / "brief_contenido.json").write_text(
        json.dumps(brief, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    _log_event("contenido_stub", cliente, {"path": str(out_dir)})
    return {"ok": True, "path": str(out_dir), "note": "stub_requires_canva"}


# ---------------------------------------------------------------------------
# Phase 6: Entrega
# ---------------------------------------------------------------------------

def phase_entregar(cliente: str, dry_run: bool = False) -> Dict:
    logger.info("=== FASE 6: Entrega — %s ===", cliente)
    data = _get_cliente_data(cliente) or {"title": cliente, "urls": ""}

    slug = cliente.lower().replace(" ", "_")
    delivery_dir = DATA_OUTPUTS_DIR / "deliveries" / slug
    delivery_dir.mkdir(parents=True, exist_ok=True)

    if dry_run:
        logger.info("  [DRY-RUN] Delivery package would be created for %s", cliente)
        return {"ok": True, "dry_run": True}

    # 1. Screenshots
    screenshot_script = ROOT_DIR / "scripts" / "graphic_designer" / "web-screenshot" / "web_screenshots.py"
    site_url = (data.get("urls") or "").split(",")[0].strip() if data.get("urls") else ""

    screenshots_dir = delivery_dir / "screenshots"
    screenshots_dir.mkdir(exist_ok=True)

    if site_url and screenshot_script.exists():
        logger.info("  Tomando screenshots de %s ...", site_url)
        try:
            # Import the function directly
            import importlib.util
            spec = importlib.util.spec_from_file_location("web_screenshots", str(screenshot_script))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            for viewport in ["desktop", "tablet", "mobile"]:
                fname = screenshots_dir / f"{slug}_{viewport}.png"
                mod.take_screenshot(site_url, viewport, str(fname))
            logger.info("  Screenshots completados")
        except Exception as e:
            logger.warning("  Error tomando screenshots: %s", e)
    else:
        logger.info("  Sin URL de sitio o script de screenshots no disponible — se omite")

    # 2. Copiar contrato si existe
    contrato_src = DATA_OUTPUTS_DIR / "contratos" / f"{slug}_contrato.md"
    if contrato_src.exists():
        shutil.copy2(contrato_src, delivery_dir / "contrato.md")
        logger.info("  Contrato copiado al paquete de entrega")

    # 3. Copiar reporte SEO si existe
    seo_src = DATA_OUTPUTS_DIR / "seo" / slug
    if seo_src.exists():
        shutil.copytree(seo_src, delivery_dir / "seo", dirs_exist_ok=True)
        logger.info("  Reporte SEO copiado al paquete de entrega")

    # 4. Crear instructivo básico
    instructivo = f"""# Instructivo de Uso — {data.get('title', cliente)}

## Credenciales
(completar con credenciales reales del sitio)

## Acceso al Sitio
- URL: {site_url or 'pendiente'}
- Panel de administración: (completar)

## Próximos Pasos
1. Revisar el sitio entregado
2. Solicitar cambios si es necesario (30 días de garantía)
3. Confirmar aceptación formal
"""
    (delivery_dir / "instructivo_uso.md").write_text(instructivo, encoding="utf-8")

    _log_event("entrega", cliente, {"path": str(delivery_dir), "url": site_url})
    logger.info("  Paquete de entrega listo: %s", delivery_dir)
    return {"ok": True, "path": str(delivery_dir)}


# ---------------------------------------------------------------------------
# Phase 7: Seguimiento (Trello + Calendar + Meet)
# ---------------------------------------------------------------------------

def phase_seguimiento(cliente: str, dry_run: bool = False) -> Dict:
    logger.info("=== FASE 7: Seguimiento — %s ===", cliente)
    data = _get_cliente_data(cliente) or {"title": cliente}

    if dry_run:
        logger.info("  [DRY-RUN] Seguimiento would be created for %s", cliente)
        return {"ok": True, "dry_run": True}

    results = {}

    # --- Trello ---
    if TRELLO_API_KEY and TRELLO_TOKEN and TRELLO_API_KEY != "YOUR_TRELLO_API_KEY":
        try:
            import requests as req

            base = "https://api.trello.com/1"
            auth = {"key": TRELLO_API_KEY, "token": TRELLO_TOKEN}

            # Find board
            boards_resp = req.get(f"{base}/members/me/boards", params=auth, timeout=15)
            boards_resp.raise_for_status()
            boards = boards_resp.json()

            board_id = None
            for b in boards:
                if "marketing" in b.get("name", "").lower() or "proyectos" in b.get("name", "").lower():
                    board_id = b["id"]
                    break
            if not board_id and boards:
                board_id = boards[0]["id"]

            if board_id:
                # Get lists
                lists_resp = req.get(f"{base}/boards/{board_id}/lists", params=auth, timeout=15)
                lists_resp.raise_for_status()
                lists = lists_resp.json()

                pending_id = None
                for lst in lists:
                    if "pendiente" in lst.get("name", "").lower() or "todo" in lst.get("name", "").lower():
                        pending_id = lst["id"]
                        break
                if not pending_id and lists:
                    pending_id = lists[0]["id"]

                if pending_id:
                    card_data = {
                        **auth,
                        "idList": pending_id,
                        "name": f"Seguimiento — {data.get('title', cliente)}",
                        "desc": f"Cliente: {data.get('title', cliente)}\nEmail: {data.get('primary_email', '')}\nTel: {data.get('phone', '')}",
                    }
                    card_resp = req.post(f"{base}/cards", data=card_data, timeout=15)
                    card_resp.raise_for_status()
                    card = card_resp.json()
                    results["trello"] = {"ok": True, "card_id": card["id"], "url": card.get("shortUrl")}
                    logger.info("  Trello card creada: %s", card.get("shortUrl"))
                else:
                    results["trello"] = {"ok": False, "error": "no_list_found"}
            else:
                results["trello"] = {"ok": False, "error": "no_board_found"}
        except Exception as e:
            results["trello"] = {"ok": False, "error": str(e)}
            logger.warning("  Error Trello: %s", e)
    else:
        results["trello"] = {"ok": False, "error": "credentials_missing"}
        logger.info("  Trello: credenciales no configuradas")

    # --- Google Calendar + Meet ---
    try:
        token_pickle = GOOGLE_CREDS_DIR / "token.pickle"
        client_secret = GOOGLE_CREDS_DIR / "client_secret.json"

        if token_pickle.exists() and client_secret.exists():
            from google.auth.transport.requests import Request
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            import pickle

            SCOPES = ["https://www.googleapis.com/auth/calendar"]
            creds = None
            with open(token_pickle, "rb") as f:
                creds = pickle.load(f)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(str(client_secret), SCOPES)
                    creds = flow.run_local_server(port=0)
                with open(token_pickle, "wb") as f:
                    pickle.dump(creds, f)

            service = build("calendar", "v3", credentials=creds)

            now = datetime.now()
            event = {
                "summary": f"Reunión — {data.get('title', cliente)}",
                "description": f"Seguimiento con {data.get('title', cliente)}\nEmail: {data.get('primary_email', '')}",
                "start": {
                    "dateTime": (now + timedelta(days=1)).replace(hour=10, minute=0, second=0).isoformat(),
                    "timeZone": "America/Argentina/Buenos_Aires",
                },
                "end": {
                    "dateTime": (now + timedelta(days=1)).replace(hour=11, minute=0, second=0).isoformat(),
                    "timeZone": "America/Argentina/Buenos_Aires",
                },
                "conferenceData": {
                    "createRequest": {
                        "requestId": f"meet-{slug}-{int(now.timestamp())}",
                        "conferenceSolutionKey": {"type": "hangoutsMeet"},
                    }
                },
            }

            created = service.events().insert(
                calendarId="primary",
                body=event,
                conferenceDataVersion=1,
            ).execute()

            meet_link = created.get("conferenceData", {}).get("entryPoints", [{}])[0].get("uri", "")
            results["calendar"] = {"ok": True, "event_id": created["id"], "meet_link": meet_link}
            logger.info("  Calendar event creado con Meet link: %s", meet_link)
        else:
            results["calendar"] = {"ok": False, "error": "credentials_missing"}
            logger.info("  Calendar: credenciales no configuradas")
    except Exception as e:
        results["calendar"] = {"ok": False, "error": str(e)}
        logger.warning("  Error Calendar: %s", e)

    _log_event("seguimiento", cliente, results)
    return results


# ---------------------------------------------------------------------------
# Phase 8: Financiero
# ---------------------------------------------------------------------------

def phase_financiero(dry_run: bool = False) -> Dict:
    logger.info("=== FASE 8: Dashboard Financiero ===")

    if dry_run:
        logger.info("  [DRY-RUN] Financial dashboard would be generated")
        return {"ok": True, "dry_run": True}

    accountly_main = ROOT_DIR / "scripts" / "financial_manager" / "accountly" / "main.py"
    if not accountly_main.exists():
        logger.error("accountly/main.py no encontrado")
        return {"ok": False, "error": "script_missing"}

    try:
        result = subprocess.run(
            [sys.executable, str(accountly_main)],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(accountly_main.parent),
        )
        if result.returncode != 0:
            logger.warning("  Accountly warnings: %s", result.stderr[:500])
        _log_event("financiero", "global", {})
        logger.info("  Dashboard financiero generado")
        return {"ok": True}
    except subprocess.TimeoutExpired:
        logger.error("  Timeout ejecutando accountly")
        return {"ok": False, "error": "timeout"}


# ---------------------------------------------------------------------------
# Phase 9: Status (resumen de todos los clientes)
# ---------------------------------------------------------------------------

def phase_status() -> Dict:
    logger.info("=== FASE 9: Status ===")

    telemetry = _load_telemetry()
    if not telemetry:
        logger.info("  Sin datos de telemetría aún")
        return {"ok": True, "entries": 0}

    # Agrupar por cliente
    clientes = {}
    for entry in telemetry:
        c = entry.get("cliente", "unknown")
        if c not in clientes:
            clientes[c] = []
        clientes[c].append(entry)

    logger.info("  Clientes en telemetría: %d", len(clientes))
    for c, events in clientes.items():
        logger.info("    %s: %d eventos", c, len(events))

    return {"ok": True, "clientes": len(clientes), "total_events": len(telemetry)}


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def run_pipeline(
    cliente: str,
    do_all: bool = False,
    do_contrato: bool = False,
    setup_web: Optional[str] = None,
    do_seo: bool = False,
    seo_mode: str = "content",
    do_ads: bool = False,
    ads_platform: str = "google",
    do_contenido: bool = False,
    do_entregar: bool = False,
    do_seguimiento: bool = False,
    do_financiero: bool = False,
    do_status: bool = False,
    dry_run: bool = False,
) -> Dict:
    results = {}
    start = datetime.now()
    logger.info("Pipeline Services iniciado para cliente: %s", cliente or "(global)")

    try:
        if do_status:
            results["status"] = phase_status()

        if do_all or do_contrato:
            results["contrato"] = phase_contrato(cliente, dry_run)

        if do_all or setup_web:
            web_type = setup_web if setup_web else "landing"
            results["setup_web"] = phase_setup_web(cliente, web_type, dry_run)

        if do_all or do_seo:
            results["seo"] = phase_seo(cliente, seo_mode, dry_run)

        if do_all or do_ads:
            results["ads"] = phase_ads(cliente, ads_platform, dry_run)

        if do_all or do_contenido:
            results["contenido"] = phase_contenido(cliente, dry_run)

        if do_all or do_entregar:
            results["entrega"] = phase_entregar(cliente, dry_run)

        if do_all or do_seguimiento:
            results["seguimiento"] = phase_seguimiento(cliente, dry_run)

        if do_all or do_financiero:
            results["financiero"] = phase_financiero(dry_run)

    except Exception as e:
        logger.error("Error en pipeline: %s", e)
        results["error"] = str(e)

    elapsed = (datetime.now() - start).total_seconds()
    logger.info("Pipeline completado en %.1fs", elapsed)

    _log_event("pipeline_complete", cliente, {"elapsed_s": round(elapsed, 1), "results": results})
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Services Pipeline — Ciclo de vida del cliente",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--cliente", "-c", default="", help="Nombre del cliente")
    parser.add_argument("--all", action="store_true", help="Ejecutar todas las fases")
    parser.add_argument("--contrato", action="store_true", help="Generar contrato")
    parser.add_argument("--setup_web", metavar="TYPE", nargs="?", const="landing", help="Setup web (landing|astro|medusa)")
    parser.add_argument("--seo", action="store_true", help="Ejecutar análisis/contenido SEO")
    parser.add_argument("--seo_mode", default="content", choices=["analyze", "content"], help="Modo SEO")
    parser.add_argument("--ads", action="store_true", help="Ejecutar estrategia de ads")
    parser.add_argument("--ads_platform", default="google", choices=["google", "meta"], help="Plataforma de ads")
    parser.add_argument("--contenido", action="store_true", help="Generar contenido audiovisual")
    parser.add_argument("--entregar", action="store_true", help="Empaquetar entrega al cliente")
    parser.add_argument("--seguimiento", action="store_true", help="Crear seguimiento (Trello + Calendar)")
    parser.add_argument("--financiero", action="store_true", help="Dashboard financiero")
    parser.add_argument("--status", action="store_true", help="Ver estado de todos los clientes")
    parser.add_argument("--dry-run", action="store_true", help="Simular sin escribir archivos")

    args = parser.parse_args()

    # If --status only, no cliente needed
    if args.status and not any([args.all, args.contrato, args.setup_web, args.seo,
                                 args.ads, args.contenido, args.entregar, args.seguimiento,
                                 args.financiero]):
        phase_status()
        return

    if not args.cliente and not args.status and not args.financiero:
        parser.error("--cliente es requerido (excepto para --status y --financiero)")

    results = run_pipeline(
        cliente=args.cliente,
        do_all=args.all,
        do_contrato=args.contrato,
        setup_web=args.setup_web,
        do_seo=args.seo,
        seo_mode=args.seo_mode,
        do_ads=args.ads,
        ads_platform=args.ads_platform,
        do_contenido=args.contenido,
        do_entregar=args.entregar,
        do_seguimiento=args.seguimiento,
        do_financiero=args.financiero,
        do_status=args.status,
        dry_run=args.dry_run,
    )

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
