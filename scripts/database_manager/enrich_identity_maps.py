"""
Enriquece contacts.db con datos de Identity Maps (logs/campaigns/identity_map_*.json).

Acciones:
1. Actualiza `assigned_sender` en contactos existentes (~16.332)
2. Inserta contactos nuevos válidos (~130-140) que no están en la DB
"""

import sqlite3
import json
import os
import re
from datetime import datetime

DB_PATH = os.path.join("data", "inputs", "contacts.db")
LOGS_DIR = os.path.join("logs", "campaigns")

# Patrones de basura a excluir
JUNK_PATTERNS = [
    "sentry", "wixpress", "example", "test", "demo",
    "@2x.png", ".js", "username@domain", "your@mail",
    "juan.perez", "beispiel", "ejemplo", "mysite",
]

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def load_identity_maps(logs_dir):
    """Carga todos los identity_map_*.json y mergea en un solo dict."""
    merged = {}
    files_loaded = []
    for f in sorted(os.listdir(logs_dir)):
        if f.startswith("identity_map") and f.endswith(".json"):
            path = os.path.join(logs_dir, f)
            data = json.load(open(path, encoding="utf-8"))
            # Prioridad: archivos más recientes sobreescriben
            merged.update(data)
            files_loaded.append(f)
    print(f"[INFO] Cargados {len(files_loaded)} identity maps")
    print(f"[INFO] Total emails únicos: {len(merged)}")
    return merged


def is_valid_email(email):
    """Valida que el email sea real y no basura."""
    if not email or not EMAIL_RE.match(email):
        return False
    email_lower = email.lower()
    return not any(p in email_lower for p in JUNK_PATTERNS)


def enrich(db_path, identity_map):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Obtener emails existentes en DB
    cur.execute("SELECT ROWID, primary_email FROM main")
    db_rows = {}
    for row in cur.fetchall():
        if row[1]:
            db_rows[row[1].lower().strip()] = row[0]

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # --- PASO 1: UPDATE assigned_sender para contactos existentes ---
    updated = 0
    skipped_invalid = 0
    for raw_email, sender in identity_map.items():
        email = raw_email.lower().strip()
        if not is_valid_email(raw_email):
            skipped_invalid += 1
            continue
        if email in db_rows:
            cur.execute(
                "UPDATE main SET assigned_sender = ?, date_updated = ? WHERE ROWID = ?",
                (sender, now, db_rows[email]),
            )
            updated += 1

    print(f"[STEP 1] UPDATE assigned_sender: {updated} filas actualizadas")
    print(f"[STEP 1] Emails inválidos/basura omitidos: {skipped_invalid}")

    # --- PASO 2: INSERT contactos nuevos válidos ---
    inserted = 0
    skipped_existing = 0
    skipped_junk = 0
    for raw_email, sender in identity_map.items():
        email = raw_email.lower().strip()
        if not is_valid_email(raw_email):
            skipped_junk += 1
            continue
        if email in db_rows:
            skipped_existing += 1
            continue
        # Insertar nuevo contacto
        cur.execute(
            """INSERT INTO main (primary_email, assigned_sender, date_added, date_updated, smtp_processed, form_processed)
               VALUES (?, ?, ?, ?, '0', '0')""",
            (raw_email.strip(), sender, now, now),
        )
        inserted += 1

    print(f"[STEP 2] INSERT nuevos: {inserted} contactos nuevos insertados")
    print(f"[STEP 2] Ya existían en DB: {skipped_existing}")
    print(f"[STEP 2] Basura filtrada: {skipped_junk}")

    conn.commit()

    # Verificación final
    cur.execute("SELECT COUNT(*) FROM main")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM main WHERE assigned_sender IS NOT NULL AND assigned_sender != ''")
    with_sender = cur.fetchone()[0]
    print(f"\n--- VERIFICACIÓN ---")
    print(f"Total contactos en DB: {total}")
    print(f"Con assigned_sender: {with_sender}")

    conn.close()
    return updated, inserted


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "..", DB_PATH)
    logs_dir = os.path.join(script_dir, "..", "..", LOGS_DIR)

    print("=== Enriquecimiento Identity Maps ===\n")
    identity_map = load_identity_maps(logs_dir)
    updated, inserted = enrich(db_path, identity_map)
    print(f"\n=== COMPLETADO: {updated} actualizados, {inserted} nuevos ===")
