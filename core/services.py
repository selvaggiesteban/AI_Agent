# Copyright (C) 2025 Esteban Selvaggi
# ... (License header omitted for brevity but I'll keep it in the real file)
"""
Services Pipeline — Orquestador del ciclo de vida del cliente.
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

# Import the base pipeline
from src.agent.pipeline_base import BasePipeline

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
# ServicesPipeline Implementation
# ---------------------------------------------------------------------------

class ServicesPipeline(BasePipeline):
    def __init__(self):
        log_dir = ROOT_DIR / "logs" / "pipeline"
        log_dir.mkdir(parents=True, exist_ok=True)
        super().__init__(name="services", telemetry_path=str(log_dir / "services_execution_log.json"))
        
        self.logger.setLevel(logging.INFO)
        _console = logging.StreamHandler()
        _console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S"))
        self.logger.addHandler(_console)
        _file_handler = logging.FileHandler(log_dir / "services.log", encoding="utf-8")
        _file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
        self.logger.addHandler(_file_handler)

    def _db_query(self, query: str, params: tuple = (), fetch: bool = True) -> list:
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

    def _get_cliente_data(self, cliente: str) -> Optional[Dict]:
        rows = self._db_query(
            "SELECT * FROM main WHERE title LIKE ? OR primary_email LIKE ? LIMIT 1",
            (f"%{cliente}%", f"%{cliente}%"),
        )
        return rows[0] if rows else None

    def phase_contrato(self, cliente: str, dry_run: bool = False) -> Dict:
        self.logger.info("=== FASE 1: Contrato — %s ===", cliente)
        data = self._get_cliente_data(cliente) or {"title": cliente, "primary_email": "", "phone": "", "address": "", "sector": ""}
        template_path = ROOT_DIR / "scripts" / "templates" / "contrato_prestacion_servicios.md"
        if not template_path.exists(): return {"ok": False, "error": "template_missing"}
        template = template_path.read_text(encoding="utf-8")
        nombre, domicilio, email, telefono, ciudad, provincia, sector = data.get("title", cliente), data.get("address", ""), data.get("primary_email", ""), data.get("phone", ""), data.get("city", ""), data.get("province", ""), data.get("sector", "")
        template = template.replace("CONTRATANTE: ..........................................................", f"CONTRATANTE: {nombre}")
        template = template.replace("D.N.I. ...................................", "D.N.I. [COMPLETAR]")
        template = template.replace("CUIT/CUIL ...................................", "CUIT/CUIL [COMPLETAR]")
        template = template.replace("con domicilio en .........................................................., en adelante", f"con domicilio en {domicilio or '[COMPLETAR]'}, en adelante")
        today = datetime.now()
        template = template.replace("a los ....... días del mes de ........................... de 20....", f"a los {today.day} días del mes de {today.strftime('%B')} de {today.year}")
        if sector: template = template.replace("Descripción del proyecto:\n> .................................................................................", f"Descripción del proyecto:\n> Servicios de {sector.lower()} para {nombre}")
        contact_info = f"\n\n---\n> **Datos de contacto del CONTRATANTE (extraídos de DB):**\n"
        if email: contact_info += f"> - Email: {email}\n"
        if telefono: contact_info += f"> - Teléfono: {telefono}\n"
        if ciudad: contact_info += f"> - Ciudad: {ciudad}\n"
        if provincia: contact_info += f"> - Provincia: {provincia}\n"
        contact_info += f"> - Sector: {sector or 'No especificado'}\n"
        contact_info += "> - **NOTA:** DNI y CUIT deben ser completados por el cliente antes de firmar.\n"
        template += contact_info
        out_dir = DATA_OUTPUTS_DIR / "contratos"
        out_dir.mkdir(parents=True, exist_ok=True)
        slug = cliente.lower().replace(" ", "_").replace(".", "")
        out_path = out_dir / f"{slug}_contrato.md"
        if dry_run: return {"ok": True, "path": str(out_path), "dry_run": True}
        out_path.write_text(template, encoding="utf-8")
        self._log_event("contrato", cliente, {"path": str(out_path)})
        return {"ok": True, "path": str(out_path)}

    def _setup_landing(self, cliente: str, data: Dict, dry_run: bool) -> Dict:
        self.logger.info("  → Setup Landing Page para %s", cliente)
        landing_gen = ROOT_DIR / "scripts" / "web_designer" / "landing-page-generator" / "landing-page-generator.py"
        if not landing_gen.exists(): return {"ok": False, "error": "script_missing"}
        out_dir = DATA_OUTPUTS_DIR / "landing" / cliente.lower().replace(" ", "_")
        out_dir.mkdir(parents=True, exist_ok=True)
        if dry_run: return {"ok": True, "dry_run": True}
        brief_path = out_dir / "brief.json"
        brief = {"title": data.get("title", cliente), "category": data.get("sector", ""), "phone": data.get("phone", ""), "address": data.get("address", ""), "city": data.get("city", ""), "website": (data.get("urls") or "").split(",")[0].strip() if data.get("urls") else ""}
        brief_path.write_text(json.dumps(brief, indent=2, ensure_ascii=False), encoding="utf-8")
        try:
            result = subprocess.run([sys.executable, str(landing_gen), "--brief", str(brief_path), "--output", str(out_dir)], capture_output=True, text=True, timeout=120, cwd=str(ROOT_DIR))
            self.logger.info("  Landing page generada en: %s", out_dir)
            self._log_event("setup_landing", cliente, {"path": str(out_dir)})
            return {"ok": True, "path": str(out_dir)}
        except Exception as e: return {"ok": False, "error": str(e)}

    def _setup_astro(self, cliente: str, data: Dict, dry_run: bool) -> Dict:
        self.logger.info("  → Setup Sitio Astro para %s", cliente)
        template_dir = ROOT_DIR / "scripts" / "web_designer" / "example"
        if not template_dir.exists(): return {"ok": False, "error": "template_missing"}
        slug = cliente.lower().replace(" ", "_")
        out_dir = DATA_OUTPUTS_DIR / "sites" / slug
        if dry_run: return {"ok": True, "dry_run": True}
        if not out_dir.exists():
            shutil.copytree(template_dir, out_dir, ignore=shutil.ignore_patterns("node_modules", ".astro", "dist"))
        content_dir = out_dir / "src" / "content" / "blog"
        if content_dir.exists():
            (out_dir / "brief.json").write_text(json.dumps({"title": data.get("title", cliente), "sector": data.get("sector", ""), "phone": data.get("phone", "")}, indent=2, ensure_ascii=False), encoding="utf-8")
        self._log_event("setup_astro", cliente, {"path": str(out_dir)})
        return {"ok": True, "path": str(out_dir)}

    def _setup_medusa(self, cliente: str, data: Dict, dry_run: bool) -> Dict:
        self.logger.info("  → Setup MedusaJS para %s", cliente)
        slug = cliente.lower().replace(" ", "_")
        out_dir = DATA_OUTPUTS_DIR / "stores" / slug
        if dry_run: return {"ok": True, "dry_run": True}
        if out_dir.exists(): return {"ok": True, "path": str(out_dir), "note": "already_exists"}
        try:
            result = subprocess.run(["npx", "create-medusa-app@latest", str(out_dir), "--skip-db"], capture_output=True, text=True, timeout=300, cwd=str(ROOT_DIR))
            self.logger.info("  MedusaJS scaffoldered en: %s", out_dir)
            self._log_event("setup_medusa", cliente, {"path": str(out_dir)})
            return {"ok": True, "path": str(out_dir)}
        except Exception as e: return {"ok": False, "error": str(e)}

    def phase_setup_web(self, cliente: str, web_type: str = "landing", dry_run: bool = False) -> Dict:
        self.logger.info("=== FASE 2: Setup Web (%s) — %s ===", web_type, cliente)
        data = self._get_cliente_data(cliente) or {"title": cliente}
        if web_type == "landing": return self._setup_landing(cliente, data, dry_run)
        elif web_type == "astro": return self._setup_astro(cliente, data, dry_run)
        elif web_type == "medusa": return self._setup_medusa(cliente, data, dry_run)
        else: return {"ok": False, "error": f"unknown_type:{web_type}"}

    def phase_seo(self, cliente: str, mode: str = "content", dry_run: bool = False) -> Dict:
        self.logger.info("=== FASE 3: SEO (%s) — %s ===", mode, cliente)
        data = self._get_cliente_data(cliente) or {"title": cliente, "urls": ""}
        seo_gen = ROOT_DIR / "scripts" / "seo_manager" / "seo-content-generator" / "seo_content_generator.py"
        if not seo_gen.exists(): return {"ok": False, "error": "script_missing"}
        out_dir = DATA_OUTPUTS_DIR / "seo" / cliente.lower().replace(" ", "_")
        out_dir.mkdir(parents=True, exist_ok=True)
        if dry_run: return {"ok": True, "dry_run": True}
        site_url = (data.get("urls") or "").split(",")[0].strip() if data.get("urls") else ""
        if mode == "analyze" and site_url:
            try:
                result = subprocess.run([sys.executable, str(seo_gen), "--urls", site_url, "--output", str(out_dir / "reporte.md"), "--excel", str(out_dir / "reporte.xlsx")], capture_output=True, text=True, timeout=600, cwd=str(ROOT_DIR))
                self._log_event("seo_analyze", cliente, {"path": str(out_dir), "url": site_url})
                return {"ok": True, "path": str(out_dir)}
            except Exception as e: return {"ok": False, "error": str(e)}
        else:
            self._log_event("seo_content", cliente, {"mode": "content", "path": str(out_dir)})
            return {"ok": True, "path": str(out_dir), "note": "stub_requires_brief"}

    def phase_ads(self, cliente: str, platform: str = "google", dry_run: bool = False) -> Dict:
        self.logger.info("=== FASE 4: Ads (%s) — %s ===", platform, cliente)
        data = self._get_cliente_data(cliente) or {"title": cliente, "urls": ""}
        out_dir = DATA_OUTPUTS_DIR / "ads" / cliente.lower().replace(" ", "_")
        out_dir.mkdir(parents=True, exist_ok=True)
        if dry_run: return {"ok": True, "dry_run": True}
        if platform == "google":
            ads_strat = ROOT_DIR / "scripts" / "ads_manager" / "ads_strategist.py"
            if not ads_strat.exists(): return {"ok": False, "error": "script_missing"}
            site_url = (data.get("urls") or "").split(",")[0].strip() if data.get("urls") else ""
            if not site_url: return {"ok": False, "error": "no_site_url"}
            try:
                result = subprocess.run([sys.executable, str(ads_strat), site_url, "--output", str(out_dir)], capture_output=True, text=True, timeout=120, cwd=str(ROOT_DIR))
                self._log_event("ads_google", cliente, {"path": str(out_dir), "url": site_url})
                return {"ok": True, "path": str(out_dir)}
            except Exception as e: return {"ok": False, "error": str(e)}
        elif platform == "meta":
            self._log_event("ads_meta_stub", cliente, {"path": str(out_dir)})
            return {"ok": True, "path": str(out_dir), "note": "stub_requires_meta_credentials"}
        else: return {"ok": False, "error": f"unknown_platform:{platform}"}

    def phase_contenido(self, cliente: str, dry_run: bool = False) -> Dict:
        self.logger.info("=== FASE 5: Contenido Audiovisual — %s ===", cliente)
        data = self._get_cliente_data(cliente) or {"title": cliente}
        out_dir = DATA_OUTPUTS_DIR / "content" / cliente.lower().replace(" ", "_")
        out_dir.mkdir(parents=True, exist_ok=True)
        if dry_run: return {"ok": True, "dry_run": True}
        brief = {"cliente": data.get("title", cliente), "sector": data.get("sector", ""), "colores": "por definir", "estilo": "profesional"}
        (out_dir / "brief_contenido.json").write_text(json.dumps(brief, indent=2, ensure_ascii=False), encoding="utf-8")
        self._log_event("contenido_stub", cliente, {"path": str(out_dir)})
        return {"ok": True, "path": str(out_dir), "note": "stub_requires_canva"}

    def phase_entregar(self, cliente: str, dry_run: bool = False) -> Dict:
        self.logger.info("=== FASE 6: Entrega — %s ===", cliente)
        data = self._get_cliente_data(cliente) or {"title": cliente, "urls": ""}
        slug = cliente.lower().replace(" ", "_")
        delivery_dir = DATA_OUTPUTS_DIR / "deliveries" / slug
        delivery_dir.mkdir(parents=True, exist_ok=True)
        if dry_run: return {"ok": True, "dry_run": True}
        screenshot_script = ROOT_DIR / "scripts" / "graphic_designer" / "web-screenshot" / "web_screenshots.py"
        site_url = (data.get("urls") or "").split(",")[0].strip() if data.get("urls") else ""
        screenshots_dir = delivery_dir / "screenshots"
        screenshots_dir.mkdir(exist_ok=True)
        if site_url and screenshot_script.exists():
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("web_screenshots", str(screenshot_script))
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                for viewport in ["desktop", "tablet", "mobile"]:
                    mod.take_screenshot(site_url, viewport, str(screenshots_dir / f"{slug}_{viewport}.png"))
            except Exception as e: self.logger.warning("  Error tomando screenshots: %s", e)
        contrato_src = DATA_OUTPUTS_DIR / "contratos" / f"{slug}_contrato.md"
        if contrato_src.exists(): shutil.copy2(contrato_src, delivery_dir / "contrato.md")
        seo_src = DATA_OUTPUTS_DIR / "seo" / slug
        if seo_src.exists(): shutil.copytree(seo_src, delivery_dir / "seo", dirs_exist_ok=True)
        instructivo = f"# Instructivo de Uso — {data.get('title', cliente)}\n\n## Credenciales\n(completar)\n\n## Acceso al Sitio\n- URL: {site_url or 'pendiente'}\n- Panel: (completar)\n\n## Próximos Pasos\n1. Revisar sitio\n2. Cambios\n3. Aceptación"
        (delivery_dir / "instructivo_uso.md").write_text(instructivo, encoding="utf-8")
        self._log_event("entrega", cliente, {"path": str(delivery_dir), "url": site_url})
        return {"ok": True, "path": str(delivery_dir)}

    def phase_seguimiento(self, cliente: str, dry_run: bool = False) -> Dict:
        self.logger.info("=== FASE 7: Seguimiento — %s ===", cliente)
        data = self._get_cliente_data(cliente) or {"title": cliente}
        if dry_run: return {"ok": True, "dry_run": True}
        results = {}
        if TRELLO_API_KEY and TRELLO_TOKEN and TRELLO_API_KEY != "YOUR_TRELLO_API_KEY":
            try:
                import requests as req
                base = "https://api.trello.com/1"
                auth = {"key": TRELLO_API_KEY, "token": TRELLO_TOKEN}
                boards_resp = req.get(f"{base}/members/me/boards", params=auth, timeout=15)
                boards_resp.raise_for_status()
                boards = boards_resp.json()
                board_id = next((b["id"] for b in boards if "marketing" in b.get("name", "").lower() or "proyectos" in b.get("name", "").lower()), boards[0]["id"] if boards else None)
                if board_id:
                    lists_resp = req.get(f"{base}/boards/{board_id}/lists", params=auth, timeout=15)
                    lists_resp.raise_for_status()
                    lists = lists_resp.json()
                    pending_id = next((l["id"] for l in lists if "pendiente" in l.get("name", "").lower() or "todo" in l.get("name", "").lower()), lists[0]["id"] if lists else None)
                    if pending_id:
                        card_data = {**auth, "idList": pending_id, "name": f"Seguimiento — {data.get('title', cliente)}", "desc": f"Cliente: {data.get('title', cliente)}\nEmail: {data.get('primary_email', '')}\nTel: {data.get('phone', '')}"}
                        card_resp = req.post(f"{base}/cards", data=card_data, timeout=15)
                        card_resp.raise_for_status()
                        card = card_resp.json()
                        results["trello"] = {"ok": True, "card_id": card["id"], "url": card.get("shortUrl")}
                else: results["trello"] = {"ok": False, "error": "no_board_found"}
            except Exception as e: results["trello"] = {"ok": False, "error": str(e)}
        else: results["trello"] = {"ok": False, "error": "credentials_missing"}
        
        try:
            token_pickle = GOOGLE_CREDS_DIR / "token.pickle"
            client_secret = GOOGLE_CREDS_DIR / "client_secret.json"
            if token_pickle.exists() and client_secret.exists():
                from google.auth.transport.requests import Request
                from google_auth_oauthlib.flow import InstalledAppFlow
                from googleapiclient.discovery import build
                import pickle
                SCOPES = ["https://www.googleapis.com/auth/calendar"]
                with open(token_pickle, "rb") as f: creds = pickle.load(f)
                if not creds or not creds.valid:
                    if creds and creds.expired and creds.refresh_token: creds.refresh(Request())
                    else:
                        flow = InstalledAppFlow.from_client_secrets_file(str(client_secret), SCOPES)
                        creds = flow.run_local_server(port=0)
                        with open(token_pickle, "wb") as f: pickle.dump(creds, f)
                service = build("calendar", "v3", credentials=creds)
                now = datetime.now()
                event = {
                    "summary": f"Reunión — {data.get('title', cliente)}",
                    "description": f"Seguimiento con {data.get('title', cliente)}\nEmail: {data.get('primary_email', '')}",
                    "start": {"dateTime": (now + timedelta(days=1)).replace(hour=10, minute=0, second=0).isoformat(), "timeZone": "America/Argentina/Buenos_Aires"},
                    "end": {"dateTime": (now + timedelta(days=1)).replace(hour=11, minute=0, second=0).isoformat(), "timeZone": "America/Argentina/Buenos_Aires"},
                    "conferenceData": {"createRequest": {"requestId": f"meet-{cliente.lower().replace(' ', '_')}-{int(now.timestamp())}", "conferenceSolutionKey": {"type": "hangoutsMeet"}}},
                }
                created = service.events().insert(calendarId="primary", body=event, conferenceDataVersion=1).execute()
                meet_link = created.get("conferenceData", {}).get("entryPoints", [{}])[0].get("uri", "")
                results["calendar"] = {"ok": True, "event_id": created["id"], "meet_link": meet_link}
        except Exception as e: results["calendar"] = {"ok": False, "error": str(e)}
        self._log_event("seguimiento", cliente, results)
        return results

    def phase_financiero(self, dry_run: bool = False) -> Dict:
        self.logger.info("=== FASE 8: Dashboard Financiero ===")
        if dry_run: return {"ok": True, "dry_run": True}
        accountly_main = ROOT_DIR / "scripts" / "financial_manager" / "accountly" / "main.py"
        if not accountly_main.exists(): return {"ok": False, "error": "script_missing"}
        try:
            result = subprocess.run([sys.executable, str(accountly_main)], capture_output=True, text=True, timeout=120, cwd=str(accountly_main.parent))
            self._log_event("financiero", "global", {})
            return {"ok": True}
        except Exception as e: return {"ok": False, "error": str(e)}

    def phase_status(self) -> Dict:
        self.logger.info("=== FASE 9: Status ===")
        telemetry = self._load_telemetry()
        if not telemetry: return {"ok": True, "entries": 0}
        clientes = {}
        for entry in telemetry:
            c = entry.get("cliente", "unknown")
            if c not in clientes: clientes[c] = []
            clientes[c].append(entry)
        return {"ok": True, "clientes": len(clientes), "total_events": len(telemetry)}

    def execute(self, cliente: str, **kwargs) -> Dict:
        start_time = time.time()
        results = {}
        do_all = kwargs.get("do_all", False)
        dry_run = kwargs.get("dry_run", False)
        if kwargs.get("do_status"): return self.phase_status()
        if do_all or kwargs.get("do_contrato"): results["contrato"] = self.phase_contrato(cliente, dry_run)
        if do_all or kwargs.get("setup_web"): results["setup_web"] = self.phase_setup_web(cliente, kwargs.get("setup_web", "landing"), dry_run)
        if do_all or kwargs.get("do_seo"): results["seo"] = self.phase_seo(cliente, kwargs.get("seo_mode", "content"), dry_run)
        if do_all or kwargs.get("do_ads"): results["ads"] = self.phase_ads(cliente, kwargs.get("ads_platform", "google"), dry_run)
        if do_all or kwargs.get("do_contenido"): results["contenido"] = self.phase_contenido(cliente, dry_run)
        if do_all or kwargs.get("do_entregar"): results["entrega"] = self.phase_entregar(cliente, dry_run)
        if do_all or kwargs.get("do_seguimiento"): results["seguimiento"] = self.phase_seguimiento(cliente, dry_run)
        if do_all or kwargs.get("do_financiero"): results["financiero"] = self.phase_financiero(dry_run)
        return self.finalize(start_time, results)

def run_pipeline(cliente: str, **kwargs):
    pipeline = ServicesPipeline()
    return pipeline.execute(cliente, **kwargs)

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--cliente", "-c", default="")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--contrato", action="store_true")
    parser.add_argument("--setup_web", metavar="TYPE", nargs="?", const="landing")
    parser.add_argument("--seo", action="store_true")
    parser.add_argument("--seo_mode", default="content")
    parser.add_argument("--ads", action="store_true")
    parser.add_argument("--ads_platform", default="google")
    parser.add_argument("--contenido", action="store_true")
    parser.add_argument("--entregar", action="store_true")
    parser.add_argument("--seguimiento", action="store_true")
    parser.add_argument("--financiero", action="store_true")
    parser.add_argument("--status", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.status and not any([args.all, args.contrato, args.setup_web, args.seo, args.ads, args.contenido, args.entregar, args.seguimiento, args.financiero]):
        ServicesPipeline().phase_status()
        return
    if not args.cliente and not args.status and not args.financiero:
        parser.error("--cliente es requerido")
    print(json.dumps(run_pipeline(args.cliente, **vars(args)), indent=2))

if __name__ == "__main__":
    main()
