"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
enrich_campaign.py — Consolidado para múltiples campañas.
Enriquece contacts.db parseando logs de éxito.
"""

import sqlite3
import os
import re
import glob
import argparse
from datetime import datetime

# === CONFIGURACIONES DE CAMPAÑA ===
CAMPAIGNS = {
    "amba": {
        "list_name": "AMBA-04082026",
        "type": "amba_servicio_tecnico",
        "log_pattern": "log_amba_*.txt",
    },
    "ba_caba": {
        "list_name": "BA-CABA-03082026",
        "type": "ba_caba_servicio_tecnico",
        "log_pattern": "log_ba_ciclo_*.txt",
    }
}

COMMON_SUBJECT = "Servicio Tecnico de Computadoras y Productos de Tecnologia"
COMMON_MESSAGE_BODY = (
    "Hola, buenos dias. "
    "Como estas? Espero que muy bien. "
    "Me comunico facilitando servicio tecnico de computadoras y productos de tecnologia. "
    "Brindamos soluciones tanto para particulares como para comercios y empresas de la zona. "
    "Si necesitás reparacion, mantenimiento o equipamiento, podes contactarnos. "
    "Quedo a disposicion para lo que necesites.\n\n"
    "Saludos cordiales"
)

DB_PATH = os.path.join("data", "inputs", "contacts.db")
LOGS_DIR = os.path.join("logs", "campaigns")

def parse_ok_emails(logs_dir, pattern):
    """Parsea logs y retorna lista de dicts con email, sender, timestamp."""
    results = []
    full_pattern = os.path.join(logs_dir, pattern)
    for filepath in sorted(glob.glob(full_pattern)):
        fname = os.path.basename(filepath)
        print(f"[INFO] Parseando: {fname}")
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if "[OK]" not in line:
                    continue
                m = re.search(
                    r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*\[(\S+@\S+)\]\s+\[OK\]\s+(\S+)",
                    line,
                )
                if m:
                    timestamp, sender, email = m.groups()
                    email = email.strip().rstrip(".")
                    results.append({
                        "email": email,
                        "sender": sender,
                        "timestamp": timestamp,
                    })
    return results

def enrich(db_path, entries, campaign_cfg):
    list_name = campaign_cfg["list_name"]
    camp_type = campaign_cfg["type"]
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT ROWID, primary_email FROM lead WHERE primary_email IS NOT NULL AND primary_email != ''")
    email_to_rowid = {}
    for rowid, email in cur.fetchall():
        if email:
            email_to_rowid[email.lower().strip()] = rowid

    inserted = 0
    skipped = 0

    for entry in entries:
        email_lower = entry["email"].lower().strip()
        if email_lower not in email_to_rowid:
            skipped += 1
            continue

        rowid = email_to_rowid[email_lower]

        cur.execute(
            "SELECT COUNT(*) FROM campaign WHERE contact_rowid = ? AND list_val = ?",
            (rowid, list_name),
        )
        if cur.fetchone()[0] > 0:
            skipped += 1
            continue

        cur.execute(
            """INSERT INTO campaign
               (contact_rowid, title, list_val, subject, sender, date, type, message, email_used)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                rowid,
                COMMON_SUBJECT,
                list_name,
                COMMON_SUBJECT,
                entry["sender"],
                entry["timestamp"],
                camp_type,
                COMMON_MESSAGE_BODY,
                entry["email"],
            ),
        )
        inserted += 1

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM campaign WHERE list_val = ?", (list_name,))
    total_in_campaign = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM campaign")
    total_all = cur.fetchone()[0]

    print(f"\n--- VERIFICACION ---")
    print(f"Total campaign rows: {total_all}")
    print(f"Rows with list_val='{list_name}': {total_in_campaign}")
    print(f"\n--- RESULTADO ---")
    print(f"Insertados: {inserted}")
    print(f"Skipped (no encontrado o duplicado): {skipped}")

    conn.close()
    return inserted, skipped

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enriquecimiento de Campañas Consolidado")
    parser.add_argument("--campaign", choices=CAMPAIGNS.keys(), required=True, help="Tipo de campaña: amba o ba_caba")
    args = parser.parse_args()

    cfg = CAMPAIGNS[args.campaign]
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Path adjustment to reach the root from scripts/database/
    db_path = os.path.abspath(os.path.join(script_dir, "..", "..", DB_PATH))
    logs_dir = os.path.abspath(os.path.join(script_dir, "..", "..", LOGS_DIR))

    print(f"=== Enriquecimiento Campaign {args.campaign.upper()} - {cfg['list_name']} ===\n")
    entries = parse_ok_emails(logs_dir, cfg["log_pattern"])
    print(f"[INFO] Emails OK parseados de logs: {len(entries)}")

    inserted, skipped = enrich(db_path, entries, cfg)
    print(f"\n=== COMPLETADO: {inserted} insertados, {skipped} skipped ===")
