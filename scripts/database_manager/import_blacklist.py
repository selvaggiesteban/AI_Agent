"""
import_blacklist.py — Importa CONTACTOS RECHAZADOS.docx como blacklist
Fuente: Contactos old/CONTACTOS RECHAZADOS.docx
NO BORRA ARCHIVOS ORIGINALES. Solo lee y marca contactos existentes.
"""

import os
import sys
import re
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_PATH, SOURCES
from utils import (
    is_valid_email, get_connection, setup_logging
)

logger = setup_logging("import_blacklist")

# Intentar importar python-docx para leer .docx
try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False
    logger.warning("python-docx no instalado. No se podrán leer archivos .docx")


def read_docx(filepath: str) -> list:
    """Lee archivo .docx y retorna líneas de texto"""
    if not HAS_DOCX:
        logger.error("python-docx no instalado")
        return []

    try:
        doc = docx.Document(filepath)
        lines = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                lines.append(text)
        return lines
    except Exception as e:
        logger.error(f"Error leyendo {filepath}: {e}")
        return []


def extract_emails_from_text(lines: list) -> list:
    """Extrae emails de líneas de texto"""
    email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
    emails = []
    for line in lines:
        found = email_pattern.findall(line)
        for email in found:
            email = email.lower().strip()
            if is_valid_email(email):
                emails.append(email)
    return list(set(emails))


def mark_as_blacklisted(conn, emails: list) -> int:
    """Marca contactos como blacklisted (usando deliverability='BLACKLISTED')"""
    cur = conn.cursor()
    marked = 0

    for email in emails:
        # Buscar el contacto
        cur.execute("SELECT ROWID FROM lead WHERE primary_email = ?", (email,))
        row = cur.fetchone()
        if row:
            rowid = row[0]
            # Marcar como blacklisted
            cur.execute("""
                UPDATE contact SET deliverability = 'BLACKLISTED'
                WHERE ROWID = ? AND (deliverability IS NULL OR deliverability != 'BLACKLISTED')
            """, (rowid,))
            if cur.rowcount > 0:
                marked += 1
                logger.info(f"  BLACKLISTED: {email}")

    return marked


def import_blacklist():
    """Importa la blacklist de CONTACTOS RECHAZADOS.docx"""
    filepath = os.path.join(SOURCES["contactos_old"], "CONTACTOS RECHAZADOS.docx")

    if not os.path.exists(filepath):
        logger.error(f"Archivo no encontrado: {filepath}")
        return

    logger.info(f"Leyendo blacklist de: {filepath}")

    # Leer documento
    lines = read_docx(filepath)
    if not lines:
        logger.warning("No se encontraron líneas en el documento")
        return

    logger.info(f"Líneas encontradas: {len(lines)}")

    # Extraer emails
    emails = extract_emails_from_text(lines)
    logger.info(f"Emails válidos encontrados: {len(emails)}")

    if not emails:
        logger.warning("No se encontraron emails válidos en la blacklist")
        return

    # Marcar en la DB
    with get_connection() as conn:
        marked = mark_as_blacklisted(conn, emails)

    logger.info("\n" + "=" * 60)
    logger.info("RESUMEN IMPORTACIÓN BLACKLIST")
    logger.info("=" * 60)
    logger.info(f"  Emails en documento: {len(emails)}")
    logger.info(f"  Marcados como BLACKLISTED: {marked}")
    logger.info(f"  No encontrados en DB: {len(emails) - marked}")
    logger.info("NO se eliminó ningún archivo original.")
    logger.info("NO se eliminó ningún contacto. Solo se marcó deliverability='BLACKLISTED'.")

    return {"emails": len(emails), "marked": marked}


if __name__ == "__main__":
    import_blacklist()
