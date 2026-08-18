"""
import_gosom_webdata.py — Importa CSVs de gosom/output/webdata/ y web_marketing_caba.csv
Fuentes: 36 UUID CSVs (webdata/) + 1 CSV consolidado (web_marketing_caba.csv)
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

logger = setup_logging("import_gosom_webdata")


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


def extract_emails_from_raw(raw: str) -> list:
    """Extrae emails de多种 formatos: plain, JSON array, regex"""
    if not raw or not raw.strip():
        return []

    raw = raw.strip()

    # Plain email
    if '@' in raw and ' ' not in raw and not raw.startswith('{') and not raw.startswith('['):
        if is_valid_email(raw):
            return [raw.lower()]

    # JSON array format: [{"link":"...","source":"..."}]
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            emails = []
            for item in data:
                if isinstance(item, dict):
                    for v in item.values():
                        if isinstance(v, str) and '@' in v and '.' in v:
                            if is_valid_email(v):
                                emails.append(v.lower())
            if emails:
                return list(dict.fromkeys(emails))
    except (json.JSONDecodeError, TypeError):
        pass

    # Regex fallback
    found = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw)
    valid = []
    for e in found:
        if is_valid_email(e):
            valid.append(e.lower())
    return list(dict.fromkeys(valid))


def import_gosom_webdata_file(filepath: str, stats: dict, conn):
    """Importa un archivo CSV de Gosom (webdata o web_marketing)"""
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
            has_header = 'title' in sample.lower() or 'input_id' in sample.lower()

            if not has_header:
                logger.warning(f"    Sin header detectado, saltando")
                stats["skipped"] += 1
                return

            reader = csv.DictReader(f)
            file_imported = 0
            file_skipped = 0
            file_no_email = 0
            file_errors = 0

            for row_num, row in enumerate(reader, 1):
                try:
                    # Extraer emails (multi-formato)
                    raw_emails = row.get("emails", "") or ""
                    emails = extract_emails_from_raw(raw_emails)

                    if not emails:
                        # Intentar otros campos
                        for field in ["email", "primary_email", "contact_email"]:
                            alt = row.get(field, "") or ""
                            if alt:
                                emails = extract_emails_from_raw(alt)
                                if emails:
                                    break

                    if not emails:
                        file_no_email += 1
                        stats["no_email"] += 1
                        continue

                    # Datos del contacto
                    title = fix_mojibake(row.get("title", "") or "")
                    category = fix_mojibake(row.get("category", "") or "")
                    address = fix_mojibake(row.get("address", "") or "")
                    phone = row.get("phone", "") or ""
                    website = row.get("website", "") or ""
                    google_maps = row.get("link", "") or ""
                    complete_addr = parse_complete_address(row.get("complete_address", "") or "")

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

            logger.info(f"    Importados: {file_imported} | Skip: {file_skipped} | Sin email: {file_no_email} | Errores: {file_errors}")

    except Exception as e:
        logger.error(f"  Error leyendo {filepath}: {e}")
        stats["errors"] += 1


def import_gosom_webdata():
    """Importa todos los CSVs de webdata/ y web_marketing_caba.csv"""
    csv_files = []

    # webdata/ (36 UUID CSVs)
    webdata_dir = SOURCES["gosom_webdata"]
    if os.path.exists(webdata_dir):
        for f in os.listdir(webdata_dir):
            if f.endswith('.csv') and f not in IGNORE_FILES:
                csv_files.append(os.path.join(webdata_dir, f))

    # web_marketing_caba.csv (en gosom/output/)
    web_marketing = os.path.join(SOURCES["gosom_output_root"], "web_marketing_caba.csv")
    if os.path.exists(web_marketing):
        csv_files.append(web_marketing)

    logger.info(f"Encontrados {len(csv_files)} archivos para importar")
    logger.info(f"  - webdata/: {len([f for f in csv_files if 'webdata' in f])} CSVs")
    logger.info(f"  - web_marketing_caba.csv: {'SÍ' if os.path.exists(web_marketing) else 'NO'}")

    stats = {"total": len(csv_files), "imported": 0, "skipped": 0, "errors": 0,
             "duplicates": 0, "no_email": 0, "ignored": 0}

    with get_connection() as conn:
        for filepath in csv_files:
            import_gosom_webdata_file(filepath, stats, conn)

    logger.info("\n" + "=" * 60)
    logger.info("RESUMEN IMPORTACIÓN GOSOM WEBDATA")
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
    import_gosom_webdata()
