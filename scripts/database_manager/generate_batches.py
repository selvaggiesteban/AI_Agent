"""
generate_batches.py — Genera 108 lotes (18 cuentas × 6 batches × 50 emails)
Lee emails nuevos de la DB y crea archivos .txt con emails separados por comas.

Uso:
  python generate_batches.py
  python generate_batches.py --dry-run
"""

import os
import sqlite3
import random
import argparse
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "inputs", "contacts.db")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "outputs", "campaign_batches")

# 18 cuentas remitentes (corregido: selvaggiesteban2 reemplaza duplicado)
SENDER_ACCOUNTS = [
    "selvaggi.esteban@gmail.com",
    "wwwlanuscomputacion@gmail.com",
    "adrianaavila131969@gmail.com",
    "fernando1141967@gmail.com",
    "hola@selvaggiesteban.dev",
    "esteban@lanuscomputacion.com",
    "selvaggiesteban9@gmail.com",
    "selvaggiesteban4@gmail.com",
    "selvaggiesteban2@gmail.com",
    "selvaggiesteban11@gmail.com",
    "marketing1a1oficial@gmail.com",
    "selvaggiconsultores@gmail.com",
    "estebanmfwd@gmail.com",
    "selvaggiesteban1@gmail.com",
    "selvaggiesteban2@gmail.com",
    "esteselvaggi@hotmail.com",
    "selvaggi.esteban@icloud.com",
    "selvaggiesteban11@icloud.com",
]

BATCHES_PER_ACCOUNT = 6
EMAILS_PER_BATCH = 50
TOTAL_EMAILS_NEEDED = len(SENDER_ACCOUNTS) * BATCHES_PER_ACCOUNT * EMAILS_PER_BATCH


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--random", action="store_true", help="Mezclar emails aleatoriamente")
    args = parser.parse_args()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Get all new emails (from LOMAS/LANUS imports)
    c.execute("""
        SELECT DISTINCT l.primary_email
        FROM lead l
        JOIN contact c ON l.ROWID = c.ROWID
        WHERE c.date_added LIKE '2026-07-27%'
        AND l.primary_email IS NOT NULL
        AND length(l.primary_email) > 0
        ORDER BY l.ROWID
    """)
    emails = [r[0] for r in c.fetchall()]
    conn.close()

    print(f"Emails disponibles: {len(emails)}")
    print(f"Emails necesarios: {TOTAL_EMAILS_NEEDED} ({len(SENDER_ACCOUNTS)} × {BATCHES_PER_ACCOUNT} × {EMAILS_PER_BATCH})")

    if len(emails) < TOTAL_EMAILS_NEEDED:
        print(f"ERROR: Faltan {TOTAL_EMAILS_NEEDED - len(emails)} emails")
        return

    if args.random:
        random.shuffle(emails)
        emails = emails[:TOTAL_EMAILS_NEEDED]
    else:
        emails = emails[:TOTAL_EMAILS_NEEDED]

    if args.dry_run:
        print("\n[DRY RUN] No se crearon archivos")
        print(f"Primeros 5 emails: {emails[:5]}")
        print(f"Últimos 5 emails: {emails[-5:]}")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    file_count = 0
    email_index = 0

    for account_idx, account in enumerate(SENDER_ACCOUNTS):
        for batch_num in range(1, BATCHES_PER_ACCOUNT + 1):
            batch_emails = emails[email_index:email_index + EMAILS_PER_BATCH]
            email_index += EMAILS_PER_BATCH

            # Filename: lote_01_sender.csv
            account_num = account_idx + 1
            batch_num_str = str(batch_num).zfill(2)
            account_clean = account.split("@")[0].replace(".", "_")
            filename = f"lote_{str(account_num).zfill(2)}_{account_clean}_batch{batch_num_str}.csv"

            filepath = os.path.join(OUTPUT_DIR, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(",".join(batch_emails))

            file_count += 1
            print(f"  {filename} ({len(batch_emails)} emails)")

    print(f"\nTotal archivos creados: {file_count}")
    print(f"Directorio: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
