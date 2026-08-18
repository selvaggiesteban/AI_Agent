"""
import_google_contacts.py — Importa Google Contacts CSVs (mejora cobertura teléfonos)
Fuente: contacts/*.csv, Contactos old/contactos_google/*.csv
NO BORRA ARCHIVOS ORIGINALES. Solo lee e inserta.
"""

import os
import sys
import csv
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_PATH, SOURCES
from utils import (
    is_valid_email, fix_mojibake, get_connection,
    get_contact_by_email, insert_contact, update_contact_field, setup_logging
)

logger = setup_logging("import_google_contacts")


def read_google_contacts_csv(filepath: str) -> list:
    """Lee CSV de Google Contacts y extrae contactos"""
    contacts = []

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for row in reader:
                contact = {}

                # Nombre
                first = (row.get("First Name") or "").strip()
                last = (row.get("Last Name") or "").strip()
                name = f"{first} {last}".strip()
                if name:
                    contact["title"] = fix_mojibake(name)

                # Organización
                org = (row.get("Organization Name") or "").strip()
                if org:
                    contact["organization"] = fix_mojibake(org)

                # Email 1
                email1 = (row.get("E-mail 1 - Value") or "").strip().lower()
                if email1 and is_valid_email(email1):
                    contact["primary_email"] = email1

                # Email 2
                email2 = (row.get("E-mail 2 - Value") or "").strip().lower()
                if email2 and is_valid_email(email2):
                    contact["secondary_emails"] = email2

                # Teléfono 1
                phone1 = (row.get("Phone 1 - Value") or "").strip()
                if phone1:
                    contact["phone"] = phone1

                # Teléfono 2
                phone2 = (row.get("Phone 2 - Value") or "").strip()
                if phone2 and "phone" not in contact:
                    contact["phone"] = phone2

                # Website
                website = (row.get("Website 1 - Value") or "").strip()
                if website:
                    contact["website"] = website

                # Labels
                labels = (row.get("Labels") or "").strip()
                if labels:
                    contact["labels"] = labels

                if contact.get("primary_email") or contact.get("phone"):
                    contacts.append(contact)

    except Exception as e:
        logger.error(f"Error leyendo {filepath}: {e}")

    return contacts


def import_google_contacts_file(filepath: str, stats: dict):
    """Importa un archivo de Google Contacts"""
    filename = os.path.basename(filepath)
    logger.info(f"\n  Procesando: {filename}")

    contacts = read_google_contacts_csv(filepath)
    if not contacts:
        logger.warning(f"    Sin contactos válidos")
        stats["skipped"] += 1
        return

    file_imported = 0
    file_skipped = 0
    file_errors = 0
    file_phone_updated = 0

    with get_connection() as conn:
        for i, contact in enumerate(contacts, 1):
            try:
                email = contact.get("primary_email")
                phone = contact.get("phone")

                # Si tiene email, verificar si ya existe
                if email:
                    existing = get_contact_by_email(conn, email)
                    if existing:
                        # Si existe pero no tiene teléfono, actualizar
                        if phone and not existing.get("phone"):
                            update_contact_field(conn, existing["rowid"], "lead", "phone", phone)
                            file_phone_updated += 1
                            stats["phone_updated"] += 1
                        file_skipped += 1
                        stats["duplicates"] += 1
                        continue

                # Si solo tiene teléfono (sin email), no insertar (no hay forma de deduplicar)
                if not email and phone:
                    stats["phone_only"] += 1
                    continue

                # Insertar nuevo contacto
                contact_data = {
                    "title": contact.get("title") or contact.get("organization"),
                    "sector": None,
                    "address": None,
                    "city": None,
                    "province": None,
                    "country": None,
                    "entity_type": "individual",
                    "primary_email": email,
                    "secondary_emails": contact.get("secondary_emails"),
                    "website": contact.get("website"),
                    "google_maps": None,
                    "phone": phone,
                }

                insert_contact(conn, contact_data)
                file_imported += 1
                stats["imported"] += 1

            except Exception as e:
                logger.error(f"    Error en contacto {i}: {e}")
                file_errors += 1
                stats["errors"] += 1

    logger.info(f"    Contactos: {len(contacts)} | Importados: {file_imported} | Skip: {file_skipped} | Teléfonos actualizados: {file_phone_updated}")


def import_all_google_contacts():
    """Importa todos los CSVs de Google Contacts"""
    # Buscar en múltiples directorios
    directories = [
        SOURCES["contacts_root"],
        SOURCES["contacts_google"],
    ]

    csv_files = []
    for directory in directories:
        if os.path.exists(directory):
            for f in os.listdir(directory):
                if f.lower().endswith('.csv') and 'google' in f.lower() or 'contacts' in f.lower():
                    filepath = os.path.join(directory, f)
                    if filepath not in csv_files:
                        csv_files.append(filepath)

    logger.info(f"Encontrados {len(csv_files)} archivos de Google Contacts")

    stats = {"total": len(csv_files), "imported": 0, "skipped": 0, "errors": 0,
             "duplicates": 0, "phone_only": 0, "phone_updated": 0}

    for filepath in csv_files:
        import_google_contacts_file(filepath, stats)

    logger.info("\n" + "=" * 60)
    logger.info("RESUMEN IMPORTACIÓN GOOGLE CONTACTS")
    logger.info("=" * 60)
    logger.info(f"  Total archivos: {stats['total']}")
    logger.info(f"  Importados: {stats['imported']}")
    logger.info(f"  Skip (duplicados): {stats['duplicates']}")
    logger.info(f"  Solo teléfono (sin email): {stats['phone_only']}")
    logger.info(f"  Teléfonos actualizados en existentes: {stats['phone_updated']}")
    logger.info(f"  Errores: {stats['errors']}")
    logger.info("NO se eliminó ningún archivo original.")

    return stats


if __name__ == "__main__":
    import_all_google_contacts()
