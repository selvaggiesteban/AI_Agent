"""
import_phone_contacts.py — Importa contactos phone-only de Google Contacts CSV
Fuente: data/inputs/contacts/Contactos old/contacts selvaggiesteban@gmail.com.csv
Maneja deduplicación masiva (15K filas → ~2.4K únicos) y normalización de teléfonos.
NO BORRA ARCHIVOS ORIGINALES. Solo lee e inserta.
"""

import os
import sys
import csv
import re
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_PATH, SOURCES, IGNORE_FILES
from utils import (
    is_valid_email, fix_mojibake, fix_website,
    get_connection, get_contact_by_email, insert_contact, setup_logging
)

logger = setup_logging("import_phone_contacts")

# Phone number as first name (junk detection)
PHONE_AS_NAME_RE = re.compile(r'^[\+\d\s\-\(\)]{7,}$')

# Phone normalization patterns
PHONE_STRIP_RE = re.compile(r'[^\d\+]')


def normalize_phone(phone: str) -> str:
    """Normaliza formato de teléfono argentino"""
    if not phone:
        return None

    # Limpiar
    phone = phone.strip()
    # Remove weird separators like ":::"
    phone = phone.split(":::")[0].strip()
    # Remove extensions
    phone = phone.split("ext")[0].strip()
    phone = phone.split("x")[0].strip() if len(phone.split("x")) <= 2 else phone

    # If starts with 00, replace with +
    if phone.startswith("00"):
        phone = "+" + phone[2:]

    # If doesn't start with +, add +54 if it looks Argentine
    if not phone.startswith("+"):
        # Remove leading 0
        if phone.startswith("0"):
            phone = phone[1:]
        # If starts with 11 or 9 (Buenos Aires mobile/landline)
        if phone.startswith("9") and len(phone) >= 10:
            phone = "+54" + phone
        elif phone.startswith("11") and len(phone) >= 8:
            phone = "+549" + phone
        elif len(phone) >= 8:
            phone = "+54" + phone

    return phone if phone else None


def is_junk_row(first_name: str, last_name: str, phone: str, email: str) -> bool:
    """Detecta filas basura"""
    # Phone number as name
    if first_name and PHONE_AS_NAME_RE.match(first_name):
        return True
    if last_name and PHONE_AS_NAME_RE.match(last_name):
        return True

    # Junk emails
    if email:
        junk = ['sentry', 'wixpress', 'example', 'test', 'demo', '@2x.png']
        for p in junk:
            if p in email.lower():
                return True

    # No name at all
    if not first_name and not last_name and not phone:
        return True

    return False


def get_name_key(first_name: str, last_name: str, phone: str) -> str:
    """Genera clave de deduplicación por nombre + teléfono"""
    parts = []
    if first_name:
        parts.append(first_name.strip().lower())
    if last_name:
        parts.append(last_name.strip().lower())
    name_part = " ".join(parts) if parts else ""
    phone_part = normalize_phone(phone) or ""
    return f"{name_part}|{phone_part}"


def import_phone_csv(filepath: str, stats: dict, conn):
    """Importa un archivo CSV de Google Contacts"""
    filename = os.path.basename(filepath)

    if filename in IGNORE_FILES:
        logger.debug(f"  SKIP (ignore): {filename}")
        stats["ignored"] += 1
        return

    logger.info(f"\n  Procesando: {filename}")

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            sample = f.read(2048)
            f.seek(0)

            if 'First Name' not in sample and 'E-mail' not in sample:
                logger.warning(f"    No es formato Google Contacts, saltando")
                stats["skipped"] += 1
                return

            reader = csv.DictReader(f)
            seen_keys = set()
            file_imported = 0
            file_skipped = 0
            file_junk = 0
            file_errors = 0

            for row_num, row in enumerate(reader, 1):
                try:
                    first_name = (row.get("First Name") or "").strip()
                    last_name = (row.get("Last Name") or "").strip()
                    org_name = (row.get("Organization Name") or "").strip()
                    phone1 = (row.get("Phone 1 - Value") or "").strip()
                    phone2 = (row.get("Phone 2 - Value") or "").strip()
                    email1 = (row.get("E-mail 1 - Value") or "").strip()
                    email2 = (row.get("E-mail 2 - Value") or "").strip()
                    website = (row.get("Website 1 - Value") or "").strip()

                    # Determine primary email
                    primary_email = email1 if is_valid_email(email1) else None
                    if not primary_email and email2 and is_valid_email(email2):
                        primary_email = email2

                    # Determine phone
                    phone = normalize_phone(phone1)
                    if not phone:
                        phone = normalize_phone(phone2)

                    # Skip junk rows
                    if is_junk_row(first_name, last_name, phone, primary_email):
                        file_junk += 1
                        stats["junk"] += 1
                        continue

                    # Skip rows with neither email nor phone
                    if not primary_email and not phone:
                        file_skipped += 1
                        stats["no_data"] += 1
                        continue

                    # Deduplication
                    name_key = get_name_key(first_name, last_name, phone or "")
                    if name_key in seen_keys:
                        file_skipped += 1
                        stats["duplicates"] += 1
                        continue
                    seen_keys.add(name_key)

                    # If has email, check if already in DB
                    if primary_email:
                        existing = get_contact_by_email(conn, primary_email)
                        if existing:
                            file_skipped += 1
                            stats["duplicates"] += 1
                            continue

                    # Build title
                    title_parts = []
                    if first_name:
                        title_parts.append(first_name)
                    if last_name:
                        title_parts.append(last_name)
                    title = " ".join(title_parts) if title_parts else (org_name or None)

                    # Entity type
                    entity_type = "empresa" if org_name else "individual"

                    contact_data = {
                        "title": fix_mojibake(title),
                        "sector": None,
                        "address": None,
                        "city": None,
                        "province": None,
                        "country": "Argentina" if phone and phone.startswith("+54") else None,
                        "entity_type": entity_type,
                        "primary_email": primary_email,
                        "secondary_emails": None,
                        "website": fix_website(website) if website else None,
                        "google_maps": None,
                        "phone": phone,
                    }

                    insert_contact(conn, contact_data)
                    file_imported += 1
                    stats["imported"] += 1

                except Exception as e:
                    logger.error(f"    Error en fila {row_num}: {e}")
                    file_errors += 1
                    stats["errors"] += 1

            logger.info(f"    Importados: {file_imported} | Skip: {file_skipped} | Junk: {file_junk} | Errores: {file_errors}")

    except Exception as e:
        logger.error(f"  Error leyendo {filepath}: {e}")
        stats["errors"] += 1


def import_phone_contacts():
    """Importa contactos phone-only de Google Contacts"""
    # Source: contacts selvaggiesteban@gmail.com.csv
    contacts_old = SOURCES["contactos_old"]
    target_file = os.path.join(contacts_old, "contacts selvaggiesteban@gmail.com.csv")

    if not os.path.exists(target_file):
        logger.error(f"Archivo no encontrado: {target_file}")
        return

    logger.info(f"Procesando: {target_file}")

    stats = {"total": 1, "imported": 0, "skipped": 0, "errors": 0,
             "duplicates": 0, "junk": 0, "no_data": 0, "ignored": 0}

    with get_connection() as conn:
        import_phone_csv(target_file, stats, conn)

    logger.info("\n" + "=" * 60)
    logger.info("RESUMEN IMPORTACIÓN PHONE CONTACTS")
    logger.info("=" * 60)
    logger.info(f"  Importados: {stats['imported']}")
    logger.info(f"  Skip (duplicados): {stats['duplicates']}")
    logger.info(f"  Skip (sin datos): {stats['no_data']}")
    logger.info(f"  Junk filtrados: {stats['junk']}")
    logger.info(f"  Errores: {stats['errors']}")
    logger.info("NO se eliminó ningún archivo original.")

    return stats


if __name__ == "__main__":
    import_phone_contacts()
