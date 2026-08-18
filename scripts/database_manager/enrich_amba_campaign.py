"""
enrich_amba_campaign.py — Enriquece contacts.db con datos de campana AMBA 04/08/2026.
Parsea logs de exito, inserta en tabla campaign.
"""

import sqlite3
import os
import re
import glob
from datetime import datetime

DB_PATH = os.path.join("data", "inputs", "contacts.db")
LOGS_DIR = os.path.join("logs", "campaigns")

LIST_NAME = "AMBA-04082026"
SUBJECT = "Servicio Tecnico de Computadoras y Productos de Tecnologia"
TYPE = "amba_servicio_tecnico"
MESSAGE_BODY = (
    "Hola, buenos dias. "
    "Como estas? Espero que muy bien. "
    "Me comunico facilitando servicio tecnico de computadoras y productos de tecnologia. "
    "Brindamos soluciones tanto para particulares como para comercios y empresas de la zona. "
    "Si necesitás reparacion, mantenimiento o equipamiento, podes contactarnos. "
    "Quedo a disposicion para lo que necesites.\n\n"
    "Saludos cordiales"
)


def parse_ok_emails(logs_dir):
    """Parsea logs AMBA y retorna lista de dicts con email, sender, timestamp."""
    results = []
    pattern = os.path.join(logs_dir, "log_amba_*.txt")
    for filepath in sorted(glob.glob(pattern)):
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


def enrich(db_path, entries):
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
            (rowid, LIST_NAME),
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
                SUBJECT,
                LIST_NAME,
                SUBJECT,
                entry["sender"],
                entry["timestamp"],
                TYPE,
                MESSAGE_BODY,
                entry["email"],
            ),
        )
        inserted += 1

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM campaign WHERE list_val = ?", (LIST_NAME,))
    total_in_campaign = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM campaign")
    total_all = cur.fetchone()[0]

    print(f"\n--- VERIFICACION ---")
    print(f"Total campaign rows: {total_all}")
    print(f"Rows with list_val='{LIST_NAME}': {total_in_campaign}")
    print(f"\n--- RESULTADO ---")
    print(f"Insertados: {inserted}")
    print(f"Skipped (no encontrado o duplicado): {skipped}")

    conn.close()
    return inserted, skipped


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "..", DB_PATH)
    logs_dir = os.path.join(script_dir, "..", "..", LOGS_DIR)

    print("=== Enriquecimiento Campaign AMBA-04082026 ===\n")
    entries = parse_ok_emails(logs_dir)
    print(f"[INFO] Emails OK parseados de logs: {len(entries)}")

    inserted, skipped = enrich(db_path, entries)
    print(f"\n=== COMPLETADO: {inserted} insertados, {skipped} skipped ===")
