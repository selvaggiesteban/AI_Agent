"""
import_mailrelay.py — Importa contactos de Mailrelay CSV
Fuente: data/inputs/contacts/Contactos old/contactos_mailrelay/
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

logger = setup_logging("import_mailrelay")


def parse_address_parts(address: str) -> dict:
    """Intenta extraer city, province, country de una dirección completa"""
    result = {"city": None, "province": None, "country": None}
    if not address:
        return result

    # Buscar país al final (después de la última coma)
    parts = [p.strip() for p in address.split(",")]
    if len(parts) >= 2:
        # Último componente suele ser país
        last = parts[-1].strip()
        if len(last) <= 30 and not last[0].isdigit():
            result["country"] = last
            # Penúltimo suele ser ciudad/provincia
            if len(parts) >= 3:
                result["city"] = parts[-2].strip()

    return result


def import_mailrelay_csv(filepath: str, stats: dict, conn):
    """Importa un archivo CSV de Mailrelay"""
    filename = os.path.basename(filepath)

    if filename in IGNORE_FILES:
        logger.debug(f"  SKIP (ignore): {filename}")
        stats["ignored"] += 1
        return

    logger.info(f"\n  Procesando: {filename}")

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            sample = f.read(1024)
            f.seek(0)
            has_header = 'email' in sample.lower() or 'nombre' in sample.lower()

            if not has_header:
                logger.warning(f"    Sin header detectado, saltando")
                stats["skipped"] += 1
                return

            reader = csv.DictReader(f)
            file_imported = 0
            file_skipped = 0
            file_errors = 0

            for row_num, row in enumerate(reader, 1):
                try:
                    # Extraer email
                    email = (row.get("Email") or row.get("email") or "").strip().lower()

                    if not email or not is_valid_email(email):
                        stats["no_email"] += 1
                        continue

                    # Verificar duplicado
                    existing = get_contact_by_email(conn, email)
                    if existing:
                        stats["duplicates"] += 1
                        file_skipped += 1
                        continue

                    # Extraer datos
                    nombre = (row.get("Nombre") or row.get("nombre") or "").strip()
                    direccion = (row.get("Direccion") or row.get("direccion") or "").strip()
                    website = (row.get("Pagina web") or row.get("pagina web") or "").strip()
                    phone_sms = (row.get("Telefono SMS") or row.get("telefono sms") or "").strip()
                    phone_whatsapp = (row.get("Telefono WhatsApp") or row.get("telefono whatsapp") or "").strip()
                    grupos = (row.get("Nombre de los grupos") or row.get("nombre de los grupos") or "").strip()

                    # Teléfono: preferir WhatsApp, fallback SMS
                    phone = phone_whatsapp or phone_sms or None

                    # Parsear dirección
                    addr_parts = parse_address_parts(direccion)

                    # Sector: derivar de grupos
                    sector = grupos if grupos else None

                    # Entity type
                    entity_type = "empresa"

                    contact_data = {
                        "title": fix_mojibake(nombre) or None,
                        "sector": fix_mojibake(sector),
                        "address": fix_mojibake(direccion) or None,
                        "city": addr_parts["city"],
                        "province": addr_parts["province"],
                        "country": addr_parts["country"],
                        "entity_type": entity_type,
                        "primary_email": email,
                        "secondary_emails": None,
                        "website": fix_website(website),
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

            logger.info(f"    Importados: {file_imported} | Skip: {file_skipped} | Errores: {file_errors}")

    except Exception as e:
        logger.error(f"  Error leyendo {filepath}: {e}")
        stats["errors"] += 1


def import_mailrelay_files():
    """Importa todos los CSVs de Mailrelay"""
    mailrelay_dir = SOURCES["contacts_mailrelay"]
    if not os.path.exists(mailrelay_dir):
        logger.error(f"Directorio no encontrado: {mailrelay_dir}")
        return

    csv_files = []
    for f in os.listdir(mailrelay_dir):
        if f.endswith('.csv') and f not in IGNORE_FILES:
            csv_files.append(os.path.join(mailrelay_dir, f))

    logger.info(f"Encontrados {len(csv_files)} archivos CSV de Mailrelay")

    stats = {"total": len(csv_files), "imported": 0, "skipped": 0, "errors": 0,
             "duplicates": 0, "no_email": 0, "ignored": 0}

    with get_connection() as conn:
        for filepath in csv_files:
            import_mailrelay_csv(filepath, stats, conn)

    logger.info("\n" + "=" * 60)
    logger.info("RESUMEN IMPORTACIÓN MAILRELAY")
    logger.info("=" * 60)
    logger.info(f"  Total archivos: {stats['total']}")
    logger.info(f"  Importados: {stats['imported']}")
    logger.info(f"  Skip (duplicados): {stats['duplicates']}")
    logger.info(f"  Sin email: {stats['no_email']}")
    logger.info(f"  Ignorados: {stats['ignored']}")
    logger.info(f"  Errores: {stats['errors']}")
    logger.info("NO se eliminó ningún archivo original.")

    return stats


if __name__ == "__main__":
    import_mailrelay_files()
