"""
import_linkedin_profiles.py — Importa perfiles de LinkedIn (sin email/teléfono)
Fuentes: data/outputs/linkedin/people_*.csv, authors_*.csv
Almacena: name + linkedin URL + search_keyword como sector
NO BORRA ARCHIVOS ORIGINALES. Solo lee e inserta.
"""

import os
import sys
import csv
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_PATH, SOURCES
from utils import (
    fix_mojibake, get_connection, insert_contact, setup_logging
)

logger = setup_logging("import_linkedin_profiles")


def parse_name(full_name: str) -> tuple:
    """Divide nombre completo en first/last"""
    if not full_name:
        return "", ""
    parts = full_name.strip().split()
    if len(parts) == 1:
        return parts[0], ""
    elif len(parts) == 2:
        return parts[0], parts[1]
    else:
        # First name = first part, last name = rest
        return parts[0], " ".join(parts[1:])


def normalize_linkedin_url(url: str) -> str:
    """Normaliza URL de LinkedIn"""
    if not url:
        return None
    url = url.strip()
    if not url.startswith("http"):
        url = "https://" + url
    # Remove trailing slash
    url = url.rstrip("/")
    return url


def import_linkedin_file(filepath: str, stats: dict, conn):
    """Importa un archivo CSV de LinkedIn"""
    filename = os.path.basename(filepath)

    # Skip non-contact files
    if "jobs" in filename.lower() or "posts" in filename.lower():
        logger.debug(f"  SKIP (no-contact): {filename}")
        stats["skipped"] += 1
        return

    logger.info(f"\n  Procesando: {filename}")

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            sample = f.read(1024)
            f.seek(0)

            if 'name' not in sample.lower() or 'profile_url' not in sample.lower():
                logger.warning(f"    Formato no reconocido, saltando")
                stats["skipped"] += 1
                return

            reader = csv.DictReader(f)
            file_imported = 0
            file_skipped = 0
            file_errors = 0

            for row_num, row in enumerate(reader, 1):
                try:
                    name = (row.get("name") or "").strip()
                    profile_url = (row.get("profile_url") or "").strip()
                    search_keyword = (row.get("search_keyword") or "").strip()

                    if not name:
                        file_skipped += 1
                        continue

                    # Parse name
                    first_name, last_name = parse_name(name)
                    title = f"{first_name} {last_name}".strip()

                    # Normalize LinkedIn URL
                    linkedin_url = normalize_linkedin_url(profile_url)

                    # Check duplicate by title (name) + linkedin
                    if linkedin_url:
                        cur = conn.cursor()
                        cur.execute(
                            "SELECT 1 FROM lead WHERE linkedin = ?",
                            (linkedin_url,)
                        )
                        if cur.fetchone():
                            file_skipped += 1
                            stats["duplicates"] += 1
                            continue

                    # Also check by title (name) alone
                    cur = conn.cursor()
                    cur.execute(
                        "SELECT 1 FROM main WHERE title = ? AND entity_type = ?",
                        (title, "individual")
                    )
                    if cur.fetchone():
                        file_skipped += 1
                        stats["duplicates"] += 1
                        continue

                    # Derive country from search keyword or name patterns
                    country = None
                    if "argentina" in search_keyword.lower() or "ar" in search_keyword.lower():
                        country = "Argentina"

                    contact_data = {
                        "title": fix_mojibake(title),
                        "sector": search_keyword if search_keyword else None,
                        "address": None,
                        "city": None,
                        "province": None,
                        "country": country,
                        "entity_type": "individual",
                        "primary_email": None,
                        "secondary_emails": None,
                        "website": None,
                        "google_maps": None,
                        "phone": None,
                        "linkedin": linkedin_url,
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


def import_linkedin_profiles():
    """Importa perfiles de LinkedIn"""
    linkedin_dir = os.path.join(PROJECT_ROOT, "data", "outputs", "linkedin")

    if not os.path.exists(linkedin_dir):
        logger.error(f"Directorio no encontrado: {linkedin_dir}")
        return

    csv_files = []
    for f in os.listdir(linkedin_dir):
        if f.endswith('.csv'):
            csv_files.append(os.path.join(linkedin_dir, f))

    logger.info(f"Encontrados {len(csv_files)} archivos CSV de LinkedIn")

    stats = {"total": len(csv_files), "imported": 0, "skipped": 0, "errors": 0,
             "duplicates": 0}

    with get_connection() as conn:
        for filepath in csv_files:
            import_linkedin_file(filepath, stats, conn)

    logger.info("\n" + "=" * 60)
    logger.info("RESUMEN IMPORTACIÓN LINKEDIN PROFILES")
    logger.info("=" * 60)
    logger.info(f"  Total archivos: {stats['total']}")
    logger.info(f"  Importados: {stats['imported']}")
    logger.info(f"  Skip (duplicados): {stats['duplicates']}")
    logger.info(f"  Skip (otros): {stats['skipped']}")
    logger.info(f"  Errores: {stats['errors']}")
    logger.info("NO se eliminó ningún archivo original.")

    return stats


if __name__ == "__main__":
    from config import PROJECT_ROOT
    import_linkedin_profiles()
