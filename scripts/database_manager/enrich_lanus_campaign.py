"""
Enriquece contacts.db con los 228 envíos de la campaña LANÚS-03082026.

Parsea los logs de exito, inserta en tabla campaign, y registra el message body.
"""

import sqlite3
import os
import re
from datetime import datetime

DB_PATH = os.path.join("data", "inputs", "contacts.db")
LOGS_DIR = os.path.join("logs", "campaigns")

LIST_NAME = "LANÚS-03082026"
SUBJECT = "Servicio Técnico de Computadoras y Productos de Tecnología"
TYPE = "lanus_servicio_tecnico"
MESSAGE_BODY = (
    "Hola, buenos días. ¿Cómo estás? Espero que muy bien. "
    "Me comunico facilitando servicio técnico de computadoras y productos de tecnología. "
    "Brindamos soluciones tanto para particulares como para comercios y empresas de la zona. "
    "Si necesitás reparación, mantenimiento o equipamiento, podés contactarnos. "
    "Quedo a disposición para lo que necesites. Saludos cordiales"
)

LOG_FILES = [
    "log_lanus_cycle_20260803_112153.txt",
    "log_lanus_cycle_20260803_112606.txt",
]


def parse_ok_emails(logs_dir):
    """Parsea logs y retorna lista de dicts con email, sender, timestamp."""
    results = []
    for fname in LOG_FILES:
        path = os.path.join(logs_dir, fname)
        if not os.path.exists(path):
            print(f"[WARN] Log no encontrado: {path}")
            continue
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
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

    # Build email -> rowid mapping from lead table
    cur.execute("SELECT ROWID, primary_email FROM lead WHERE primary_email IS NOT NULL AND primary_email != ''")
    email_to_rowid = {}
    for rowid, email in cur.fetchall():
        if email:
            email_to_rowid[email.lower().strip()] = rowid

    inserted = 0
    skipped = 0
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for entry in entries:
        email_lower = entry["email"].lower().strip()
        if email_lower not in email_to_rowid:
            skipped += 1
            continue

        rowid = email_to_rowid[email_lower]

        # Check if already exists in campaign for this list
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

    # Verification
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

    print("=== Enriquecimiento Campaign LANÚS-03082026 ===\n")
    entries = parse_ok_emails(logs_dir)
    print(f"[INFO] Emails OK parseados de logs: {len(entries)}")

    inserted, skipped = enrich(db_path, entries)
    print(f"\n=== COMPLETADO: {inserted} insertados, {skipped} skipped ===")
