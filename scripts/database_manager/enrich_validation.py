"""
Enriquece contacts.db con datos de validación de emails (validation_results_*.csv).

Campos actualizados:
- deliverability: 'valid' si dominio tiene registros, 'invalid' si no
- last_validation_status: 'validated' o 'invalid_syntax'
- validation_date: fecha de la validación
"""

import sqlite3
import csv
import os
from datetime import datetime

DB_PATH = os.path.join("data", "inputs", "contacts.db")
LOGS_DIR = os.path.join("logs", "campaigns")


def enrich(db_path, logs_dir):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Obtener emails existentes
    cur.execute("SELECT ROWID, primary_email FROM main")
    db_rows = {}
    for row in cur.fetchall():
        if row[1]:
            db_rows[row[1].lower().strip()] = row[0]

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated = 0
    inserted = 0
    not_found = 0

    # Procesar todos los CSVs de validación
    csv_files = sorted(f for f in os.listdir(logs_dir) if f.startswith("validation") and f.endswith(".csv"))

    for fname in csv_files:
        path = os.path.join(logs_dir, fname)
        with open(path, encoding="utf-8", errors="ignore") as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = row.get("e-mail", "").strip().lower()
                if not email:
                    continue

                syntax_ok = row.get("sintaxis dominio", "").strip() == "True"
                records_ok = row.get("registros dominio", "").strip() == "True"

                if records_ok:
                    deliverability = "valid"
                    validation_status = "validated"
                elif syntax_ok:
                    deliverability = "uncertain"
                    validation_status = "valid_syntax_no_records"
                else:
                    deliverability = "invalid"
                    validation_status = "invalid_syntax"

                if email in db_rows:
                    cur.execute(
                        """UPDATE main SET
                            deliverability = ?,
                            last_validation_status = ?,
                            last_validation_date = ?,
                            date_updated = ?
                        WHERE ROWID = ?""",
                        (deliverability, validation_status, now, now, db_rows[email]),
                    )
                    updated += 1
                else:
                    cur.execute(
                        """INSERT INTO main (primary_email, deliverability, last_validation_status, last_validation_date, date_added, date_updated)
                           VALUES (?, ?, ?, ?, ?, ?)""",
                        (email, deliverability, validation_status, now, now, now),
                    )
                    inserted += 1

    conn.commit()

    # Verificación
    cur.execute("SELECT COUNT(*) FROM main")
    total = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM main WHERE deliverability IS NOT NULL AND deliverability != ''")
    with_deliv = cur.fetchone()[0]
    cur.execute("SELECT deliverability, COUNT(*) FROM main WHERE deliverability IS NOT NULL AND deliverability != '' GROUP BY deliverability")
    deliv_dist = cur.fetchall()

    print(f"\n--- VERIFICACION ---")
    print(f"Total contactos: {total}")
    print(f"Con deliverability: {with_deliv}")
    print(f"Distribucion:")
    for d, c in deliv_dist:
        print(f"  {d}: {c}")
    print(f"\n--- RESULTADO ---")
    print(f"Actualizados: {updated}")
    print(f"Nuevos insertados: {inserted}")

    conn.close()
    return updated, inserted


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "..", DB_PATH)
    logs_dir = os.path.join(script_dir, "..", "..", LOGS_DIR)

    print("=== Enriquecimiento Validacion CSV ===\n")
    updated, inserted = enrich(db_path, logs_dir)
    print(f"\n=== COMPLETADO: {updated} actualizados, {inserted} nuevos ===")
