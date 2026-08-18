"""
Importador de datos Gosom General -> contacts.db
Lee chunk_001.csv de data/inputs/gosom/output/general/
Maximiza cobertura: inserta TODOS los emails nuevos de todas las filas
Deduplica por email (skip automático)
Valida emails (regex + blacklist)
Corrige mojibake en textos
"""

import os
import sys
import csv
import json
import re
import sqlite3
from datetime import datetime

# === CONFIG ===
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.path.join(PROJECT_ROOT, "data", "inputs", "gosom", "output", "general", "chunk_001.csv")
DB_PATH = os.path.join(PROJECT_ROOT, "data", "inputs", "contacts.db")
LOG_PATH = os.path.join(PROJECT_ROOT, "data", "inputs", "gosom_general_import.log")

# === REGLAS DE VALIDACION DE EMAILS ===
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

JUNK_PATTERNS = [
    "sentry", "wixpress", "example", "test", "demo",
    "@2x.png", "@2x.webp", ".js", "username@domain", "your@mail",
    "juan.perez", "beispiel", "ejemplo", "mysite",
]

AUTO_REPLY_PATTERNS = [
    "noreply", "no-reply", "mailer-daemon", "postmaster", "abuse",
    "auto-reply", "donotreply", "auto_submit",
]

PLACEHOLDER_EMAILS = {
    "tunombre@email.com", "usuario@dominio.com", "nombre@ejemplo.com",
    "john@doe.com", "info@yourdomain.com", "info@website.com",
    "hola@miempresa.es", "email@example.com", "ejemplo@mail.com",
    "email@ejemplo.com", "nombre@mail.com", "theratio_interior@mail.com",
}

# === REGLAS DE ENCODING (MOJIBAKE) ===
MOJIBAKE_MAP = {
    "\u00c3\u00b1": "\u00f1",  # Ã± -> ñ
    "\u00c3\u00a9": "\u00e9",  # Ã© -> é
    "\u00c3\u00a1": "\u00e1",  # Ã¡ -> á
    "\u00c3\u00b3": "\u00f3",  # Ã³ -> ó
    "\u00c3\u00ad": "\u00ed",  # Ã­ -> í
    "\u00c3\u00bc": "\u00fc",  # Ã¼ -> ü
    "\u00c3\u00a0": "\u00e0",  # Ã  -> à
    "\u00c3\u00a8": "\u00e8",  # Ã¨ -> è
    "\u00c3\u00b2": "\u00f2",  # Ã´ -> ò
    "\u00c3\u00a2": "\u00e2",  # Ã¢ -> â
    "\u00c3\u00a4": "\u00e4",  # Ã¤ -> ä
    "\u00c3\u00b6": "\u00f6",  # Ã¶ -> ö
    "\u00c3\u00a7": "\u00e7",  # Ã§ -> ç
    "\u00c3\u00ae": "\u00ee",  # Ã® -> î
    "\u00c2\u00b0": "\u00b0",  # Â° -> °
    "\u00c2\u00ba": "\u00ba",  # Âº -> º
    "\u00c2\u00b7": "",        # Â· -> (remove)
}

MOJIBAKE_DETECT_CHARS = ["\u00c3", "\u00c2"]


def is_valid_email(email):
    if not email or not email.strip():
        return False
    email = email.strip().lower()
    if not EMAIL_REGEX.match(email):
        return False
    for p in JUNK_PATTERNS:
        if p in email:
            return False
    for p in AUTO_REPLY_PATTERNS:
        if p in email:
            return False
    if email in PLACEHOLDER_EMAILS:
        return False
    return True


def fix_mojibake(text):
    if not text:
        return text
    if not any(c in text for c in MOJIBAKE_DETECT_CHARS):
        return text
    for bad, good in MOJIBAKE_MAP.items():
        text = text.replace(bad, good)
    return text


def fix_website(url):
    if not url or not url.strip():
        return None
    url = url.strip()
    if url and not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    return url


def parse_complete_address(raw):
    if not raw or not raw.strip():
        return None, None, None
    try:
        data = json.loads(raw)
        return (
            data.get("city", ""),
            data.get("state", ""),
            data.get("country", ""),
        )
    except (json.JSONDecodeError, TypeError):
        return None, None, None


def log_msg(f, msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    if f:
        f.write(line + "\n")
        f.flush()


def main():
    log = open(LOG_PATH, "w", encoding="utf-8")

    # Backup
    backup_path = DB_PATH.replace(".db", "_pre_gosom_general.db")
    if not os.path.exists(backup_path):
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        log_msg(log, f"Backup created: {backup_path}")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Load existing emails
    c.execute("SELECT primary_email FROM lead WHERE primary_email IS NOT NULL AND primary_email != ''")
    existing_emails = {row[0].lower().strip() for row in c.fetchall()}
    log_msg(log, f"Existing emails in DB: {len(existing_emails)}")

    # Load existing (title, city) pairs for dedup
    c.execute("""
        SELECT LOWER(TRIM(m.title)), LOWER(TRIM(m.city))
        FROM main m
        WHERE m.title IS NOT NULL AND m.city IS NOT NULL
    """)
    existing_pairs = {(row[0], row[1]) for row in c.fetchall()}
    log_msg(log, f"Existing (title, city) pairs: {len(existing_pairs)}")

    # Read CSV
    stats = {
        "total_rows": 0,
        "emails_found": 0,
        "emails_valid": 0,
        "emails_new": 0,
        "emails_duplicate": 0,
        "rows_inserted": 0,
        "rows_skipped_no_email": 0,
        "rows_skipped_garbage": 0,
        "rows_skipped_existing": 0,
    }

    new_contacts = []  # (main_data, lead_data)

    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stats["total_rows"] += 1
            raw_emails = (row.get("emails") or "").strip()

            if not raw_emails:
                stats["rows_skipped_no_email"] += 1
                continue

            # Parse and validate emails
            email_parts = [e.strip() for e in raw_emails.split(",")]
            valid_emails = []
            for e in email_parts:
                e = e.strip().lower()
                if is_valid_email(e):
                    valid_emails.append(e)
                    stats["emails_valid"] += 1

            if not valid_emails:
                stats["rows_skipped_garbage"] += 1
                continue

            stats["emails_found"] += len(email_parts)

            # Parse fields
            title = fix_mojibake((row.get("title") or "").strip())
            sector = fix_mojibake((row.get("category") or "").strip())
            address = fix_mojibake((row.get("address") or "").strip())
            website = fix_website(row.get("website"))
            phone = (row.get("phone") or "").strip() or None
            google_maps = (row.get("link") or "").strip() or None

            city, province, country = parse_complete_address(row.get("complete_address"))
            city = fix_mojibake(city) if city else None
            province = fix_mojibake(province) if province else None
            country = fix_mojibake(country) if country else None

            # For each valid email, create a contact
            for email in valid_emails:
                if email in existing_emails:
                    stats["emails_duplicate"] += 1
                    continue

                stats["emails_new"] += 1
                existing_emails.add(email)  # Prevent duplicates within CSV

                # Secondary emails = other valid emails from same row
                others = [e for e in valid_emails if e != email]
                secondary = ";".join(others) if others else None

                main_data = {
                    "title": title,
                    "sector": sector,
                    "address": address,
                    "city": city,
                    "province": province,
                    "country": country,
                    "entity_type": "empresa",
                }
                lead_data = {
                    "primary_email": email,
                    "secondary_emails": secondary,
                    "website": website,
                    "google_maps": google_maps,
                    "phone": phone,
                }
                new_contacts.append((main_data, lead_data))

    log_msg(log, f"CSV rows: {stats['total_rows']}")
    log_msg(log, f"Emails found: {stats['emails_found']}")
    log_msg(log, f"Emails valid: {stats['emails_valid']}")
    log_msg(log, f"Emails new: {stats['emails_new']}")
    log_msg(log, f"Emails duplicate (in DB): {stats['emails_duplicate']}")
    log_msg(log, f"Contacts to insert: {len(new_contacts)}")

    # Insert in batches
    now = datetime.now().isoformat()
    inserted = 0
    batch_size = 500

    for i in range(0, len(new_contacts), batch_size):
        batch = new_contacts[i:i + batch_size]
        for main_data, lead_data in batch:
            try:
                c.execute("""
                    INSERT INTO main (title, sector, address, city, province, country, entity_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    main_data["title"], main_data["sector"], main_data["address"],
                    main_data["city"], main_data["province"], main_data["country"],
                    main_data["entity_type"],
                ))
                rowid = c.lastrowid

                c.execute("""
                    INSERT INTO lead (ROWID, primary_email, secondary_emails, website, google_maps, phone)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    rowid, lead_data["primary_email"], lead_data["secondary_emails"],
                    lead_data["website"], lead_data["google_maps"], lead_data["phone"],
                ))

                c.execute("""
                    INSERT INTO contact (ROWID, date_added)
                    VALUES (?, ?)
                """, (rowid, now))

                inserted += 1
            except Exception as e:
                log_msg(log, f"ERROR inserting {lead_data['primary_email']}: {e}")

        conn.commit()
        log_msg(log, f"Committed batch {i // batch_size + 1}: {inserted} inserted so far")

    log_msg(log, f"\n=== SUMMARY ===")
    log_msg(log, f"Total inserted: {inserted}")
    log_msg(log, f"Emails skipped (duplicate): {stats['emails_duplicate']}")

    # Final DB count
    c.execute("SELECT COUNT(*) FROM main")
    total_main = c.fetchone()[0]
    c.execute("SELECT COUNT(DISTINCT primary_email) FROM lead WHERE primary_email IS NOT NULL")
    total_emails = c.fetchone()[0]
    log_msg(log, f"DB total contacts: {total_main}")
    log_msg(log, f"DB unique emails: {total_emails}")

    conn.close()
    log.close()
    print(f"\nDone. Log: {LOG_PATH}")


if __name__ == "__main__":
    main()
