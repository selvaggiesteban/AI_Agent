# Copyright (C) 2025 Esteban Selvaggi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
"""
Lead Pipeline — Orchestrator for lead prospecting and acquisition.
"""

import sys
import os
import json
import csv
import sqlite3
import subprocess
import logging
import re
import time
import math
from pathlib import Path
from datetime import datetime
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
    DATA_INPUTS_DIR,
    KEYWORDLESS_PROXY_CATEGORIES,
)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
GOSOM_DIR = DATA_INPUTS_DIR / "gosom"
SEEDS_DIR = GOSOM_DIR / "seeds"
CHUNKS_DIR = GOSOM_DIR / "chunks"
OUTPUT_DIR = GOSOM_DIR / "output"
KEYWORDS_FILE = SEEDS_DIR / "keywords.txt"
LOCATIONS_FILE = SEEDS_DIR / "locations.txt"

CHUNK_SIZE = 500
GOSOM_CONCURRENCY = 3
GOSOM_LANG = "es"
GOSOM_DEPTH = 1
GOSOM_ZOOM = 15
GOSOM_RADIUS = 5000
GOSOM_GRID_BBOX = "-34.93,-58.53,-34.36,-58.10"
GOSOM_GRID_CELL = 1.0
GOSOM_PBA_BBOX = "-39.0,-63.5,-33.5,-56.5"
CSV_PARTIAL_ROWS = 500
CHECKPOINT_FILE = GOSOM_DIR / "checkpoint.json"
POLL_INTERVAL = 30

LEAD_SCORE_WEIGHTS = {
    "website": 30,
    "email": 25,
    "phone": 15,
    "rating": 10,
    "reviews": 10,
    "description": 5,
    "hours": 5,
}

SECTOR_KEYWORDS = {
    "Technology": ["informatica", "computacion", "sistemas", "soporte tecnico", "reparacion", "tecnico", "web", "hosting", "programacion", "desarrollo", "software", "app", "digital"],
    "Health": ["medico", "clinica", "hospital", "odontologo", "farmacia", "kinesiologo", "psicologo", "nutricionista", "veterinaria"],
    "Commerce": ["almacen", "supermercado", "kiosco", "tienda", "comercio", "local", "venta", "negocio"],
    "Gastronomy": ["restaurante", "bar", "cafeteria", "pizzeria", "heladeria", "rotiseria", "panaderia", "pasteleria", "hamburgueseria"],
    "Industry": ["taller", "metalurgica", "mecanizado", "fabrica", "industrial", "portones", "calderas", "soldador", "toldos"],
    "Services": ["abogado", "contador", "escribano", "seguro", "inmobiliaria", "consultora", "asesoria", "arquitecto", "ingeniero"],
    "Education": ["escuela", "colegio", "instituto", "profesor", "curso", "capacitacion", "universidad", "academia"],
    "Transport": ["motos", "bicicletas", "grua", "auxilio", "taxi", "remis", "mudanza", "flete", "logistica"],
    "Construction": ["construccion", "obra", "plomeria", "electricista", "carpinteria", "pintura", "cerrajero", "vidrieria"],
}

DEFAULT_OFFER_HOSTING = (
    "Hello, how are you? I'm writing because I saw you have a presence on Google Maps "
    "and I wanted to know if you are satisfied with your current website and hosting. At LANUS "
    "COMPUTACION we are offering a Cloudflare hosting promo with improved performance "
    "and included security, at a very affordable price. No commitment, may I "
    "share more info with you? Regards!"
)

OFFERS = {
    "hosting": {
        "subject": "Cloudflare Hosting Promo - LANUS COMPUTACION",
        "message": DEFAULT_OFFER_HOSTING,
    },
    "web": {
        "subject": "Website Redesign - LANUS COMPUTACION",
        "message": (
            "Hello, I saw your business on Google Maps and noticed that you could "
            "improve your web presence. We offer modern and affordable designs. "
            "No commitment, may I send you some info?"
        ),
    },
    "seo": {
        "subject": "Web Positioning - LANUS COMPUTACION",
        "message": (
            "Hello, we offer SEO services so your business "
            "appears first on Google. Would you be interested in a "
            "free audit?"
        ),
    },
}

# ---------------------------------------------------------------------------
# LeadPipeline Implementation
# ---------------------------------------------------------------------------

class LeadPipeline(BasePipeline):
    def __init__(self):
        log_dir = ROOT_DIR / "logs" / "pipeline"
        log_dir.mkdir(parents=True, exist_ok=True)
        super().__init__(name="lead", telemetry_path=str(log_dir / "lead_execution_log.json"))

        self.logger.setLevel(logging.INFO)
        _console = logging.StreamHandler()
        _console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S"))
        self.logger.addHandler(_console)
        _file_handler = logging.FileHandler(log_dir / "lead.log", encoding="utf-8")
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

    def _write_chunk(self, num: int, lines: List[str]) -> None:
        path = CHUNKS_DIR / f"chunk_{num:03d}.txt"
        with open(path, "w", encoding="ascii", errors="replace") as f:
            f.write("\n".join(lines) + "\n")
        self.logger.info("  ✓ chunk_%03d.txt (%d lines)", num, len(lines))

    def phase_combine(self, keywords_filter="", locations_filter="", keywords_file="", grid_mode=False, keywordless_mode=False, dry_run=False):
        self.logger.info("=== PHASE 1: Combine ===")
        def _load_lines(filepath: Path):
            if not filepath.exists():
                self.logger.error("File not found: %s", filepath)
                return []
            with open(filepath, "r", encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip()]

        kw_file = Path(keywords_file) if keywords_file else KEYWORDS_FILE
        keywords = _load_lines(kw_file)

        if keywordless_mode:
            locations = _load_lines(LOCATIONS_FILE)
            if locations_filter:
                filters = [l.strip().lower() for l in locations_filter.split(",")]
                locations = [u for u in locations if any(f in u.lower() for f in filters)]
            if not locations:
                self.logger.error("No locations available")
                return {"ok": False, "error": "empty_locations"}
            queries = []
            for loc in locations:
                for proxy in KEYWORDLESS_PROXY_CATEGORIES: queries.append(f"{proxy} {loc}")
                queries.append(loc)
            total = len(queries)
            self.logger.info("  KEYWORDLESS mode activated | Locations: %d | Queries: %d | Proxies: %s", len(locations), total, ",".join(KEYWORDLESS_PROXY_CATEGORIES))
            if dry_run:
                self.logger.info("  [DRY-RUN] %d queries would be generated in chunks of %d", total, CHUNK_SIZE)
                return {"ok": True, "dry_run": True, "total": total}
            CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
            for f in CHUNKS_DIR.glob("chunk_*.txt"): f.unlink()
            chunk_num, current_lines = 1, []
            for q in queries:
                current_lines.append(q)
                if len(current_lines) >= CHUNK_SIZE:
                    self._write_chunk(chunk_num, current_lines)
                    current_lines, chunk_num = [], chunk_num + 1
            if current_lines: self._write_chunk(chunk_num, current_lines)
            self._log_event("combine", {"keywords": 0, "locations": len(locations), "chunks": chunk_num - 1, "keywordless_mode": True})
            return {"ok": True, "chunks": chunk_num - 1, "total": total, "keywordless_mode": True}

        elif grid_mode:
            self.logger.info("  GRID mode activated (grid-bbox handles location)")
            if keywords_filter:
                filters = [k.strip().lower() for k in keywords_filter.split(",")]
                keywords = [k for k in keywords if any(f in k.lower() for f in filters)]
            if not keywords:
                self.logger.error("No keywords available")
                return {"ok": False, "error": "empty_keywords"}
            total = len(keywords)
            self.logger.info("  Keywords: %d (grid-bbox: %s)", total, GOSOM_GRID_BBOX)
            if dry_run:
                self.logger.info("  [DRY-RUN] %d queries would be generated in chunks of %d", total, CHUNK_SIZE)
                return {"ok": True, "dry_run": True, "total": total}
            CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
            for f in CHUNKS_DIR.glob("chunk_*.txt"): f.unlink()
            chunk_num, current_lines = 1, []
            for kw in keywords:
                current_lines.append(kw)
                if len(current_lines) >= CHUNK_SIZE:
                    self._write_chunk(chunk_num, current_lines)
                    current_lines, chunk_num = [], chunk_num + 1
            if current_lines: self._write_chunk(chunk_num, current_lines)
            self._log_event("combine", {"keywords": len(keywords), "locations": 0, "chunks": chunk_num - 1, "grid_mode": True})
            return {"ok": True, "chunks": chunk_num - 1, "total": total, "grid_mode": True}

        else:
            locations = _load_lines(LOCATIONS_FILE)
            if keywords_filter:
                filters = [k.strip().lower() for k in keywords_filter.split(",")]
                keywords = [k for k in keywords if any(f in k.lower() for f in filters)]
            if locations_filter:
                filters = [l.strip().lower() for l in locations_filter.split(",")]
                locations = [u for u in locations if any(f in u.lower() for f in filters)]
            if not keywords or not locations:
                self.logger.error("No keywords or locations available")
                return {"ok": False, "error": "empty_seeds"}
            total = len(keywords) * len(locations)
            self.logger.info("  Keywords: %d x Locations: %d = %d combinations", len(keywords), len(locations), total)
            if dry_run:
                self.logger.info("  [DRY-RUN] %d combinations would be generated in chunks of %d", total, CHUNK_SIZE)
                return {"ok": True, "dry_run": True, "total": total}
            CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
            for f in CHUNKS_DIR.glob("chunk_*.txt"): f.unlink()
            chunk_num, current_lines = 1, []
            for kw in keywords:
                for loc in locations:
                    current_lines.append(f"{kw} {loc}")
                    if len(current_lines) >= CHUNK_SIZE:
                        self._write_chunk(chunk_num, current_lines)
                        current_lines, chunk_num = [], chunk_num + 1
            if current_lines: self._write_chunk(chunk_num, current_lines)
            self._log_event("combine", {"keywords": len(keywords), "locations": len(locations), "chunks": chunk_num - 1})
            return {"ok": True, "chunks": chunk_num - 1, "total": total}

    def phase_scrape(self, dry_run=False, grid_bbox="", grid_cell=0.0):
        self.logger.info("=== PHASE 2: Scrape (Gosom) ===")
        docker_ok = False
        try:
            result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=10)
            docker_ok = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        if docker_ok: return self._scrape_docker(dry_run, grid_bbox, grid_cell)
        else: return self._scrape_exe(dry_run, grid_bbox, grid_cell)

    def _scrape_docker(self, dry_run, grid_bbox="", grid_cell=0.0):
        self.logger.info("  Using Gosom via Docker")
        if dry_run:
            self.logger.info("  [DRY-RUN] Gosom Docker would scrape chunks")
            return {"ok": True, "dry_run": True, "method": "docker"}
        chunks = list(CHUNKS_DIR.glob("chunk_*.txt"))
        if not chunks:
            self.logger.warning("  No chunks to scrape — run --combine first")
            return {"ok": False, "error": "no_chunks"}
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        for chunk_file in chunks:
            self.logger.info("  Scraping chunk: %s", chunk_file.name)
            try:
                result = subprocess.run(
                    ["docker", "run", "--rm", "-v", f"{GOSOM_DIR}:/data", "gosom/google-maps-scraper:latest",
                     "-i", f"/data/chunks/{chunk_file.name}", "-o", "/data/output", "-lang", GOSOM_LANG,
                     "-depth", str(GOSOM_DEPTH), "-concurrency", str(GOSOM_CONCURRENCY)],
                    capture_output=True, text=True, timeout=1800, cwd=str(ROOT_DIR),
                )
                if result.returncode != 0: self.logger.warning("  Gosom error in %s: %s", chunk_file.name, result.stderr[:300])
                else: self.logger.info("  ✓ %s completed", chunk_file.name)
            except Exception as e: self.logger.error("  Error executing Gosom Docker: %s", e)
        self._log_event("scrape", {"method": "docker", "chunks": len(chunks)})
        return {"ok": True, "method": "docker", "chunks_processed": len(chunks)}

    def _count_csv_rows(self, csv_path: Path) -> int:
        if not csv_path.exists(): return 0
        try:
            with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
                reader = csv.reader(f)
                next(reader, None)
                return sum(1 for _ in reader)
        except Exception: return 0

    def _split_csv_incremental(self, csv_path: Path, checkpoint: Dict, last_split_row: int) -> int:
        if not csv_path.exists(): return last_split_row
        try:
            with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                if not header: return last_split_row
                existing_parts = sorted([k for k in checkpoint.get("partials", {}) if k.startswith(csv_path.stem)])
                part_num, row_idx, part_row_count = len(existing_parts) + 1, 0, 0
                part_file, part_writer = None, None
                for row in reader:
                    row_idx += 1
                    if row_idx <= last_split_row: continue
                    if part_row_count == 0:
                        part_path = OUTPUT_DIR / f"{csv_path.stem}_part{part_num:04d}.csv"
                        part_file = open(part_path, "w", encoding="utf-8", newline="")
                        part_writer = csv.writer(part_file)
                        part_writer.writerow(header)
                    part_writer.writerow(row)
                    part_row_count += 1
                    if part_row_count >= CSV_PARTIAL_ROWS:
                        part_file.close()
                        checkpoint["partials"][part_path.name] = {"ts": datetime.now().isoformat(), "rows": part_row_count}
                        self._save_checkpoint(checkpoint)
                        self.logger.info("  ✓ Partial: %s (%d rows, total %d)", part_path.name, part_row_count, row_idx)
                        part_num, part_row_count = part_num + 1, 0
                if part_file and part_row_count > 0:
                    part_file.close()
                    checkpoint["partials"][part_path.name] = {"ts": datetime.now().isoformat(), "rows": part_row_count}
                    self._save_checkpoint(checkpoint)
                    self.logger.info("  ✓ Partial: %s (%d rows, total %d)", part_path.name, part_row_count, row_idx)
                return row_idx
        except Exception as e:
            self.logger.error("  Error in incremental split %s: %s", csv_path.name, e)
            return last_split_row

    def _scrape_exe(self, dry_run, grid_bbox="", grid_cell=0.0):
        self.logger.info("  Using Gosom via local EXE (Popen + polling)")
        exe_path = GOSOM_DIR / "google_maps_scraper-1.3.0-windows-amd64.exe"
        if not exe_path.exists():
            exes = list(GOSOM_DIR.glob("*.exe"))
            if exes: exe_path = exes[0]
            else: return {"ok": False, "error": "gosom_not_found"}
        if dry_run: return {"ok": True, "dry_run": True, "method": "exe"}
        chunks = list(CHUNKS_DIR.glob("chunk_*.txt"))
        if not chunks: return {"ok": False, "error": "no_chunks"}
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        checkpoint = self._load_checkpoint()
        bbox_val, cell_val = grid_bbox or GOSOM_GRID_BBOX, grid_cell or GOSOM_GRID_CELL
        pending = [c for c in sorted(chunks) if c.name not in checkpoint["completed"]]
        if not pending: return {"ok": True, "method": "exe", "skipped": len(chunks), "processed": 0}
        processed, total_rows = 0, 0
        for chunk_file in pending:
            csv_path = OUTPUT_DIR / f"{chunk_file.stem}.csv"
            if csv_path.exists() and chunk_file.name not in checkpoint["completed"]:
                csv_path.unlink(missing_ok=True)
                for old_partial in OUTPUT_DIR.glob(f"{chunk_file.stem}_part*.csv"):
                    old_partial.unlink(missing_ok=True)
                    checkpoint["partials"].pop(old_partial.name, None)
                self._save_checkpoint(checkpoint)
            try:
                log_file = open(GOSOM_DIR / "gosom_live.log", "w", encoding="utf-8", errors="replace")
                proc = subprocess.Popen(
                    [str(exe_path), "-input", str(chunk_file), "-results", str(csv_path), "-lang", GOSOM_LANG,
                     "-depth", str(GOSOM_DEPTH), "-c", str(GOSOM_CONCURRENCY), "-email", "-disable-page-reuse",
                     "-grid-bbox", bbox_val, "-grid-cell", str(cell_val), "-zoom", str(GOSOM_ZOOM)],
                    stdout=log_file, stderr=subprocess.STDOUT, cwd=str(GOSOM_DIR),
                )
                last_split_row, last_rows_seen, stale_count = 0, 0, 0
                while True:
                    proc.poll()
                    current_rows = self._count_csv_rows(csv_path)
                    if current_rows > last_rows_seen:
                        stale_count, last_rows_seen = 0, current_rows
                        self.logger.info("  📊 %d rows", current_rows)
                    else: stale_count += 1
                    if current_rows >= last_split_row + CSV_PARTIAL_ROWS:
                        last_split_row = self._split_csv_incremental(csv_path, checkpoint, last_split_row)
                    if proc.returncode is not None:
                        log_file.close()
                        final_rows = self._count_csv_rows(csv_path)
                        if final_rows > last_split_row:
                            last_split_row = self._split_csv_incremental(csv_path, checkpoint, last_split_row)
                        self._mark_chunk_done(checkpoint, chunk_file.name, final_rows)
                        processed += 1
                        total_rows += final_rows
                        break
                    if stale_count >= 240:
                        proc.terminate()
                        log_file.close()
                        final_rows = self._count_csv_rows(csv_path)
                        if final_rows > 0:
                            self._mark_chunk_done(checkpoint, chunk_file.name, final_rows)
                            processed += 1
                            total_rows += final_rows
                        break
                    time.sleep(POLL_INTERVAL)
            except Exception as e:
                self.logger.error("  Error in Popen+polling for %s: %s", chunk_file.name, e)
        self._log_event("scrape", {"method": "exe", "chunks_total": len(chunks), "chunks_processed": processed, "total_rows": total_rows})
        return {"ok": True, "method": "exe", "chunks_processed": processed, "total_rows": total_rows}

    def _load_checkpoint(self) -> Dict:
        if CHECKPOINT_FILE.exists():
            try: return json.loads(CHECKPOINT_FILE.read_text(encoding="utf-8"))
            except: return {"completed": {}, "partials": {}}
        return {"completed": {}, "partials": {}}

    def _save_checkpoint(self, data: Dict) -> None:
        CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
        CHECKPOINT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def _mark_chunk_done(self, checkpoint: Dict, chunk_name: str, rows: int) -> None:
        checkpoint["completed"][chunk_name] = {"ts": datetime.now().isoformat(), "rows": rows}
        self._save_checkpoint(checkpoint)

    def phase_import(self, dry_run=False):
        self.logger.info("=== PHASE 3: Import (CSV -> DB) ===")
        if not DB_PATH.exists(): return {"ok": False, "error": "db_missing"}
        existing_emails = set()
        rows = self._db_query("SELECT primary_email FROM main WHERE primary_email IS NOT NULL")
        for row in rows:
            if row.get("primary_email"): existing_emails.add(row["primary_email"].lower())
        csv_files = list(OUTPUT_DIR.glob("*.csv")) or list(GOSOM_DIR.glob("*.csv"))
        if not csv_files: return {"ok": True, "imported": 0, "skipped": 0, "note": "no_csvs"}
        total_new, total_skip = 0, 0
        for csv_file in csv_files:
            if csv_file.name.startswith("chunk_"): continue
            try:
                with open(csv_file, mode="r", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        email_str = row.get("emails", "") or row.get("email", "")
                        emails = [e.strip().lower() for e in email_str.replace("[", "").replace("]", "").replace("'", "").split(",") if e.strip()]
                        if not emails:
                            total_skip += 1; continue
                        primary_email = emails[0]
                        if primary_email in existing_emails:
                            total_skip += 1; continue
                        if dry_run:
                            self.logger.info("  [DRY-RUN] New: %s <%s>", row.get("title"), primary_email)
                            continue
                        self._db_query("INSERT INTO main (title, sector, primary_email, other_emails, phone, address, google_maps, urls, country, list, date_added) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, date('now'))",
                                      (row.get("title"), row.get("category"), primary_email, ",".join(emails[1:]), row.get("phone"), row.get("complete_address") or row.get("address", ""), row.get("link", ""), row.get("website", ""), "", "gosom_auto"), fetch=False)
                        existing_emails.add(primary_email)
                        total_new += 1
                self.logger.info("  ✓ %s processed", csv_file.name)
            except Exception as e: self.logger.error("  Error with %s: %s", csv_file.name, e)
        self._log_event("import", {"new": total_new, "skipped": total_skip, "csvs": len(csv_files)})
        return {"ok": True, "imported": total_new, "skipped": total_skip}

    def phase_sanitize(self, dry_run=False):
        self.logger.info("=== PHASE 4: Sanitize ===")
        if not DB_PATH.exists(): return {"ok": False, "error": "db_missing"}
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(main)")
        col_set = {col[1] for col in cursor.fetchall()}
        cursor.execute("SELECT rowid, * FROM main")
        rows = cursor.fetchall()
        stats = {"normalized": 0, "reclassified": 0, "scored": 0, "errors": 0}
        for row in rows:
            rowid, title, sector_orig = row["rowid"], row["title"] or "", row["sector"] or ""
            new_title = re.sub(r"\s+", " ", title).strip()
            text = f"{title} {sector_orig}".lower()
            new_sector = sector_orig
            for sector, keywords in SECTOR_KEYWORDS.items():
                for kw in keywords:
                    if kw in text:
                        new_sector = sector; break
                if new_sector != sector_orig: break
            if not new_sector: new_sector = "General"
            score = 0
            if "urls" in col_set and row["urls"] and str(row["urls"]).strip(): score += LEAD_SCORE_WEIGHTS["website"]
            if "primary_email" in col_set and row["primary_email"] and str(row["primary_email"]).strip(): score += LEAD_SCORE_WEIGHTS["email"]
            if "phone" in col_set and row["phone"] and str(row["phone"]).strip(): score += LEAD_SCORE_WEIGHTS["phone"]
            if "review_rating" in col_set:
                try:
                    rating = float(row["review_rating"] or 0)
                    if rating >= 4.0: score += LEAD_SCORE_WEIGHTS["rating"]
                except: pass
            if new_title != title: stats["normalized"] += 1
            if new_sector != sector_orig: stats["reclassified"] += 1
            score_label = "hot" if score >= 50 else "warm" if score >= 25 else "cold"
            if dry_run: continue
            try:
                cursor.execute("UPDATE main SET title = ?, sector = ?, deliverability = ? WHERE rowid = ?", (new_title, new_sector, score_label, rowid))
                stats["scored"] += 1
            except sqlite3.Error: stats["errors"] += 1
        if not dry_run: conn.commit()
        conn.close()
        self._log_event("sanitize", stats)
        return {"ok": True, **stats}

    def phase_prospect(self, channel="all", limit=100, offer="hosting", dry_run=False):
        self.logger.info("=== PHASE 5: Prospect (channel=%s, offer=%s, limit=%d) ===", channel, offer, limit)
        if not DB_PATH.exists(): return {"ok": False, "error": "db_missing"}
        channels = ["forms", "smtp", "whatsapp"] if channel == "all" else [channel]
        results = {}
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        for ch in channels:
            if ch == "forms": results["forms"] = self._prospect_forms(cursor, limit, dry_run)
            elif ch == "smtp": results["smtp"] = self._prospect_smtp(cursor, limit, offer, dry_run)
            elif ch == "whatsapp": results["whatsapp"] = self._prospect_whatsapp(cursor, limit, dry_run)
        conn.close()
        self._log_event("prospect", {"channel": channel, "offer": offer, "limit": limit, "results": results})
        return {"ok": True, **results}

    def _prospect_forms(self, cursor, limit, dry_run):
        cursor.execute("SELECT rowid, title, urls, primary_email FROM main WHERE urls IS NOT NULL AND urls != '' AND (form_processed IS NULL OR form_processed == '') AND deliverability != 'rejected' LIMIT ?", (limit,))
        leads = cursor.fetchall()
        if not leads: return {"count": 0}
        domains_file = LOG_DIR / "prospect_forms_domains.txt"
        if dry_run: return {"count": len(leads), "dry_run": True}
        with open(domains_file, "w", encoding="utf-8") as f:
            for lead in leads: f.write(f"{lead['urls']},{lead['primary_email']}\n")
        return {"count": len(leads), "file": str(domains_file)}

    def _prospect_smtp(self, cursor, limit, offer, dry_run):
        cursor.execute("SELECT rowid, title, primary_email, sector FROM main WHERE primary_email IS NOT NULL AND primary_email != '' AND (smtp_processed IS NULL OR smtp_processed == '') AND deliverability NOT IN ('rejected', 'bounce') LIMIT ?", (limit,))
        leads = cursor.fetchall()
        if not leads: return {"count": 0}
        offer_data = OFFERS.get(offer, OFFERS["hosting"])
        contacts_file = LOG_DIR / f"prospect_smtp_{offer}.txt"
        if dry_run: return {"count": len(leads), "dry_run": True}
        with open(contacts_file, "w", encoding="utf-8") as f:
            for lead in leads: f.write(lead["primary_email"] + "\n")
        return {"count": len(leads), "file": str(contacts_file)}

    def _prospect_whatsapp(self, cursor, limit, dry_run):
        cursor.execute("SELECT rowid, title, phone, primary_email FROM main WHERE phone IS NOT NULL AND phone != '' AND (whatsapp_received IS NULL OR whatsapp_received == '') LIMIT ?", (limit,))
        leads = cursor.fetchall()
        if not leads: return {"count": 0}
        phones_file = LOG_DIR / "prospect_whatsapp_phones.txt"
        if dry_run: return {"count": len(leads), "dry_run": True}
        with open(phones_file, "w", encoding="utf-8") as f:
            for lead in leads: f.write(f"{lead['phone']}|{lead['title']}|{lead['primary_email']}\n")
        return {"count": len(leads), "file": str(phones_file)}

    def execute(self, **kwargs) -> Dict:
        start_time = time.time()
        results = {}
        do_all = kwargs.get("do_all", False)
        dry_run = kwargs.get("dry_run", False)
        if kwargs.get("do_status"): return self.phase_status()
        if do_all or kwargs.get("do_combine"):
            results["combine"] = self.phase_combine(kwargs.get("keywords_filter", ""), kwargs.get("locations_filter", ""), kwargs.get("keywords_file", ""), kwargs.get("grid_mode", False), kwargs.get("keywordless_mode", False), dry_run)
        if do_all or kwargs.get("do_scrape"):
            results["scrape"] = self.phase_scrape(dry_run, kwargs.get("grid_bbox", ""), kwargs.get("grid_cell", 0.0))
        if do_all or kwargs.get("do_import"):
            results["import"] = self.phase_import(dry_run)
        if do_all or kwargs.get("do_sanitize"):
            results["sanitize"] = self.phase_sanitize(dry_run)
        if do_all or kwargs.get("do_prospect"):
            results["prospect"] = self.phase_prospect(kwargs.get("prospect_channel", "all"), kwargs.get("prospect_limit", 100), kwargs.get("prospect_offer", "hosting"), dry_run)
        return self.finalize(start_time, results)

    def phase_status(self):
        db_stats = {}
        if DB_PATH.exists():
            rows = self._db_query("SELECT COUNT(*) as total FROM main")
            db_stats["total_leads"] = rows[0]["total"] if rows else 0
            rows = self._db_query("SELECT COUNT(DISTINCT primary_email) as emails FROM main WHERE primary_email IS NOT NULL AND primary_email != ''")
            db_stats["emails"] = rows[0]["emails"] if rows else 0
            rows = self._db_query("SELECT COUNT(*) as sites FROM main WHERE urls IS NOT NULL AND urls != ''")
            db_stats["websites"] = rows[0]["sites"] if rows else 0
            rows = self._db_query("SELECT deliverability, COUNT(*) as cnt FROM main WHERE deliverability IS NOT NULL GROUP BY deliverability ORDER BY cnt DESC")
            db_stats["by_score"] = {row["deliverability"]: row["cnt"] for row in rows}
        telemetry = self._load_telemetry()
        db_stats["telemetry_events"] = len(telemetry)
        chunks = list(CHUNKS_DIR.glob("chunk_*.txt")) if CHUNKS_DIR.exists() else []
        csvs = list(OUTPUT_DIR.glob("*.csv")) if OUTPUT_DIR.exists() else []
        db_stats["chunks"] = len(chunks)
        db_stats["scrape_csvs"] = len(csvs)
        return db_stats

    def run_pipeline(**kwargs):
        pipeline = LeadPipeline()
        return pipeline.execute(**kwargs)

    def main():
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("--all", action="store_true")
        parser.add_argument("--combine", action="store_true")
        parser.add_argument("--keywords", default="")
        parser.add_argument("--locations", default="")
        parser.add_argument("--keywords-file", default="")
        parser.add_argument("--grid-mode", action="store_true")
        parser.add_argument("--keywordless-mode", action="store_true")
        parser.add_argument("--grid-bbox", default="")
        parser.add_argument("--grid-cell", type=float, default=0.0)
        parser.add_argument("--scrape", action="store_true")
        parser.add_argument("--import", dest="do_import", action="store_true")
        parser.add_argument("--sanitize", action="store_true")
        parser.add_argument("--prospect", action="store_true")
        parser.add_argument("--channel", default="all")
        parser.add_argument("--limit", type=int, default=100)
        parser.add_argument("--offer", default="hosting")
        parser.add_argument("--status", action="store_true")
        parser.add_argument("--dry-run", action="store_true")
        args = parser.parse_args()
        if args.status and not any([args.all, args.combine, args.scrape, args.do_import, args.sanitize, args.prospect]):
            LeadPipeline().phase_status()
            return
        print(json.dumps(run_pipeline(**vars(args)), indent=2))

    if __name__ == "__main__":
        main()
