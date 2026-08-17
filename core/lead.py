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
Lead Pipeline — Orquestador de prospección y adquisición de leads.

Fases:
  1. Combine   — Generar combinaciones keywords × ubicaciones (chunks)
  2. Scrape    — Scraping Google Maps vía Gosom (Docker o EXE)
  3. Import    — Importar CSVs de gosom → contacts.db
  4. Sanitize  — Normalizar, categorizar, scorear leads
  5. Prospect  — Campañas multicanal (SMTP, forms, WhatsApp)
  6. Telemetry — Logs JSON

Uso:
  python -m core.lead --all
  python -m core.lead --combine --keywords "hosting,seo" --locations "Lanús"
  python -m core.lead --scrape
  python -m core.lead --import
  python -m core.lead --sanitize
  python -m core.lead --prospect --channel smtp --offer hosting --limit 100
  python -m core.lead --status
  python -m core.lead --all --dry-run
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
# Config (from scripts/pipeline/config.py constants)
# ---------------------------------------------------------------------------
GOSOM_DIR = DATA_INPUTS_DIR / "gosom"
SEEDS_DIR = GOSOM_DIR / "seeds"
CHUNKS_DIR = GOSOM_DIR / "chunks"
OUTPUT_DIR = GOSOM_DIR / "output"
KEYWORDS_FILE = SEEDS_DIR / "keywords.txt"
UBICACIONES_FILE = SEEDS_DIR / "ubicaciones.txt"

CHUNK_SIZE = 500
GOSOM_CONCURRENCY = 3
GOSOM_LANG = "es"
GOSOM_DEPTH = 1
GOSOM_ZOOM = 15
GOSOM_RADIUS = 5000
GOSOM_GRID_BBOX = "-34.93,-58.53,-34.36,-58.10"  # CABA completo
GOSOM_GRID_CELL = 1.0  # Celdas de 1km
GOSOM_PBA_BBOX = "-39.0,-63.5,-33.5,-56.5"  # Provincia de Buenos Aires completa
CSV_PARTIAL_ROWS = 500  # Filas por CSV parcial
CHECKPOINT_FILE = GOSOM_DIR / "checkpoint.json"
POLL_INTERVAL = 30  # Segundos entre polls del CSV

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
    "Tecnología": ["informatica", "computacion", "sistemas", "soporte tecnico",
                    "reparacion", "tecnico", "web", "hosting", "programacion",
                    "desarrollo", "software", "app", "digital"],
    "Salud": ["medico", "clinica", "hospital", "odontologo", "farmacia",
              "kinesiologo", "psicologo", "nutricionista", "veterinaria"],
    "Comercio": ["almacen", "supermercado", "kiosco", "tienda", "comercio",
                 "local", "venta", "negocio"],
    "Gastronomía": ["restaurante", "bar", "cafeteria", "pizzeria", "heladeria",
                    "rotiseria", "panaderia", "pasteleria", "hamburgueseria"],
    "Industria": ["taller", "metalurgica", "mecanizado", "fabrica", "industrial",
                  "portones", "calderas", "soldador", "toldos"],
    "Servicios": ["abogado", "contador", "escribano", "seguro", "inmobiliaria",
                  "consultora", "asesoria", "arquitecto", "ingeniero"],
    "Educación": ["escuela", "colegio", "instituto", "profesor", "curso",
                  "capacitacion", "universidad", "academia"],
    "Transporte": ["motos", "bicicletas", "grua", "auxilio", "taxi", "remis",
                   "mudanza", "flete", "logistica"],
    "Construcción": ["construccion", "obra", "plomeria", "electricista",
                     "carpinteria", "pintura", "cerrajero", "vidrieria"],
}

DEFAULT_OFFER_HOSTING = (
    "Hola, ¿todo bien? Te escribo porque vi que tienen presencia en Google Maps "
    "y quería saber si están conformes con su sitio web y hosting actual. En LANUS "
    "COMPUTACION estamos ofreciendo una promo de hosting en Cloudflare con rendimiento "
    "mejorado y seguridad incluida, a un precio muy accesible. Sin compromiso, ¿puedo "
    "compartirte más info? Saludos!"
)

OFFERS = {
    "hosting": {
        "asunto": "Promo Hosting Cloudflare - LANUS COMPUTACION",
        "mensaje": DEFAULT_OFFER_HOSTING,
    },
    "web": {
        "asunto": "Rediseño de sitio web - LANUS COMPUTACION",
        "mensaje": (
            "Hola, vi su comercio en Google Maps y noté que podrían "
            "mejorar su presencia web. Ofrecemos diseños modernos y "
            "económicos. Sin compromiso, ¿puedo enviarles info?"
        ),
    },
    "seo": {
        "asunto": "Posicionamiento Web - LANUS COMPUTACION",
        "mensaje": (
            "Hola, ofrecemos servicios de SEO para que su negocio "
            "aparezca primero en Google. ¿Les interesaría una "
            "auditoría gratuita?"
        ),
    },
}

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_DIR = ROOT_DIR / "logs" / "pipeline"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger("lead")
logger.setLevel(logging.INFO)

_console = logging.StreamHandler()
_console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S"))
logger.addHandler(_console)

_file_handler = logging.FileHandler(LOG_DIR / "lead.log", encoding="utf-8")
_file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(_file_handler)


# ---------------------------------------------------------------------------
# Telemetry
# ---------------------------------------------------------------------------
TELEMETRY_PATH = LOG_DIR / "lead_execution_log.json"


def _load_telemetry() -> List[Dict]:
    if TELEMETRY_PATH.exists():
        try:
            return json.loads(TELEMETRY_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []


def _save_telemetry(entries: List[Dict]) -> None:
    TELEMETRY_PATH.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")


def _log_event(event_type: str, detail: Dict[str, Any]) -> None:
    entries = _load_telemetry()
    entries.append({
        "ts": datetime.now().isoformat(),
        "pipeline": "lead",
        "event": event_type,
        **detail,
    })
    _save_telemetry(entries)
    logger.info("Telemetry: %s", event_type)


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


# ---------------------------------------------------------------------------
# Phase 1: Combine (keywords × locations → chunks)
# ---------------------------------------------------------------------------

def phase_combine(
    keywords_filter: str = "",
    locations_filter: str = "",
    keywords_file: str = "",
    grid_mode: bool = False,
    keywordless_mode: bool = False,
    dry_run: bool = False,
) -> Dict:
    logger.info("=== FASE 1: Combine ===")

    def _load_lines(filepath: Path) -> List[str]:
        if not filepath.exists():
            logger.error("Archivo no encontrado: %s", filepath)
            return []
        with open(filepath, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]

    # Load keywords from specified file or default
    kw_file = Path(keywords_file) if keywords_file else KEYWORDS_FILE
    keywords = _load_lines(kw_file)
    
    if keywordless_mode:
        ubicaciones = _load_lines(UBICACIONES_FILE)

        if locations_filter:
            filtros = [l.strip().lower() for l in locations_filter.split(",")]
            ubicaciones = [u for u in ubicaciones if any(f in u.lower() for f in filtros)]

        if not ubicaciones:
            logger.error("No hay ubicaciones disponibles")
            return {"ok": False, "error": "empty_locations"}

        queries = []
        for loc in ubicaciones:
            for proxy in KEYWORDLESS_PROXY_CATEGORIES:
                queries.append(f"{proxy} {loc}")
            queries.append(loc)

        total = len(queries)
        logger.info("  Modo KEYWORDLESS activado | Ubicaciones: %d | Queries: %d | Proxys: %s",
                    len(ubicaciones), total, ",".join(KEYWORDLESS_PROXY_CATEGORIES))

        if dry_run:
            logger.info("  [DRY-RUN] Se generarian %d queries en chunks de %d", total, CHUNK_SIZE)
            return {"ok": True, "dry_run": True, "total": total}

        CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

        for f in CHUNKS_DIR.glob("chunk_*.txt"):
            f.unlink()

        chunk_num = 1
        current_lines: List[str] = []

        for q in queries:
            current_lines.append(q)
            if len(current_lines) >= CHUNK_SIZE:
                _write_chunk(chunk_num, current_lines)
                current_lines = []
                chunk_num += 1

        if current_lines:
            _write_chunk(chunk_num, current_lines)
            chunk_num += 1

        logger.info("  Chunks generados: %d", chunk_num - 1)
        _log_event("combine", {"keywords": 0, "locations": len(ubicaciones), "chunks": chunk_num - 1, "keywordless_mode": True})
        return {"ok": True, "chunks": chunk_num - 1, "total": total, "keywordless_mode": True}

    elif grid_mode:
        # Grid mode: keywords only, no locations needed (grid handles geo)
        logger.info("  Modo GRID activado (grid-bbox maneja la ubicación)")
        
        if keywords_filter:
            filtros = [k.strip().lower() for k in keywords_filter.split(",")]
            keywords = [k for k in keywords if any(f in k.lower() for f in filtros)]
        
        if not keywords:
            logger.error("No hay keywords disponibles")
            return {"ok": False, "error": "empty_keywords"}
        
        total = len(keywords)
        logger.info("  Keywords: %d (grid-bbox: %s)", total, GOSOM_GRID_BBOX)
        
        if dry_run:
            logger.info("  [DRY-RUN] Se generarían %d queries en chunks de %d", total, CHUNK_SIZE)
            return {"ok": True, "dry_run": True, "total": total}
        
        CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Clean old chunks
        for f in CHUNKS_DIR.glob("chunk_*.txt"):
            f.unlink()
        
        chunk_num = 1
        current_lines: List[str] = []
        
        for kw in keywords:
            current_lines.append(kw)
            if len(current_lines) >= CHUNK_SIZE:
                _write_chunk(chunk_num, current_lines)
                current_lines = []
                chunk_num += 1
        
        if current_lines:
            _write_chunk(chunk_num, current_lines)
            chunk_num += 1
        
        logger.info("  Chunks generados: %d", chunk_num - 1)
        _log_event("combine", {"keywords": len(keywords), "locations": 0, "chunks": chunk_num - 1, "grid_mode": True})
        return {"ok": True, "chunks": chunk_num - 1, "total": total, "grid_mode": True}
    
    else:
        # Traditional mode: keywords × locations
        ubicaciones = _load_lines(UBICACIONES_FILE)
        
        if keywords_filter:
            filtros = [k.strip().lower() for k in keywords_filter.split(",")]
            keywords = [k for k in keywords if any(f in k.lower() for f in filtros)]
        if locations_filter:
            filtros = [l.strip().lower() for l in locations_filter.split(",")]
            ubicaciones = [u for u in ubicaciones if any(f in u.lower() for f in filtros)]
        
        if not keywords or not ubicaciones:
            logger.error("No hay keywords o ubicaciones disponibles")
            return {"ok": False, "error": "empty_seeds"}
        
        total = len(keywords) * len(ubicaciones)
        logger.info("  Keywords: %d × Ubicaciones: %d = %d combinaciones", len(keywords), len(ubicaciones), total)
        
        if dry_run:
            logger.info("  [DRY-RUN] Se generarían %d combinaciones en chunks de %d", total, CHUNK_SIZE)
            return {"ok": True, "dry_run": True, "total": total}
        
        CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Clean old chunks
        for f in CHUNKS_DIR.glob("chunk_*.txt"):
            f.unlink()
        
        chunk_num = 1
        current_lines: List[str] = []
        
        for kw in keywords:
            for loc in ubicaciones:
                current_lines.append(f"{kw} {loc}")
                if len(current_lines) >= CHUNK_SIZE:
                    _write_chunk(chunk_num, current_lines)
                    current_lines = []
                    chunk_num += 1
        
        if current_lines:
            _write_chunk(chunk_num, current_lines)
            chunk_num += 1
        
        logger.info("  Chunks generados: %d", chunk_num - 1)
        _log_event("combine", {"keywords": len(keywords), "locations": len(ubicaciones), "chunks": chunk_num - 1})
        return {"ok": True, "chunks": chunk_num - 1, "total": total}


def _write_chunk(num: int, lines: List[str]) -> None:
    path = CHUNKS_DIR / f"chunk_{num:03d}.txt"
    with open(path, "w", encoding="ascii", errors="replace") as f:
        f.write("\n".join(lines) + "\n")
    logger.info("  ✓ chunk_%03d.txt (%d líneas)", num, len(lines))


# ---------------------------------------------------------------------------
# Checkpoint helpers (resume + partial CSV delivery)
# ---------------------------------------------------------------------------

def _load_checkpoint() -> Dict:
    if CHECKPOINT_FILE.exists():
        try:
            return json.loads(CHECKPOINT_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {"completed": {}, "partials": {}}
    return {"completed": {}, "partials": {}}


def _save_checkpoint(data: Dict) -> None:
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _mark_chunk_done(checkpoint: Dict, chunk_name: str, rows: int) -> None:
    checkpoint["completed"][chunk_name] = {
        "ts": datetime.now().isoformat(),
        "rows": rows,
    }
    _save_checkpoint(checkpoint)


def _split_csv_into_partials(csv_path: Path, checkpoint: Dict) -> int:
    """Split a CSV into partial files of CSV_PARTIAL_ROWS rows each."""
    if not csv_path.exists():
        return 0

    try:
        with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                return 0

            part_num = 1
            row_count = 0
            total_rows = 0
            part_file = None
            part_writer = None

            for row in reader:
                if row_count == 0:
                    part_path = OUTPUT_DIR / f"{csv_path.stem}_part{part_num:04d}.csv"
                    part_file = open(part_path, "w", encoding="utf-8", newline="")
                    part_writer = csv.writer(part_file)
                    part_writer.writerow(header)

                part_writer.writerow(row)
                row_count += 1
                total_rows += 1

                if row_count >= CSV_PARTIAL_ROWS:
                    part_file.close()
                    checkpoint["partials"][part_path.name] = {
                        "ts": datetime.now().isoformat(),
                        "rows": row_count,
                    }
                    _save_checkpoint(checkpoint)
                    logger.info("  ✓ Partial: %s (%d filas)", part_path.name, row_count)
                    part_num += 1
                    row_count = 0

            if part_file and row_count > 0:
                part_file.close()
                checkpoint["partials"][part_path.name] = {
                    "ts": datetime.now().isoformat(),
                    "rows": row_count,
                }
                _save_checkpoint(checkpoint)
                logger.info("  ✓ Partial: %s (%d filas)", part_path.name, row_count)

            return total_rows

    except Exception as e:
        logger.error("  Error spliteando %s: %s", csv_path.name, e)
        return 0


# ---------------------------------------------------------------------------
# Phase 2: Scrape (Gosom Docker or EXE)
# ---------------------------------------------------------------------------

def phase_scrape(dry_run: bool = False, grid_bbox: str = "", grid_cell: float = 0.0) -> Dict:
    logger.info("=== FASE 2: Scrape (Gosom) ===")

    # Check if Docker is available
    docker_ok = False
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True, timeout=10)
        docker_ok = result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    if docker_ok:
        return _scrape_docker(dry_run, grid_bbox, grid_cell)
    else:
        return _scrape_exe(dry_run, grid_bbox, grid_cell)


def _scrape_docker(dry_run: bool, grid_bbox: str = "", grid_cell: float = 0.0) -> Dict:
    logger.info("  Usando Gosom vía Docker")

    if dry_run:
        logger.info("  [DRY-RUN] Gosom Docker would scrape chunks")
        return {"ok": True, "dry_run": True, "method": "docker"}

    chunks = list(CHUNKS_DIR.glob("chunk_*.txt"))
    if not chunks:
        logger.warning("  No hay chunks para scrape — ejecutá --combine primero")
        return {"ok": False, "error": "no_chunks"}

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for chunk_file in chunks:
        logger.info("  Scrapeando chunk: %s", chunk_file.name)
        try:
            result = subprocess.run(
                [
                    "docker", "run", "--rm",
                    "-v", f"{GOSOM_DIR}:/data",
                    "gosom/google-maps-scraper:latest",
                    "-i", f"/data/chunks/{chunk_file.name}",
                    "-o", "/data/output",
                    "-lang", GOSOM_LANG,
                    "-depth", str(GOSOM_DEPTH),
                    "-concurrency", str(GOSOM_CONCURRENCY),
                ],
                capture_output=True,
                text=True,
                timeout=1800,
                cwd=str(ROOT_DIR),
            )
            if result.returncode != 0:
                logger.warning("  Gosom error en %s: %s", chunk_file.name, result.stderr[:300])
            else:
                logger.info("  ✓ %s completado", chunk_file.name)
        except subprocess.TimeoutExpired:
            logger.error("  Timeout en chunk %s", chunk_file.name)
        except Exception as e:
            logger.error("  Error ejecutando Gosom Docker: %s", e)

    _log_event("scrape", {"method": "docker", "chunks": len(chunks)})
    return {"ok": True, "method": "docker", "chunks_processed": len(chunks)}


def _count_csv_rows(csv_path: Path) -> int:
    """Count data rows in a CSV (without reading all into memory)."""
    if not csv_path.exists():
        return 0
    try:
        with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            return sum(1 for _ in reader)
    except Exception:
        return 0


def _split_csv_incremental(csv_path: Path, checkpoint: Dict, last_split_row: int) -> int:
    """Split CSV from last_split_row onward into new partial files.

    Returns the new total row count after splitting.
    Only creates new partials for rows beyond what was already split.
    """
    if not csv_path.exists():
        return last_split_row

    try:
        with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header:
                return last_split_row

            # Determine next part number from existing partials
            existing_parts = sorted(
                [k for k in checkpoint.get("partials", {}) if k.startswith(csv_path.stem)],
            )
            part_num = len(existing_parts) + 1
            row_idx = 0
            part_row_count = 0
            part_file = None
            part_writer = None
            new_partials_created = 0

            for row in reader:
                row_idx += 1
                if row_idx <= last_split_row:
                    continue  # skip already-split rows

                if part_row_count == 0:
                    part_path = OUTPUT_DIR / f"{csv_path.stem}_part{part_num:04d}.csv"
                    part_file = open(part_path, "w", encoding="utf-8", newline="")
                    part_writer = csv.writer(part_file)
                    part_writer.writerow(header)

                part_writer.writerow(row)
                part_row_count += 1

                if part_row_count >= CSV_PARTIAL_ROWS:
                    part_file.close()
                    checkpoint["partials"][part_path.name] = {
                        "ts": datetime.now().isoformat(),
                        "rows": part_row_count,
                    }
                    _save_checkpoint(checkpoint)
                    logger.info("  ✓ Partial: %s (%d filas, total %d)",
                                part_path.name, part_row_count, row_idx)
                    new_partials_created += 1
                    part_num += 1
                    part_row_count = 0

            # Flush remaining rows
            if part_file and part_row_count > 0:
                part_file.close()
                checkpoint["partials"][part_path.name] = {
                    "ts": datetime.now().isoformat(),
                    "rows": part_row_count,
                }
                _save_checkpoint(checkpoint)
                logger.info("  ✓ Partial: %s (%d filas, total %d)",
                            part_path.name, part_row_count, row_idx)
                new_partials_created += 1

            return row_idx

    except Exception as e:
        logger.error("  Error en split incremental %s: %s", csv_path.name, e)
        return last_split_row


def _scrape_exe(dry_run: bool, grid_bbox: str = "", grid_cell: float = 0.0) -> Dict:
    logger.info("  Usando Gosom vía EXE local (Popen + polling)")

    # Find the EXE
    exe_path = GOSOM_DIR / "google_maps_scraper-1.3.0-windows-amd64.exe"
    if not exe_path.exists():
        exes = list(GOSOM_DIR.glob("*.exe"))
        if exes:
            exe_path = exes[0]
            logger.info("  EXE encontrado: %s", exe_path.name)
        else:
            logger.error("  No se encontró Gosom EXE ni Docker.")
            return {"ok": False, "error": "gosom_not_found"}

    if dry_run:
        logger.info("  [DRY-RUN] Gosom EXE would scrape chunks")
        return {"ok": True, "dry_run": True, "method": "exe"}

    chunks = list(CHUNKS_DIR.glob("chunk_*.txt"))
    if not chunks:
        logger.warning("  No hay chunks para scrape — ejecutá --combine primero")
        return {"ok": False, "error": "no_chunks"}

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    checkpoint = _load_checkpoint()
    bbox_val = grid_bbox or GOSOM_GRID_BBOX
    cell_val = grid_cell or GOSOM_GRID_CELL

    # Resume: skip already-completed chunks
    pending = []
    for c in sorted(chunks):
        if c.name in checkpoint["completed"]:
            logger.info("  ⏩ SKIP (ya completado): %s (%d filas)",
                        c.name, checkpoint["completed"][c.name].get("rows", 0))
        else:
            pending.append(c)

    if not pending:
        logger.info("  Todos los chunks ya fueron procesados. Nada para hacer.")
        return {"ok": True, "method": "exe", "skipped": len(chunks), "processed": 0}

    logger.info("  Chunks: %d total | %d skip | %d pendientes",
                len(chunks), len(chunks) - len(pending), len(pending))

    processed = 0
    total_rows = 0

    for chunk_file in pending:
        csv_path = OUTPUT_DIR / f"{chunk_file.stem}.csv"

        # Remove stale CSV from aborted run (no checkpoint = incomplete)
        if csv_path.exists() and chunk_file.name not in checkpoint["completed"]:
            logger.info("  Limpiando CSV previo (sin checkpoint): %s", csv_path.name)
            csv_path.unlink(missing_ok=True)
            # Also clean old partials for this chunk
            for old_partial in OUTPUT_DIR.glob(f"{chunk_file.stem}_part*.csv"):
                old_partial.unlink(missing_ok=True)
                checkpoint["partials"].pop(old_partial.name, None)
            _save_checkpoint(checkpoint)

        logger.info("  Scrapeando chunk: %s (grid-bbox=%s, depth=%d, cell=%.1fkm)",
                    chunk_file.name, bbox_val, GOSOM_DEPTH, cell_val)

        try:
            log_file = open(GOSOM_DIR / "gosom_live.log", "w",
                            encoding="utf-8", errors="replace")

            proc = subprocess.Popen(
                [
                    str(exe_path),
                    "-input", str(chunk_file),
                    "-results", str(csv_path),
                    "-lang", GOSOM_LANG,
                    "-depth", str(GOSOM_DEPTH),
                    "-c", str(GOSOM_CONCURRENCY),
                    "-email",
                    "-disable-page-reuse",
                    "-grid-bbox", bbox_val,
                    "-grid-cell", str(cell_val),
                    "-zoom", str(GOSOM_ZOOM),
                ],
                stdout=log_file,
                stderr=subprocess.STDOUT,
                cwd=str(GOSOM_DIR),
            )

            # Polling loop: monitor CSV growth, generate partials + checkpoint
            last_split_row = 0
            last_rows_seen = 0
            stale_count = 0
            MAX_STALE = 240  # ~2hr sin filas nuevas → asumir terminado (240 polls × 30s)

            logger.info("  Polling cada %ds | partials cada %d filas", POLL_INTERVAL, CSV_PARTIAL_ROWS)

            while True:
                proc.poll()

                current_rows = _count_csv_rows(csv_path)
                if current_rows > last_rows_seen:
                    stale_count = 0
                    last_rows_seen = current_rows
                    logger.info("  📊 %d filas", current_rows)
                else:
                    stale_count += 1

                # Incremental partial split when crossing 1000-row boundaries
                if current_rows >= last_split_row + CSV_PARTIAL_ROWS:
                    last_split_row = _split_csv_incremental(csv_path, checkpoint, last_split_row)

                # Process finished
                if proc.returncode is not None:
                    logger.info("  Gosom terminó (rc=%d)", proc.returncode)
                    log_file.close()

                    # Final incremental split (captures remaining rows)
                    final_rows = _count_csv_rows(csv_path)
                    if final_rows > last_split_row:
                        last_split_row = _split_csv_incremental(csv_path, checkpoint, last_split_row)

                    _mark_chunk_done(checkpoint, chunk_file.name, final_rows)
                    processed += 1
                    total_rows += final_rows
                    logger.info("  ✓ %s completado: %d filas, %d parciales",
                                chunk_file.name, final_rows,
                                sum(1 for k in checkpoint["partials"]
                                    if k.startswith(chunk_file.stem)))
                    break

                # Stale detection: no new rows for ~1hr → process likely hung/finished
                if stale_count >= MAX_STALE:
                    logger.warning("  ⚠ Sin filas nuevas por %d polls (~%dmin). Terminando proceso.",
                                   stale_count, stale_count * POLL_INTERVAL // 60)
                    proc.terminate()
                    try:
                        proc.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                    log_file.close()

                    final_rows = _count_csv_rows(csv_path)
                    if final_rows > last_split_row:
                        last_split_row = _split_csv_incremental(csv_path, checkpoint, last_split_row)

                    if final_rows > 0:
                        _mark_chunk_done(checkpoint, chunk_file.name, final_rows)
                        processed += 1
                        total_rows += final_rows
                        logger.info("  ✓ %s (stale-terminated): %d filas", chunk_file.name, final_rows)
                    else:
                        logger.error("  ✗ %s: proceso colgado sin datos", chunk_file.name)
                    break

                time.sleep(POLL_INTERVAL)

        except Exception as e:
            logger.error("  Error en Popen+polling para %s: %s", chunk_file.name, e)
            # Try to kill process if still running
            try:
                if proc.poll() is None:
                    proc.kill()
                if log_file and not log_file.closed:
                    log_file.close()
            except Exception:
                pass

            # Emergency: count what we have and save checkpoint
            emergency_rows = _count_csv_rows(csv_path)
            if emergency_rows > 0:
                _split_csv_incremental(csv_path, checkpoint, 0)
                _mark_chunk_done(checkpoint, chunk_file.name, emergency_rows)
                processed += 1
                total_rows += emergency_rows
                logger.info("  ✓ %s (emergency save): %d filas preservadas",
                            chunk_file.name, emergency_rows)

    _log_event("scrape", {
        "method": "exe",
        "chunks_total": len(chunks),
        "chunks_processed": processed,
        "chunks_skipped": len(chunks) - len(pending),
        "total_rows": total_rows,
    })
    return {
        "ok": True,
        "method": "exe",
        "chunks_processed": processed,
        "chunks_skipped": len(chunks) - len(pending),
        "total_rows": total_rows,
    }


# ---------------------------------------------------------------------------
# Phase 3: Import (CSVs → contacts.db)
# ---------------------------------------------------------------------------

def phase_import(dry_run: bool = False) -> Dict:
    logger.info("=== FASE 3: Import (CSV → DB) ===")

    if not DB_PATH.exists():
        logger.error("DB no encontrada: %s", DB_PATH)
        return {"ok": False, "error": "db_missing"}

    # Get existing emails
    existing_emails = set()
    rows = _db_query("SELECT primary_email FROM main WHERE primary_email IS NOT NULL")
    for row in rows:
        if row.get("primary_email"):
            existing_emails.add(row["primary_email"].lower())

    # Find CSVs
    csv_files = list(OUTPUT_DIR.glob("*.csv"))
    if not csv_files:
        # Also check gosom output directly
        csv_files = list(GOSOM_DIR.glob("*.csv"))
    if not csv_files:
        logger.warning("  No hay CSVs para importar")
        return {"ok": True, "imported": 0, "skipped": 0, "note": "no_csvs"}

    total_new = 0
    total_skip = 0

    for csv_file in csv_files:
        if csv_file.name.startswith("chunk_"):
            continue
        try:
            with open(csv_file, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Normalize emails
                    email_str = row.get("emails", "") or row.get("email", "")
                    emails = [
                        e.strip().lower()
                        for e in email_str.replace("[", "").replace("]", "").replace("'", "").split(",")
                        if e.strip()
                    ]
                    if not emails:
                        total_skip += 1
                        continue

                    primary_email = emails[0]
                    if primary_email in existing_emails:
                        total_skip += 1
                        continue

                    title = row.get("title", "")
                    sector = row.get("category", "")
                    phone = row.get("phone", "")
                    address = row.get("complete_address") or row.get("address", "")
                    google_maps = row.get("link", "")
                    website = row.get("website", "")
                    other_emails = ",".join(emails[1:]) if len(emails) > 1 else ""

                    if dry_run:
                        logger.info("  [DRY-RUN] Nuevo: %s <%s>", title, primary_email)
                        continue

                    try:
                        _db_query("""
                            INSERT INTO main (
                                title, sector, primary_email, other_emails, phone,
                                address, google_maps, urls, country,
                                list, date_added
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, date('now'))
                        """, (
                            title, sector, primary_email, other_emails, phone,
                            address, google_maps, website, "",
                            "gosom_auto",
                        ), fetch=False)
                        existing_emails.add(primary_email)
                        total_new += 1
                    except sqlite3.Error as e:
                        logger.error("  Error insertando %s: %s", primary_email, e)

            logger.info("  ✓ %s procesado", csv_file.name)
        except Exception as e:
            logger.error("  Error con %s: %s", csv_file.name, e)

    logger.info("  Nuevos: %d | Saltados: %d", total_new, total_skip)
    _log_event("import", {"new": total_new, "skipped": total_skip, "csvs": len(csv_files)})
    return {"ok": True, "imported": total_new, "skipped": total_skip}


# ---------------------------------------------------------------------------
# Phase 4: Sanitize (normalize, classify, score)
# ---------------------------------------------------------------------------

def phase_sanitize(dry_run: bool = False) -> Dict:
    logger.info("=== FASE 4: Sanitize ===")

    if not DB_PATH.exists():
        logger.error("DB no encontrada: %s", DB_PATH)
        return {"ok": False, "error": "db_missing"}

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get column info
    cursor.execute("PRAGMA table_info(main)")
    columns = [col[1] for col in cursor.fetchall()]
    col_set = set(columns)

    cursor.execute("SELECT rowid, * FROM main")
    rows = cursor.fetchall()
    logger.info("  Leads en DB: %d", len(rows))

    stats = {"normalized": 0, "reclassified": 0, "scored": 0, "errors": 0}

    for row in rows:
        rowid = row["rowid"]
        title = row["title"] or ""
        sector_orig = row["sector"] or ""

        # Normalize title
        new_title = re.sub(r"\s+", " ", title).strip()

        # Classify sector
        text = f"{title} {sector_orig}".lower()
        new_sector = sector_orig
        for sector, keywords in SECTOR_KEYWORDS.items():
            for kw in keywords:
                if kw in text:
                    new_sector = sector
                    break
            if new_sector != sector_orig:
                break
        if not new_sector:
            new_sector = "General"

        # Score
        score = 0
        if "urls" in col_set and row["urls"] and str(row["urls"]).strip():
            score += LEAD_SCORE_WEIGHTS["website"]
        if "primary_email" in col_set and row["primary_email"] and str(row["primary_email"]).strip():
            score += LEAD_SCORE_WEIGHTS["email"]
        if "phone" in col_set and row["phone"] and str(row["phone"]).strip():
            score += LEAD_SCORE_WEIGHTS["phone"]
        if "review_rating" in col_set:
            try:
                rating = float(row["review_rating"] or 0)
                if rating >= 4.0:
                    score += LEAD_SCORE_WEIGHTS["rating"]
            except (ValueError, TypeError):
                pass

        if new_title != title:
            stats["normalized"] += 1
        if new_sector != sector_orig:
            stats["reclassified"] += 1

        score_label = "caliente" if score >= 50 else "tibio" if score >= 25 else "frio"

        if dry_run:
            if new_title != title or new_sector != sector_orig:
                logger.info("  [DRY-RUN] %d: '%s' -> '%s' [%s -> %s] score:%d",
                            rowid, title[:40], new_title[:40], sector_orig, new_sector, score)
            continue

        try:
            cursor.execute("""
                UPDATE main SET title = ?, sector = ?, deliverability = ?
                WHERE rowid = ?
            """, (new_title, new_sector, score_label, rowid))
            stats["scored"] += 1
        except sqlite3.Error as e:
            stats["errors"] += 1

    if not dry_run:
        conn.commit()
    conn.close()

    logger.info("  Normalizados: %d | Re-categorizados: %d | Scoreados: %d | Errores: %d",
                stats["normalized"], stats["reclassified"], stats["scored"], stats["errors"])
    _log_event("sanitize", stats)
    return {"ok": True, **stats}


# ---------------------------------------------------------------------------
# Phase 5: Prospect (multichannel outreach)
# ---------------------------------------------------------------------------

def phase_prospect(
    channel: str = "all",
    limit: int = 100,
    offer: str = "hosting",
    dry_run: bool = False,
) -> Dict:
    logger.info("=== FASE 5: Prospect (canal=%s, oferta=%s, límite=%d) ===", channel, offer, limit)

    if not DB_PATH.exists():
        logger.error("DB no encontrada: %s", DB_PATH)
        return {"ok": False, "error": "db_missing"}

    channels = ["forms", "smtp", "whatsapp"] if channel == "all" else [channel]
    results = {}

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    for ch in channels:
        if ch == "forms":
            results["forms"] = _prospect_forms(cursor, limit, dry_run)
        elif ch == "smtp":
            results["smtp"] = _prospect_smtp(cursor, limit, offer, dry_run)
        elif ch == "whatsapp":
            results["whatsapp"] = _prospect_whatsapp(cursor, limit, dry_run)

    conn.close()
    _log_event("prospect", {"channel": channel, "offer": offer, "limit": limit, "results": results})
    return {"ok": True, **results}


def _prospect_forms(cursor, limit: int, dry_run: bool) -> Dict:
    cursor.execute("""
        SELECT rowid, title, urls, primary_email
        FROM main
        WHERE urls IS NOT NULL AND urls != ''
          AND (form_processed IS NULL OR form_processed = '')
          AND deliverability != 'rechazado'
        LIMIT ?
    """, (limit,))
    leads = cursor.fetchall()

    if not leads:
        logger.info("  [Forms] No hay leads con website para prospectar")
        return {"count": 0}

    domains_file = LOG_DIR / "prospect_forms_domains.txt"
    if dry_run:
        logger.info("  [Forms][DRY-RUN] %d leads con website", len(leads))
        return {"count": len(leads), "dry_run": True}

    with open(domains_file, "w", encoding="utf-8") as f:
        for lead in leads:
            f.write(f"{lead['urls']},{lead['primary_email']}\n")

    logger.info("  [Forms] %d leads escritos en %s", len(leads), domains_file)
    return {"count": len(leads), "file": str(domains_file)}


def _prospect_smtp(cursor, limit: int, offer: str, dry_run: bool) -> Dict:
    cursor.execute("""
        SELECT rowid, title, primary_email, sector
        FROM main
        WHERE primary_email IS NOT NULL AND primary_email != ''
          AND (smtp_processed IS NULL OR smtp_processed = '')
          AND deliverability NOT IN ('rechazado', 'bounce')
        LIMIT ?
    """, (limit,))
    leads = cursor.fetchall()

    if not leads:
        logger.info("  [SMTP] No hay leads con email para prospectar")
        return {"count": 0}

    offer_data = OFFERS.get(offer, OFFERS["hosting"])
    contacts_file = LOG_DIR / f"prospect_smtp_{offer}.txt"

    if dry_run:
        logger.info("  [SMTP][DRY-RUN] %d leads con email", len(leads))
        return {"count": len(leads), "dry_run": True}

    with open(contacts_file, "w", encoding="utf-8") as f:
        for lead in leads:
            f.write(lead["primary_email"] + "\n")

    logger.info("  [SMTP] %d contactos escritos en %s", len(leads), contacts_file)
    logger.info("  [SMTP] Para ejecutar: python scripts/e-mail_marketing_manager/e-mail.py")
    return {"count": len(leads), "file": str(contacts_file)}


def _prospect_whatsapp(cursor, limit: int, dry_run: bool) -> Dict:
    cursor.execute("""
        SELECT rowid, title, phone, primary_email
        FROM main
        WHERE phone IS NOT NULL AND phone != ''
          AND (whatsapp_received IS NULL OR whatsapp_received = '')
        LIMIT ?
    """, (limit,))
    leads = cursor.fetchall()

    if not leads:
        logger.info("  [WhatsApp] No hay leads con teléfono para prospectar")
        return {"count": 0}

    phones_file = LOG_DIR / "prospect_whatsapp_phones.txt"
    if dry_run:
        logger.info("  [WhatsApp][DRY-RUN] %d leads con teléfono", len(leads))
        return {"count": len(leads), "dry_run": True}

    with open(phones_file, "w", encoding="utf-8") as f:
        for lead in leads:
            f.write(f"{lead['phone']}|{lead['title']}|{lead['primary_email']}\n")

    logger.info("  [WhatsApp] %d contactos escritos en %s", len(leads), phones_file)
    return {"count": len(leads), "file": str(phones_file)}


# ---------------------------------------------------------------------------
# Phase 6: Status
# ---------------------------------------------------------------------------

def phase_status() -> Dict:
    logger.info("=== FASE 6: Status ===")

    # DB stats
    db_stats = {}
    if DB_PATH.exists():
        rows = _db_query("SELECT COUNT(*) as total FROM main")
        db_stats["total_leads"] = rows[0]["total"] if rows else 0

        rows = _db_query("SELECT COUNT(DISTINCT primary_email) as emails FROM main WHERE primary_email IS NOT NULL AND primary_email != ''")
        db_stats["emails"] = rows[0]["emails"] if rows else 0

        rows = _db_query("SELECT COUNT(*) as sites FROM main WHERE urls IS NOT NULL AND urls != ''")
        db_stats["websites"] = rows[0]["sites"] if rows else 0

        rows = _db_query("SELECT deliverability, COUNT(*) as cnt FROM main WHERE deliverability IS NOT NULL GROUP BY deliverability ORDER BY cnt DESC")
        db_stats["by_score"] = {row["deliverability"]: row["cnt"] for row in rows}

    # Telemetry stats
    telemetry = _load_telemetry()
    db_stats["telemetry_events"] = len(telemetry)

    # Gosom stats
    chunks = list(CHUNKS_DIR.glob("chunk_*.txt")) if CHUNKS_DIR.exists() else []
    csvs = list(OUTPUT_DIR.glob("*.csv")) if OUTPUT_DIR.exists() else []
    db_stats["chunks"] = len(chunks)
    db_stats["scrape_csvs"] = len(csvs)

    logger.info("  Total leads: %d", db_stats.get("total_leads", 0))
    logger.info("  Emails: %d | Websites: %d", db_stats.get("emails", 0), db_stats.get("websites", 0))
    logger.info("  Chunks: %d | CSVs scrapeados: %d", db_stats.get("chunks", 0), db_stats.get("scrape_csvs", 0))

    return db_stats


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def run_pipeline(
    do_all: bool = False,
    do_combine: bool = False,
    keywords_filter: str = "",
    locations_filter: str = "",
    keywords_file: str = "",
    grid_mode: bool = False,
    keywordless_mode: bool = False,
    grid_bbox: str = "",
    grid_cell: float = 0.0,
    do_scrape: bool = False,
    do_import: bool = False,
    do_sanitize: bool = False,
    do_prospect: bool = False,
    prospect_channel: str = "all",
    prospect_limit: int = 100,
    prospect_offer: str = "hosting",
    do_status: bool = False,
    dry_run: bool = False,
) -> Dict:
    results = {}
    start = datetime.now()
    logger.info("Pipeline Lead iniciado")

    try:
        if do_status:
            results["status"] = phase_status()
            return results

        if do_all or do_combine:
            results["combine"] = phase_combine(keywords_filter, locations_filter, keywords_file, grid_mode, keywordless_mode, dry_run)

        if do_all or do_scrape:
            results["scrape"] = phase_scrape(dry_run, grid_bbox, grid_cell)

        if do_all or do_import:
            results["import"] = phase_import(dry_run)

        if do_all or do_sanitize:
            results["sanitize"] = phase_sanitize(dry_run)

        if do_all or do_prospect:
            results["prospect"] = phase_prospect(prospect_channel, prospect_limit, prospect_offer, dry_run)

    except Exception as e:
        logger.error("Error en pipeline: %s", e)
        results["error"] = str(e)

    elapsed = (datetime.now() - start).total_seconds()
    logger.info("Pipeline completado en %.1fs", elapsed)

    _log_event("pipeline_complete", {"elapsed_s": round(elapsed, 1), "results": results})
    return results


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Lead Pipeline — Prospección y adquisición de leads",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--all", action="store_true", help="Ejecutar todas las fases en orden")
    parser.add_argument("--combine", action="store_true", help="Generar combinaciones keywords × ubicaciones")
    parser.add_argument("--keywords", default="", help="Filtro de keywords (separados por coma)")
    parser.add_argument("--locations", default="", help="Filtro de ubicaciones (separadas por coma)")
    parser.add_argument("--keywords-file", default="", help="Archivo de keywords alternativo")
    parser.add_argument("--grid-mode", action="store_true", help="Modo grid: usa grid-bbox sin ubicaciones")
    parser.add_argument("--keywordless-mode", action="store_true", help="Modo keywordless: genera queries genéricas por ubicación")
    parser.add_argument("--grid-bbox", default="", help="BBOX para grid mode (formato: south_lat,west_lon,north_lat,east_lon)")
    parser.add_argument("--grid-cell", type=float, default=0.0, help="Tamaño de celda en km (default: 1.0)")
    parser.add_argument("--scrape", action="store_true", help="Scrapear Google Maps vía Gosom")
    parser.add_argument("--import", dest="do_import", action="store_true", help="Importar CSVs a contacts.db")
    parser.add_argument("--sanitize", action="store_true", help="Normalizar y scorear leads")
    parser.add_argument("--prospect", action="store_true", help="Ejecutar prospección multicanal")
    parser.add_argument("--channel", default="all", choices=["all", "forms", "smtp", "whatsapp"], help="Canal de prospección")
    parser.add_argument("--limit", type=int, default=100, help="Límite de leads por canal")
    parser.add_argument("--offer", default="hosting", choices=["hosting", "web", "seo"], help="Tipo de oferta")
    parser.add_argument("--status", action="store_true", help="Ver estado del pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Simular sin escribir")

    args = parser.parse_args()

    # If only --status
    if args.status and not any([args.all, args.combine, args.scrape, args.do_import,
                                 args.sanitize, args.prospect]):
        phase_status()
        return

    results = run_pipeline(
        do_all=args.all,
        do_combine=args.combine,
        keywords_filter=args.keywords,
        locations_filter=args.locations,
        keywords_file=args.keywords_file,
        grid_mode=args.grid_mode,
        keywordless_mode=args.keywordless_mode,
        grid_bbox=args.grid_bbox,
        grid_cell=args.grid_cell,
        do_scrape=args.scrape,
        do_import=args.do_import,
        do_sanitize=args.sanitize,
        do_prospect=args.prospect,
        prospect_channel=args.channel,
        prospect_limit=args.limit,
        prospect_offer=args.offer,
        do_status=args.status,
        dry_run=args.dry_run,
    )

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
