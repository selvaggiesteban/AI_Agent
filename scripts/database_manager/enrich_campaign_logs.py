"""
Enriquece contacts.db con datos de logs de campañas (log_*.txt).

Campos actualizados:
- last_sender_account: último sender que contactó al email
- last_interaction_date: fecha del último EXITO
- campaigns: lista de campañas (append)
- smtp_processed: '1' si tiene al menos un EXITO
"""

import sqlite3
import os
import re
from datetime import datetime
from collections import defaultdict

DB_PATH = os.path.join("data", "inputs", "contacts.db")
LOGS_DIR = os.path.join("logs", "campaigns")

JUNK_PATTERNS = [
    "sentry", "wixpress", "example", "test", "demo",
    "@2x.png", ".js", "username@domain", "your@mail",
    "juan.perez", "beispiel", "ejemplo", "mysite",
]

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def is_valid_email(email):
    if not email or not EMAIL_RE.match(email):
        return False
    email_lower = email.lower()
    return not any(p in email_lower for p in JUNK_PATTERNS)


def parse_logs(logs_dir):
    """Parsea todos los log_*.txt y retorna datos agrupados por email."""
    # {email: {sender, timestamp, campaign, exito}}
    email_data = defaultdict(lambda: {"sender": None, "timestamp": None, "campaigns": set(), "has_exito": False})
    files_parsed = 0
    total_exito = 0
    total_fallo = 0

    log_files = sorted(f for f in os.listdir(logs_dir) if f.startswith("log_") and f.endswith(".txt"))

    for fname in log_files:
        path = os.path.join(logs_dir, fname)
        current_campaign = None
        file_exito = 0
        file_fallo = 0

        for line in open(path, encoding="utf-8", errors="ignore"):
            # Detectar campaña (maneja encoding Ñ)
            if "INICIADA" in line:
                m = re.search(r"===\s+(.+?)\s+INICIADA", line)
                if m:
                    current_campaign = m.group(1).strip()
                    continue

            # Detectar EXITO
            m = re.search(
                r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+).*\[(\S+@\S+)\]\s+\[EXITO\]\s+(\S+)",
                line,
            )
            if m:
                ts, sender, email_raw = m.groups()
                email = email_raw.strip().lower()
                if not is_valid_email(email_raw):
                    file_fallo += 1
                    continue
                entry = email_data[email]
                entry["sender"] = sender
                entry["timestamp"] = ts
                entry["has_exito"] = True
                if current_campaign:
                    entry["campaigns"].add(current_campaign)
                file_exito += 1
                continue

            # Detectar FALLO
            m = re.search(
                r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+).*\[(\S+@\S+)\]\s+\[FALLO\]\s+(\S+)",
                line,
            )
            if m:
                ts, sender, email_raw = m.groups()
                email = email_raw.strip().rstrip(".").lower()
                if not is_valid_email(email_raw):
                    file_fallo += 1
                    continue
                entry = email_data[email]
                if not entry["timestamp"] or ts > entry["timestamp"]:
                    entry["sender"] = sender
                    entry["timestamp"] = ts
                if current_campaign:
                    entry["campaigns"].add(current_campaign)
                file_fallo += 1

        total_exito += file_exito
        total_fallo += file_fallo
        files_parsed += 1

    print(f"[INFO] Parseados {files_parsed} archivos de log")
    print(f"[INFO] Total EXITO parseados: {total_exito}")
    print(f"[INFO] Total FALLO parseados: {total_fallo}")
    print(f"[INFO] Emails únicos con actividad: {len(email_data)}")
    return email_data


def enrich(db_path, email_data):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Obtener emails existentes
    cur.execute("SELECT ROWID, primary_email, campaigns FROM main")
    db_rows = {}
    for row in cur.fetchall():
        if row[1]:
            db_rows[row[1].lower().strip()] = {
                "rowid": row[0],
                "campaigns": row[2] or "",
            }

    updated = 0
    inserted = 0
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for email, data in email_data.items():
        if email in db_rows:
            # UPDATE contacto existente
            row = db_rows[email]
            rowid = row["rowid"]

            existing_campaigns = row["campaigns"]
            new_campaigns = ",".join(sorted(data["campaigns"]))
            if existing_campaigns and new_campaigns:
                existing_set = set(c.strip() for c in existing_campaigns.split(",") if c.strip())
                truly_new = set(data["campaigns"]) - existing_set
                if truly_new:
                    campaigns_final = existing_campaigns + "," + ",".join(sorted(truly_new))
                else:
                    campaigns_final = existing_campaigns
            elif new_campaigns:
                campaigns_final = new_campaigns
            else:
                campaigns_final = existing_campaigns

            cur.execute(
                """UPDATE main SET
                    last_sender_account = ?,
                    last_interaction_date = ?,
                    campaigns = ?,
                    smtp_processed = '1',
                    date_updated = ?
                WHERE ROWID = ?""",
                (data["sender"], data["timestamp"], campaigns_final, now, rowid),
            )
            updated += 1
        else:
            # INSERT contacto nuevo
            campaigns_str = ",".join(sorted(data["campaigns"])) if data["campaigns"] else None
            cur.execute(
                """INSERT INTO main (primary_email, last_sender_account, last_interaction_date, campaigns, smtp_processed, date_added, date_updated)
                   VALUES (?, ?, ?, ?, '1', ?, ?)""",
                (email, data["sender"], data["timestamp"], campaigns_str, now, now),
            )
            inserted += 1

    conn.commit()

    # Verificación
    cur.execute("SELECT COUNT(*) FROM main")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM main WHERE last_sender_account IS NOT NULL AND last_sender_account != ''")
    with_sender = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM main WHERE last_interaction_date IS NOT NULL AND last_interaction_date != ''")
    with_date = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM main WHERE campaigns IS NOT NULL AND campaigns != ''")
    with_campaigns = cur.fetchone()[0]

    print(f"\n--- VERIFICACION ---")
    print(f"Total contactos: {total}")
    print(f"Con last_sender_account: {with_sender}")
    print(f"Con last_interaction_date: {with_date}")
    print(f"Con campaigns: {with_campaigns}")
    print(f"\n--- RESULTADO ---")
    print(f"Actualizados: {updated}")
    print(f"Nuevos insertados: {inserted}")

    conn.close()
    return updated, inserted


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "..", DB_PATH)
    logs_dir = os.path.join(script_dir, "..", "..", LOGS_DIR)

    print("=== Enriquecimiento Campaign Logs ===\n")
    email_data = parse_logs(logs_dir)
    updated, inserted = enrich(db_path, email_data)
    print(f"\n=== COMPLETADO: {updated} actualizados, {inserted} nuevos insertados ===")
