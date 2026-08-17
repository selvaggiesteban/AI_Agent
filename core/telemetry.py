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
Telemetry — Reporting transversal para pipelines Lead y Services.

Consolida datos de:
  - logs/pipeline/lead_execution_log.json
  - logs/pipeline/services_execution_log.json
  - logs/pipeline/telemetry.json (consolidado)

Uso:
  python -m core.telemetry [--reporte] [--consolidar] [--status]
"""

import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

ROOT_DIR = Path(__file__).resolve().parent.parent

from core.config import DB_PATH, DATA_OUTPUTS_DIR

LOG_DIR = ROOT_DIR / "logs" / "pipeline"
LOG_DIR.mkdir(parents=True, exist_ok=True)

LEAD_LOG = LOG_DIR / "lead_execution_log.json"
SERVICES_LOG = LOG_DIR / "services_execution_log.json"
CONSOLIDATED_LOG = LOG_DIR / "telemetry.json"
ACCOUNTING_LOG = LOG_DIR / "accounting.json"

logger = logging.getLogger("telemetry")
logger.setLevel(logging.INFO)
_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s", "%H:%M:%S"))
logger.addHandler(_handler)


def _load_json(path: Path) -> List[Dict]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []
    return []


def _save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Consolidar telemetría de ambos pipelines
# ---------------------------------------------------------------------------

def consolidar() -> Dict:
    logger.info("Consolidando telemetría de Lead + Services...")

    lead_events = _load_json(LEAD_LOG)
    services_events = _load_json(SERVICES_LOG)

    all_events = lead_events + services_events
    all_events.sort(key=lambda e: e.get("ts", ""))

    consolidated = {
        "generated_at": datetime.now().isoformat(),
        "lead_events": len(lead_events),
        "services_events": len(services_events),
        "total_events": len(all_events),
        "events": all_events,
    }

    _save_json(CONSOLIDATED_LOG, consolidated)
    logger.info("  Lead events: %d | Services events: %d | Total: %d",
                len(lead_events), len(services_events), len(all_events))
    return consolidated


# ---------------------------------------------------------------------------
# Generar reporte de contabilidad por cliente
# ---------------------------------------------------------------------------

def reporte_contabilidad() -> Dict:
    logger.info("Generando reporte de contabilidad...")

    if not DB_PATH.exists():
        logger.error("DB no encontrada")
        return {"error": "db_missing"}

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Clientes con entregas
    cursor.execute("""
        SELECT title, primary_email, sector, address, deliverability,
               date_added
        FROM main
        WHERE deliverability IN ('caliente', 'tibio')
        ORDER BY deliverability, title
    """)
    active_clients = [dict(row) for row in cursor.fetchall()]

    # Clientes por score
    cursor.execute("""
        SELECT deliverability, COUNT(*) as cnt
        FROM main
        WHERE deliverability IS NOT NULL
        GROUP BY deliverability
    """)
    by_score = {row["deliverability"]: row["cnt"] for row in cursor.fetchall()}

    # Total leads
    cursor.execute("SELECT COUNT(*) FROM main")
    total = cursor.fetchone()[0]

    conn.close()

    accounting = {
        "generated_at": datetime.now().isoformat(),
        "total_leads": total,
        "by_score": by_score,
        "active_clients": len(active_clients),
        "clients": active_clients[:50],  # Top 50
    }

    _save_json(ACCOUNTING_LOG, accounting)
    logger.info("  Total leads: %d | Activos: %d", total, len(active_clients))
    return accounting


# ---------------------------------------------------------------------------
# Resumen rápido de estado
# ---------------------------------------------------------------------------

def status() -> Dict:
    lead_events = _load_json(LEAD_LOG)
    services_events = _load_json(SERVICES_LOG)

    lead_runs = [e for e in lead_events if e.get("event") == "pipeline_complete"]
    services_runs = [e for e in services_events if e.get("event") == "pipeline_complete"]

    # Último run de cada pipeline
    last_lead = lead_runs[-1] if lead_runs else None
    last_services = services_runs[-1] if services_runs else None

    result = {
        "lead": {
            "total_runs": len(lead_runs),
            "last_run": last_lead.get("ts") if last_lead else None,
            "last_elapsed": last_lead.get("elapsed_s") if last_lead else None,
        },
        "services": {
            "total_runs": len(services_runs),
            "last_run": last_services.get("ts") if last_services else None,
            "last_elapsed": last_services.get("elapsed_s") if last_services else None,
        },
        "consolidated_exists": CONSOLIDATED_LOG.exists(),
    }

    logger.info("Lead: %d runs | Services: %d runs", len(lead_runs), len(services_runs))
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Telemetry — Reporting transversal")
    parser.add_argument("--consolidar", action="store_true", help="Consolidar telemetría de ambos pipelines")
    parser.add_argument("--reporte", action="store_true", help="Generar reporte de contabilidad")
    parser.add_argument("--status", action="store_true", help="Ver estado de telemetría")

    args = parser.parse_args()

    if not any([args.consolidar, args.reporte, args.status]):
        args.status = True

    if args.consolidar:
        consolidar()
    if args.reporte:
        reporte_contabilidad()
    if args.status:
        status()


if __name__ == "__main__":
    main()
