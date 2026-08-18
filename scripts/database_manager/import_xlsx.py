"""
import_xlsx.py — Importa archivos XLSX/XLS de contactos (ferias TV/media, DATABASETVMAS)
Fuente: Contactos old/*.xlsx, Contactos old/*.xls
NO BORRA ARCHIVOS ORIGINALES. Solo lee e inserta.
"""

import os
import sys
import re
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_PATH, SOURCES, IGNORE_FILES
from utils import (
    is_valid_email, fix_mojibake, get_connection,
    get_contact_by_email, insert_contact, setup_logging
)

logger = setup_logging("import_xlsx")

# Intentar importar openpyxl (para XLSX) y xlrd (para XLS)
try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False
    logger.warning("openpyxl no instalado. No se podrán leer archivos .xlsx")

try:
    import xlrd
    HAS_XLRD = True
except ImportError:
    HAS_XLRD = False
    logger.warning("xlrd no instalado. No se podrán leer archivos .xls")


def detect_email_column(headers: list) -> int:
    """Detecta la columna que contiene emails"""
    email_keywords = ['email', 'e-mail', 'correo', 'mail', 'correo electronico']
    for i, h in enumerate(headers):
        if h and any(kw in str(h).lower() for kw in email_keywords):
            return i
    return -1


def detect_name_column(headers: list) -> int:
    """Detecta la columna que contiene nombres"""
    name_keywords = ['nombre', 'name', 'contacto', 'empresa', 'company', 'organization']
    for i, h in enumerate(headers):
        if h and any(kw in str(h).lower() for kw in name_keywords):
            return i
    return -1


def detect_phone_column(headers: list) -> int:
    """Detecta la columna que contiene teléfonos"""
    phone_keywords = ['telefono', 'phone', 'tel', 'movil', 'cell', 'sms', 'whatsapp']
    for i, h in enumerate(headers):
        if h and any(kw in str(h).lower() for kw in phone_keywords):
            return i
    return -1


def detect_company_column(headers: list) -> int:
    """Detecta la columna que contiene empresa/compañía"""
    company_keywords = ['empresa', 'company', 'organizacion', 'organization', 'compañia']
    for i, h in enumerate(headers):
        if h and any(kw in str(h).lower() for kw in company_keywords):
            return i
    return -1


def detect_country_column(headers: list) -> int:
    """Detecta la columna que contiene país"""
    country_keywords = ['pais', 'country', 'país']
    for i, h in enumerate(headers):
        if h and any(kw in str(h).lower() for kw in country_keywords):
            return i
    return -1


def detect_city_column(headers: list) -> int:
    """Detecta la columna que contiene ciudad"""
    city_keywords = ['ciudad', 'city', 'localidad', 'municipio']
    for i, h in enumerate(headers):
        if h and any(kw in str(h).lower() for kw in city_keywords):
            return i
    return -1


def read_xlsx(filepath: str) -> list:
    """Lee archivo XLSX y retorna lista de filas (dict)"""
    if not HAS_OPENPYXL:
        logger.error("openpyxl no instalado")
        return []

    try:
        wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        wb.close()

        if len(rows) < 2:
            return []

        headers = [str(h).strip() if h else f"col_{i}" for i, h in enumerate(rows[0])]
        result = []
        for row in rows[1:]:
            if any(cell for cell in row):  # Skip empty rows
                row_dict = {}
                for i, val in enumerate(row):
                    if i < len(headers):
                        row_dict[headers[i]] = str(val).strip() if val else ""
                result.append(row_dict)
        return result
    except Exception as e:
        logger.error(f"Error leyendo XLSX {filepath}: {e}")
        return []


def read_xls(filepath: str) -> list:
    """Lee archivo XLS y retorna lista de filas (dict)"""
    if not HAS_XLRD:
        logger.error("xlrd no instalado")
        return []

    try:
        wb = xlrd.open_workbook(filepath)
        ws = wb.sheet_by_index(0)
        if ws.nrows < 2:
            return []

        headers = [str(ws.cell_value(0, i)).strip() for i in range(ws.ncols)]
        result = []
        for row_idx in range(1, ws.nrows):
            row_dict = {}
            for col_idx in range(ws.ncols):
                val = ws.cell_value(row_idx, col_idx)
                if col_idx < len(headers):
                    row_dict[headers[col_idx]] = str(val).strip() if val else ""
            if any(row_dict.values()):
                result.append(row_dict)
        return result
    except Exception as e:
        logger.error(f"Error leyendo XLS {filepath}: {e}")
        return []


def import_xlsx_file(filepath: str, stats: dict, is_tvmas_master: bool = False):
    """Importa un archivo XLSX/XLS"""
    filename = os.path.basename(filepath)
    ext = os.path.splitext(filename)[1].lower()

    if filename in IGNORE_FILES:
        stats["ignored"] += 1
        return

    logger.info(f"\n  Procesando: {filename}")

    # Leer archivo
    if ext == '.xlsx':
        rows = read_xlsx(filepath)
    elif ext == '.xls':
        rows = read_xls(filepath)
    else:
        logger.warning(f"    Formato no soportado: {ext}")
        stats["skipped"] += 1
        return

    if not rows:
        logger.warning(f"    Sin datos")
        stats["skipped"] += 1
        return

    # Detectar columnas
    headers = list(rows[0].keys())
    email_col = detect_email_column(headers)
    name_col = detect_name_column(headers)
    phone_col = detect_phone_column(headers)
    company_col = detect_company_column(headers)
    country_col = detect_country_column(headers)
    city_col = detect_city_column(headers)

    if email_col == -1:
        logger.warning(f"    No se detectó columna de email. Headers: {headers[:10]}")
        stats["skipped"] += 1
        return

    file_imported = 0
    file_skipped = 0
    file_errors = 0

    with get_connection() as conn:
        for row_num, row in enumerate(rows, 1):
            try:
                # Extraer email
                raw_email = list(row.values())[email_col] if email_col < len(row) else ""
                if not raw_email or not is_valid_email(raw_email):
                    stats["no_email"] += 1
                    continue

                primary_email = raw_email.lower().strip()

                # Verificar duplicado
                existing = get_contact_by_email(conn, primary_email)
                if existing:
                    stats["duplicates"] += 1
                    file_skipped += 1
                    continue

                # Extraer otros campos
                title = None
                if name_col >= 0 and name_col < len(row):
                    title = fix_mojibake(list(row.values())[name_col])
                if not title and company_col >= 0 and company_col < len(row):
                    title = fix_mojibake(list(row.values())[company_col])

                phone = None
                if phone_col >= 0 and phone_col < len(row):
                    phone = list(row.values())[phone_col]

                country = None
                if country_col >= 0 and country_col < len(row):
                    country = fix_mojibake(list(row.values())[country_col])

                city = None
                if city_col >= 0 and city_col < len(row):
                    city = fix_mojibake(list(row.values())[city_col])

                # Determinar entity_type
                entity_type = "empresa"
                if title and any(kw in title.lower() for kw in ["tv", "media", "broadcast", "canal", "produccion"]):
                    entity_type = "empresa"

                # Insertar
                contact_data = {
                    "title": title or None,
                    "sector": None,
                    "address": None,
                    "city": city,
                    "province": None,
                    "country": country,
                    "entity_type": entity_type,
                    "primary_email": primary_email,
                    "secondary_emails": None,
                    "website": None,
                    "google_maps": None,
                    "phone": phone if phone else None,
                }

                insert_contact(conn, contact_data)
                file_imported += 1
                stats["imported"] += 1

            except Exception as e:
                logger.error(f"    Error en fila {row_num}: {e}")
                file_errors += 1
                stats["errors"] += 1

    logger.info(f"    Filas: {len(rows)} | Importados: {file_imported} | Skip: {file_skipped} | Errores: {file_errors}")


def import_all_xlsx():
    """Importa todos los archivos XLSX/XLS de Contactos old/"""
    contactos_old = SOURCES["contactos_old"]
    if not os.path.exists(contactos_old):
        logger.error(f"Directorio no encontrado: {contactos_old}")
        return

    # Encontrar archivos XLSX/XLS
    xlsx_files = []
    for f in os.listdir(contactos_old):
        if f.lower().endswith(('.xlsx', '.xls')) and f not in IGNORE_FILES:
            xlsx_files.append(os.path.join(contactos_old, f))

    # También buscar en backup_fuentes/
    backup_dir = SOURCES["contacts_tvmas_backup"]
    if os.path.exists(backup_dir):
        for f in os.listdir(backup_dir):
            if f.lower().endswith(('.xlsx', '.xls')) and f not in IGNORE_FILES:
                xlsx_files.append(os.path.join(backup_dir, f))

    logger.info(f"Encontrados {len(xlsx_files)} archivos XLSX/XLS")

    stats = {"total": len(xlsx_files), "imported": 0, "skipped": 0, "errors": 0,
             "duplicates": 0, "no_email": 0, "ignored": 0}

    # Procesar DATABASETVMAS primero (prioridad)
    tvmas_files = [f for f in xlsx_files if 'DATABASETVMAS' in os.path.basename(f).upper()]
    other_files = [f for f in xlsx_files if 'DATABASETVMAS' not in os.path.basename(f).upper()]

    for filepath in tvmas_files:
        import_xlsx_file(filepath, stats, is_tvmas_master=True)

    for filepath in other_files:
        import_xlsx_file(filepath, stats)

    logger.info("\n" + "=" * 60)
    logger.info("RESUMEN IMPORTACIÓN XLSX/XLS")
    logger.info("=" * 60)
    logger.info(f"  Total archivos: {stats['total']}")
    logger.info(f"  Importados: {stats['imported']}")
    logger.info(f"  Skip (duplicados/sin email): {stats['duplicates'] + stats['skipped']}")
    logger.info(f"  Errores: {stats['errors']}")
    logger.info("NO se eliminó ningún archivo original.")

    return stats


if __name__ == "__main__":
    import_all_xlsx()
