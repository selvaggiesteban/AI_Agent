"""
Importador de datos Gosom RRHH -> contacts.db
Lee CSVs y TXTs de data/inputs/gosom/output/rrhh/
Deduplica por title+city (interactivo: Skip/Update/Merge)
Valida emails (regex + blacklist)
Corrige mojibake en textos
Solo escribe con flag --write
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
RRHH_DIR = os.path.join(PROJECT_ROOT, "data", "inputs", "gosom", "output", "rrhh")
DB_PATH = os.path.join(PROJECT_ROOT, "data", "inputs", "contacts.db")

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
    if not text or not any(c in text for c in MOJIBAKE_DETECT_CHARS):
        return text
    result = text
    for bad, good in MOJIBAKE_MAP.items():
        result = result.replace(bad, good)
    return result


def normalize_website(url):
    if not url or not url.strip():
        return None
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


def parse_complete_address(ca_str):
    if not ca_str or not ca_str.strip():
        return "", "", ""
    try:
        ca = json.loads(ca_str)
        city = (ca.get("city") or "").strip()
        state = (ca.get("state") or "").strip()
        country = (ca.get("country") or "").strip()
        return city, state, country
    except (json.JSONDecodeError, TypeError):
        return "", "", ""


def parse_emails(emails_str):
    if not emails_str or not emails_str.strip():
        return [], []
    raw = [e.strip() for e in emails_str.split(",") if e.strip()]
    valid = []
    invalid = []
    for e in raw:
        if is_valid_email(e):
            valid.append(e.lower())
        else:
            invalid.append(e)
    return valid, invalid


def make_dedup_key(title, city):
    t = (title or "").strip().lower()
    c = (city or "").strip().lower()
    return (t, c)


def read_all_csvs(rrhh_dir):
    csv_files = [f for f in os.listdir(rrhh_dir) if f.endswith(".csv")]
    all_rows = []
    for f in sorted(csv_files):
        path = os.path.join(rrhh_dir, f)
        with open(path, "r", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                all_rows.append(row)
    return all_rows


def read_all_txts(rrhh_dir):
    txt_files = [f for f in os.listdir(rrhh_dir) if f.endswith(".txt")]
    all_emails = set()
    for f in sorted(txt_files):
        path = os.path.join(rrhh_dir, f)
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
            for e in content.split(","):
                e = e.strip()
                if e and is_valid_email(e):
                    all_emails.add(e.lower())
    return list(all_emails)


def deduplicate_csv_rows(rows):
    seen = {}
    unique = []
    dups = 0
    for row in rows:
        title = (row.get("title") or "").strip()
        city_raw = ""
        ca = row.get("complete_address", "")
        if ca and ca.strip():
            city_raw, _, _ = parse_complete_address(ca)
        key = make_dedup_key(title, city_raw)
        if key in seen:
            dups += 1
        else:
            seen[key] = True
            unique.append(row)
    return unique, dups


def check_existing_in_db(conn, csv_emails, csv_title_city_keys):
    cur = conn.cursor()

    # Check emails
    existing_emails = set()
    email_list = list(csv_emails)
    for i in range(0, len(email_list), 500):
        chunk = email_list[i:i + 500]
        placeholders = ",".join(["?"] * len(chunk))
        cur.execute(
            f"SELECT LOWER(primary_email) FROM lead WHERE LOWER(primary_email) IN ({placeholders})",
            chunk,
        )
        for r in cur.fetchall():
            existing_emails.add(r[0])

    # Check title+city
    existing_titles = set()
    title_list = [k[0] for k in csv_title_city_keys if k[0]]
    for i in range(0, len(title_list), 500):
        chunk = title_list[i:i + 500]
        placeholders = ",".join(["?"] * len(chunk))
        cur.execute(
            f"SELECT DISTINCT LOWER(title) FROM main WHERE LOWER(title) IN ({placeholders})",
            chunk,
        )
        for r in cur.fetchall():
            existing_titles.add(r[0])

    return existing_emails, existing_titles


def build_contact_from_csv_row(row):
    title = fix_mojibake((row.get("title") or "").strip())
    sector = fix_mojibake((row.get("category") or "").strip())
    address = fix_mojibake((row.get("address") or "").strip())
    link = (row.get("link") or "").strip()
    website = (row.get("website") or "").strip()
    phone = (row.get("phone") or "").strip()
    emails_raw = (row.get("emails") or "").strip()
    city, state, country = parse_complete_address(row.get("complete_address", ""))
    city = fix_mojibake(city)
    state = fix_mojibake(state)
    country = fix_mojibake(country)

    valid_emails, invalid_emails = parse_emails(emails_raw)
    primary_email = valid_emails[0] if valid_emails else None
    secondary_emails = ";".join(valid_emails[1:]) if len(valid_emails) > 1 else None
    website = normalize_website(website)

    return {
        "title": title or None,
        "sector": sector or None,
        "address": address or None,
        "city": city or None,
        "province": state or None,
        "country": country or None,
        "entity_type": "empresa",
        "primary_email": primary_email,
        "secondary_emails": secondary_emails,
        "website": website,
        "google_maps": link or None,
        "phone": phone or None,
        "date_added": datetime.now().isoformat(),
        "_invalid_emails": invalid_emails,
        "_all_valid_emails": valid_emails,
    }


def insert_contact(conn, contact):
    cur = conn.cursor()

    cur.execute(
        """INSERT INTO main (id, title, sector, address, city, province, country, entity_type)
           VALUES (NULL, ?, ?, ?, ?, ?, ?, ?)""",
        (contact["title"], contact["sector"], contact["address"],
         contact["city"], contact["province"], contact["country"],
         contact["entity_type"]),
    )
    rowid = cur.lastrowid

    cur.execute(
        """INSERT INTO lead (primary_email, secondary_emails, website, google_maps, phone,
                              facebook, instagram, messenger, whatsapp, linkedin,
                              telegram, x, youtube)
           VALUES (?, ?, ?, ?, ?, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL)""",
        (contact["primary_email"], contact["secondary_emails"],
         contact["website"], contact["google_maps"], contact["phone"]),
    )

    cur.execute(
        """INSERT INTO contact (sender, deliverability, email_last_response,
                                  last_validation_date, last_validation_status,
                                  last_subject_received, smtp_processed,
                                  form_processed, date_added)
           VALUES (NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, ?)""",
        (contact["date_added"],),
    )

    return rowid


def interactive_dedup(existing_row, new_contact):
    print("\n" + "=" * 60)
    print("DUPLICADO ENCONTRADO:")
    print(f"  Existente: ROWID={existing_row['rowid']} | title='{existing_row['title']}' | city='{existing_row['city']}' | email='{existing_row['primary_email']}'")
    print(f"  Nuevo:     title='{new_contact['title']}' | city='{new_contact['city']}' | email='{new_contact['primary_email']}'")
    print("  Opciones: [S]kip / [U]pdate / [M]erge")
    if not sys.stdin.isatty():
        print("  > S (auto-skip: stdin no interactivo)")
        return "S"
    sys.stdout.write("  > ")
    sys.stdout.flush()
    choice = sys.stdin.readline().strip().upper()
    return choice or "S"


def get_existing_row(conn, title):
    cur = conn.cursor()
    cur.execute(
        """SELECT m.ROWID, m.title, m.sector, m.address, m.city, m.province, m.country,
                  l.primary_email, l.secondary_emails, l.website, l.google_maps, l.phone
           FROM main m
           LEFT JOIN lead l ON m.ROWID = l.ROWID
           WHERE LOWER(m.title) = LOWER(?)
           LIMIT 1""",
        (title,),
    )
    row = cur.fetchone()
    if not row:
        return None
    return {
        "rowid": row[0], "title": row[1], "sector": row[2], "address": row[3],
        "city": row[4], "province": row[5], "country": row[6],
        "primary_email": row[7], "secondary_emails": row[8], "website": row[9],
        "google_maps": row[10], "phone": row[11],
    }


def update_existing_row(conn, rowid, contact):
    cur = conn.cursor()
    cur.execute(
        """UPDATE main SET sector = COALESCE(?, sector),
                           address = COALESCE(?, address),
                           city = COALESCE(?, city),
                           province = COALESCE(?, province),
                           country = COALESCE(?, country),
                           entity_type = COALESCE(?, entity_type)
           WHERE ROWID = ?""",
        (contact["sector"], contact["address"], contact["city"],
         contact["province"], contact["country"], contact["entity_type"], rowid),
    )
    cur.execute(
        """UPDATE lead SET primary_email = COALESCE(?, primary_email),
                            secondary_emails = COALESCE(?, secondary_emails),
                            website = COALESCE(?, website),
                            phone = COALESCE(?, phone)
           WHERE ROWID = ?""",
        (contact["primary_email"], contact["secondary_emails"],
         contact["website"], contact["phone"], rowid),
    )
    return rowid


def merge_existing_row(conn, rowid, existing, contact):
    cur = conn.cursor()

    new_sector = existing["sector"] if existing["sector"] else contact["sector"]
    new_address = existing["address"] if existing["address"] else contact["address"]
    new_city = existing["city"] if existing["city"] else contact["city"]
    new_province = existing["province"] if existing["province"] else contact["province"]
    new_country = existing["country"] if existing["country"] else contact["country"]
    new_email = existing["primary_email"] if existing["primary_email"] else contact["primary_email"]
    new_website = existing["website"] if existing["website"] else contact["website"]
    new_phone = existing["phone"] if existing["phone"] else contact["phone"]

    cur.execute(
        """UPDATE main SET sector = ?, address = ?, city = ?, province = ?, country = ?
           WHERE ROWID = ?""",
        (new_sector, new_address, new_city, new_province, new_country, rowid),
    )
    cur.execute(
        """UPDATE lead SET primary_email = ?, website = ?, phone = ?
           WHERE ROWID = ?""",
        (new_email, new_website, new_phone, rowid),
    )
    return rowid


def main():
    write_mode = "--write" in sys.argv

    print("=" * 60)
    print("IMPORTADOR GOSOM RRHH -> contacts.db")
    print(f"Modo: {'ESCRITURA' if write_mode else 'DRY-RUN (no escribe)'}")
    print(f"Directorio: {RRHH_DIR}")
    print(f"DB: {DB_PATH}")
    print("=" * 60)

    # 1. Leer CSVs
    print("\n[1/6] Leyendo CSVs...")
    all_rows = read_all_csvs(RRHH_DIR)
    print(f"  Filas CSV totales: {len(all_rows)}")

    # 2. Dedup CSVs
    print("\n[2/6] Deduplicando CSVs (title+city)...")
    unique_rows, dups = deduplicate_csv_rows(all_rows)
    print(f"  Duplicados internos: {dups}")
    print(f"  Filas unicas: {len(unique_rows)}")

    # 3. Leer TXTs
    print("\n[3/6] Leyendo TXTs...")
    txt_emails = read_all_txts(RRHH_DIR)
    print(f"  Emails validos en TXTs: {len(txt_emails)}")

    # 4. Build contacts from CSV rows
    print("\n[4/6] Procesando contactos...")
    csv_contacts = []
    total_invalid_emails = 0
    for row in unique_rows:
        contact = build_contact_from_csv_row(row)
        total_invalid_emails += len(contact["_invalid_emails"])
        csv_contacts.append(contact)

    # 5. Check existing in DB
    print("\n[5/6] Verificando duplicados en DB...")
    conn = sqlite3.connect(DB_PATH)

    csv_emails = set()
    for c in csv_contacts:
        for e in c["_all_valid_emails"]:
            csv_emails.add(e)
    for e in txt_emails:
        csv_emails.add(e)

    csv_title_city_keys = set()
    for c in csv_contacts:
        csv_title_city_keys.add(make_dedup_key(c["title"], c["city"]))

    existing_emails, existing_titles = check_existing_in_db(conn, csv_emails, csv_title_city_keys)
    print(f"  Emails ya en DB: {len(existing_emails)}")
    print(f"  Titles ya en DB: {len(existing_titles)}")

    # 6. Reporte final
    print("\n[6/6] REPORTE FINAL ESPERADO")
    print("=" * 60)
    print(f"  Filas CSV originales:        {len(all_rows):>8}")
    print(f"  Duplicados internos CSV:     {dups:>8}")
    print(f"  Contactos unicos CSV:        {len(unique_rows):>8}")
    print(f"  Emails TXTs validos:          {len(txt_emails):>8}")
    print(f"  Emails invalidos descartados: {total_invalid_emails:>8}")
    print(f"  Emails validos unicos:       {len(csv_emails):>8}")
    print(f"    ya existen en DB:          {len(existing_emails):>8}")
    print(f"    nuevos a importar:         {len(csv_emails) - len(existing_emails):>8}")
    print(f"  Contactos con email:         {sum(1 for c in csv_contacts if c['primary_email']):>8}")
    print(f"  Contactos sin email:         {sum(1 for c in csv_contacts if not c['primary_email']):>8}")
    print()
    print(f"  Titles ya en DB (duplicados): {len(existing_titles):>8}")
    print(f"  Titles nuevos:               {len(csv_title_city_keys) - len(existing_titles) > 0 and len(csv_title_city_keys) - len(existing_titles):>8}")

    # Calcular estado final
    new_contacts_csv = 0
    dup_contacts_csv = 0
    for c in csv_contacts:
        key = make_dedup_key(c["title"], c["city"])
        title_lower = (c["title"] or "").lower()
        if title_lower and title_lower in existing_titles:
            dup_contacts_csv += 1
        else:
            new_contacts_csv += 1

    new_txt = len([e for e in txt_emails if e not in existing_emails])

    print()
    print(f"  === RESUMEN IMPORTACION ===")
    print(f"  CSV contactos nuevos:        {new_contacts_csv:>8}")
    print(f"  CSV contactos duplicados:    {dup_contacts_csv:>8}  (Skip/Update/Merge interactivo)")
    print(f"  TXT emails nuevos:          {new_txt:>8}")
    print(f"  TOTAL nuevos a insertar:     {new_contacts_csv + new_txt:>8}")
    print("=" * 60)

    if not write_mode:
        print("\n*** MODO DRY-RUN: no se escribio nada ***")
        print("    Para importar de verdad: python import_rrhh_gosom.py --write")
        conn.close()
        return

    # === IMPORTACION REAL ===
    print("\n" + "=" * 60)
    print("INICIANDO IMPORTACION REAL...")
    print("=" * 60)

    inserted = 0
    skipped = 0
    updated = 0
    merged = 0
    errors = 0

    # Importar CSV contacts
    print("\n[CSV] Procesando contactos...")
    dup_log = open(os.path.join(PROJECT_ROOT, "data", "inputs", "gosom_duplicates_skipped.txt"), "w", encoding="utf-8")
    dup_log.write("ROWID\tdb_title\tdb_email\tnew_title\tnew_city\tnew_email\n")
    for i, contact in enumerate(csv_contacts):
        title_lower = (contact["title"] or "").lower()
        email_lower = (contact["primary_email"] or "").lower()

        # Skip si el email ya existe en la DB
        if email_lower and email_lower in existing_emails:
            skipped += 1
            dup_log.write(f"\t(email exists)\t{email_lower}\t{contact['title']}\t{contact['city']}\t{contact['primary_email']}\n")
            continue

        # Skip si el title+city ya existe en la DB
        if title_lower and title_lower in existing_titles:
            existing_row = get_existing_row(conn, contact["title"])
            if existing_row:
                choice = interactive_dedup(existing_row, contact)
                if choice == "S":
                    skipped += 1
                    dup_log.write(f"{existing_row['rowid']}\t{existing_row['title']}\t{existing_row['primary_email']}\t{contact['title']}\t{contact['city']}\t{contact['primary_email']}\n")
                    continue
                elif choice == "U":
                    update_existing_row(conn, existing_row["rowid"], contact)
                    updated += 1
                    continue
                elif choice == "M":
                    merge_existing_row(conn, existing_row["rowid"], existing_row, contact)
                    merged += 1
                    continue
            else:
                print("  WARNING: title en set pero no encontrado en DB, insertando...")

        # Insertar nuevo
        try:
            insert_contact(conn, contact)
            inserted += 1
            if email_lower:
                existing_emails.add(email_lower)
        except Exception as e:
            print(f"  ERROR inserting: {e}")
            errors += 1

        if (i + 1) % 500 == 0:
            print(f"  Procesados: {i + 1}/{len(csv_contacts)} | Insertados: {inserted} | Skipped: {skipped} | Updated: {updated} | Merged: {merged}")
            conn.commit()

    conn.commit()

    # Importar TXT emails
    print(f"\n[TXT] Importando {len(txt_emails)} emails...")
    txt_inserted = 0
    for email in txt_emails:
        if email in existing_emails:
            continue
        contact = {
            "title": None,
            "sector": None,
            "address": None,
            "city": None,
            "province": None,
            "country": None,
            "entity_type": "empresa",
            "primary_email": email,
            "secondary_emails": None,
            "website": None,
            "google_maps": None,
            "phone": None,
            "date_added": datetime.now().isoformat(),
        }
        try:
            insert_contact(conn, contact)
            txt_inserted += 1
        except Exception as e:
            print(f"  ERROR inserting TXT email {email}: {e}")
            errors += 1

    conn.commit()
    conn.close()
    dup_log.close()

    print("\n" + "=" * 60)
    print("IMPORTACION COMPLETADA")
    print("=" * 60)
    print(f"  CSV insertados:   {inserted:>8}")
    print(f"  CSV skipped:      {skipped:>8}")
    print(f"  CSV updated:      {updated:>8}")
    print(f"  CSV merged:       {merged:>8}")
    print(f"  TXT insertados:   {txt_inserted:>8}")
    print(f"  Errores:          {errors:>8}")
    print(f"  TOTAL insertados: {inserted + txt_inserted:>8}")
    print(f"  Duplicados skipped: {skipped:>8}")
    print(f"  -> Log duplicados: data/inputs/gosom_duplicates_skipped.txt")
    print("=" * 60)


if __name__ == "__main__":
    main()
