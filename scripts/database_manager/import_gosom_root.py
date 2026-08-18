"""
import_gosom_root.py — Importa CSVs de gosom/output/ que NO están en general/ ni rrhh/
Fuente: data/inputs/gosom/output/ (zone_CABA.csv, rrhh_grid_*.csv, web_marketing_caba.csv, webdata/*.csv)
NO BORRA ARCHIVOS ORIGINALES. Solo lee e inserta.
"""

import os
import sys
import csv
import json
import re
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_PATH, SOURCES, IGNORE_FILES
from utils import (
    is_valid_email, parse_emails_field, fix_mojibake, fix_website,
    get_connection, get_contact_by_email, insert_contact, setup_logging
)

logger = setup_logging("import_gosom_root")


def parse_complete_address(complete_address_str: str) -> dict:
    """Parsea el JSON de complete_address de Gosom"""
    result = {"city": None, "province": None, "country": None}
    if not complete_address_str:
        return result
    try:
        data = json.loads(complete_address_str)
        result["city"] = data.get("city")
        result["province"] = data.get("state")
        result["country"] = data.get("country")
    except (json.JSONDecodeError, TypeError):
        pass
    return result


def import_gosom_csv(filepath: str, stats: dict, conn):
    """Importa un archivo CSV de Gosom"""
    filename = os.path.basename(filepath)

    if filename in IGNORE_FILES:
        logger.debug(f"  SKIP (ignore): {filename}")
        stats["ignored"] += 1
        return

    logger.info(f"\n  Procesando: {filename}")

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            # Detectar si tiene header
            sample = f.read(1024)
            f.seek(0)
            has_header = 'title' in sample.lower() or 'input_id' in sample.lower()

            if has_header:
                reader = csv.DictReader(f)
            else:
                # Sin header, usar columnas por posición
                reader = csv.reader(f)
                # Saltar, no podemos procesar sin header
                logger.warning(f"    Sin header detectado, saltando")
                stats["skipped"] += 1
                return

            file_imported = 0
            file_skipped = 0
            file_errors = 0

            for row_num, row in enumerate(reader, 1):
                try:
                    # Extraer emails
                    raw_emails = row.get("emails", "")
                    emails = parse_emails_field(raw_emails)

                    if not emails:
                        # Intentar otros campos de email
                        for field in ["email", "primary_email", "contact_email"]:
                            if row.get(field):
                                emails = parse_emails_field(row[field])
                                if emails:
                                    break

                    if not emails:
                        stats["no_email"] += 1
                        continue

                    # Extraer datos del contacto
                    title = fix_mojibake(row.get("title", ""))
                    category = fix_mojibake(row.get("category", ""))
                    address = fix_mojibake(row.get("address", ""))
                    phone = row.get("phone", "")
                    website = row.get("website", "")
                    google_maps = row.get("link", "")

                    # Parsear complete_address
                    complete_addr = parse_complete_address(row.get("complete_address", ""))

                    # Usar el primer email como primario
                    primary_email = emails[0]
                    secondary_emails = ";".join(emails[1:]) if len(emails) > 1 else None

                    # Verificar duplicado
                    existing = get_contact_by_email(conn, primary_email)
                    if existing:
                        stats["duplicates"] += 1
                        file_skipped += 1
                        continue

                    # Insertar
                    contact_data = {
                        "title": title or None,
                        "sector": category or None,
                        "address": address or None,
                        "city": complete_addr["city"],
                        "province": complete_addr["province"],
                        "country": complete_addr["country"],
                        "entity_type": "empresa",
                        "primary_email": primary_email,
                        "secondary_emails": secondary_emails,
                        "website": fix_website(website),
                        "google_maps": google_maps if google_maps else None,
                        "phone": phone if phone else None,
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


def import_gosom_root_files():
    """Importa todos los CSVs de gosom/output/ que no están en general/ ni rrhh/"""
    gosom_root = SOURCES["gosom_output_root"]
    if not os.path.exists(gosom_root):
        logger.error(f"Directorio no encontrado: {gosom_root}")
        return

    # Encontrar CSVs en el root (no en subdirectorios)
    csv_files = []
    for f in os.listdir(gosom_root):
        if f.endswith('.csv') and f not in IGNORE_FILES:
            csv_files.append(os.path.join(gosom_root, f))

    # Encontrar CSVs en webdata/
    webdata_dir = SOURCES["gosom_webdata"]
    if os.path.exists(webdata_dir):
        for f in os.listdir(webdata_dir):
            if f.endswith('.csv') and f not in IGNORE_FILES:
                csv_files.append(os.path.join(webdata_dir, f))

    logger.info(f"Encontrados {len(csv_files)} CSVs para importar en gosom/output/")

    stats = {"total": len(csv_files), "imported": 0, "skipped": 0, "errors": 0,
             "duplicates": 0, "no_email": 0, "ignored": 0}

    with get_connection() as conn:
        for filepath in csv_files:
            import_gosom_csv(filepath, stats, conn)

    logger.info("\n" + "=" * 60)
    logger.info("RESUMEN IMPORTACIÓN GOSOM ROOT")
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
    import_gosom_root_files()
