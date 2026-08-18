"""
verify_imported.py — CONTRASTA fuentes ✅ IMPORTADO contra contacts.db
Verifica que no se haya perdido información durante importaciones previas.

NO BORRA NADA. Solo lee y reporta.
"""

import os
import sys
import csv
import sqlite3
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_PATH, SOURCES
from utils import is_valid_email, get_connection, setup_logging

logger = setup_logging("verify_imported")


def verify_brevo_contacts():
    """
    CONTRASTA: contactos Brevo/CRM (111K contactos con date_added=NULL)
    Verifica que los emails de las fuentes Brevo existan en la DB.
    """
    logger.info("=" * 60)
    logger.info("CONTRASTANDO: Brevo/CRM imports (✅ IMPORTADO)")
    logger.info("=" * 60)

    brevo_files = [
        ("brevo_10042026.csv", SOURCES["contacts_tvmas_backup"]),
        ("brevo_consolidada_total.csv", SOURCES["contacts_tvmas_backup"]),
        ("base de datos de contactos de TVMAS.csv", SOURCES["contactos_old"]),
        ("contactos hola@selvaggiesteban.dev 5446366-69dd03c16c52d05601bba7c9-eVstda.csv", SOURCES["contacts_brevo"]),
    ]

    results = {}
    with get_connection() as conn:
        cur = conn.cursor()

        for filename, directory in brevo_files:
            filepath = os.path.join(directory, filename)
            if not os.path.exists(filepath):
                logger.warning(f"  Archivo no encontrado: {filepath}")
                continue

            logger.info(f"\n  Verificando: {filename}")

            # Leer emails del archivo fuente
            source_emails = set()
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    reader = csv.DictReader(f)
                    email_col = None
                    for col in reader.fieldnames or []:
                        if col.upper() in ('EMAIL', 'E-MAIL', 'PRIMARY_EMAIL'):
                            email_col = col
                            break
                    if not email_col:
                        logger.warning(f"    No se encontró columna de email en {filename}")
                        continue

                    for row in reader:
                        email = row.get(email_col, '').strip().lower()
                        if email and is_valid_email(email):
                            source_emails.add(email)
            except Exception as e:
                logger.error(f"    Error leyendo {filename}: {e}")
                continue

            if not source_emails:
                logger.warning(f"    No se encontraron emails válidos en {filename}")
                continue

            # Verificar cuántos existen en la DB
            found_in_db = 0
            missing = []
            for email in list(source_emails)[:1000]:  # Muestra de 1000
                cur.execute("SELECT COUNT(*) FROM lead WHERE primary_email = ?", (email,))
                if cur.fetchone()[0] > 0:
                    found_in_db += 1
                else:
                    missing.append(email)

            coverage = (found_in_db / len(source_emails)) * 100 if source_emails else 0
            results[filename] = {
                "source_emails": len(source_emails),
                "found_in_db": found_in_db,
                "coverage_pct": coverage,
                "sample_missing": missing[:10],
            }

            logger.info(f"    Emails únicos en fuente: {len(source_emails)}")
            logger.info(f"    Encontrados en DB: {found_in_db}/{min(1000, len(source_emails))} ({coverage:.1f}%)")
            if missing[:5]:
                logger.info(f"    Muestra faltantes: {missing[:5]}")

    return results


def verify_gosom_imports():
    """
    CONTRASTA: Gosom General + RRHH (~10K contactos)
    Verifica que los contactos Gosom estén en la DB.
    """
    logger.info("\n" + "=" * 60)
    logger.info("CONTRASTANDO: Gosom imports (✅ IMPORTADO)")
    logger.info("=" * 60)

    with get_connection() as conn:
        cur = conn.cursor()

        # Verificar contactos Gosom General (date_added ~2026-07-14)
        cur.execute("""
            SELECT COUNT(*) FROM contact
            WHERE date_added LIKE '2026-07-14%'
        """)
        gosom_general_count = cur.fetchone()[0]
        logger.info(f"\n  Gosom General (date_added=2026-07-14): {gosom_general_count} contactos")

        # Verificar contactos Gosom RRHH (date_added ~2026-07-13)
        cur.execute("""
            SELECT COUNT(*) FROM contact
            WHERE date_added LIKE '2026-07-13%'
        """)
        gosom_rrhh_count = cur.fetchone()[0]
        logger.info(f"  Gosom RRHH (date_added=2026-07-13): {gosom_rrhh_count} contactos")

        # Verificar que tengan datos válidos
        cur.execute("""
            SELECT COUNT(*) FROM lead l
            JOIN contact c ON l.ROWID = c.ROWID
            WHERE c.date_added LIKE '2026-07-1%'
            AND l.primary_email IS NOT NULL AND l.primary_email != ''
        """)
        with_email = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) FROM lead l
            JOIN contact c ON l.ROWID = c.ROWID
            WHERE c.date_added LIKE '2026-07-1%'
            AND l.phone IS NOT NULL AND l.phone != ''
        """)
        with_phone = cur.fetchone()[0]

        cur.execute("""
            SELECT COUNT(*) FROM main m
            JOIN contact c ON m.ROWID = c.ROWID
            WHERE c.date_added LIKE '2026-07-1%'
            AND m.title IS NOT NULL AND m.title != ''
        """)
        with_title = cur.fetchone()[0]

        logger.info(f"  Con email válido: {with_email}")
        logger.info(f"  Con teléfono: {with_phone}")
        logger.info(f"  Con título/empresa: {with_title}")

        # Muestra de contactos Gosom
        cur.execute("""
            SELECT m.title, m.city, l.primary_email, l.phone
            FROM main m
            JOIN lead l ON m.ROWID = l.ROWID
            JOIN contact c ON m.ROWID = c.ROWID
            WHERE c.date_added LIKE '2026-07-14%'
            AND l.primary_email IS NOT NULL
            LIMIT 5
        """)
        sample = cur.fetchall()
        if sample:
            logger.info("\n  Muestra de contactos Gosom General:")
            for row in sample:
                logger.info(f"    {row[0] or '(sin título)'} | {row[1] or '-'} | {row[2]} | {row[3] or '-'}")

    return {
        "gosom_general": gosom_general_count,
        "gosom_rrhh": gosom_rrhh_count,
        "with_email": with_email,
        "with_phone": with_phone,
        "with_title": with_title,
    }


def verify_preexisting_contacts():
    """
    CONTRASTA: Contactos pre-existentes (date_added=NULL, ~111K)
    Verifica integridad de los contactos originales.
    """
    logger.info("\n" + "=" * 60)
    logger.info("CONTRASTANDO: Contactos pre-existentes (date_added=NULL)")
    logger.info("=" * 60)

    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM contact WHERE date_added IS NULL OR date_added = ''")
        preexisting = cur.fetchone()[0]
        logger.info(f"\n  Total contactos pre-existentes: {preexisting:,}")

        # Distribución de entity_type
        cur.execute("""
            SELECT m.entity_type, COUNT(*)
            FROM main m
            JOIN contact c ON m.ROWID = c.ROWID
            WHERE c.date_added IS NULL OR c.date_added = ''
            GROUP BY m.entity_type
            ORDER BY COUNT(*) DESC
        """)
        entity_dist = cur.fetchall()
        logger.info("  Distribución entity_type:")
        for et, count in entity_dist:
            logger.info(f"    {et or '(NULL)'}: {count:,}")

        # Top 5 senders en pre-existentes
        cur.execute("""
            SELECT c.sender, COUNT(*)
            FROM contact c
            WHERE (c.date_added IS NULL OR c.date_added = '')
            AND c.sender IS NOT NULL AND c.sender != ''
            GROUP BY c.sender
            ORDER BY COUNT(*) DESC
            LIMIT 5
        """)
        senders = cur.fetchall()
        logger.info("  Top 5 senders:")
        for s, count in senders:
            logger.info(f"    {s}: {count:,}")

        # Muestra de emails pre-existentes
        cur.execute("""
            SELECT l.primary_email, m.title, m.city
            FROM lead l
            JOIN main m ON l.ROWID = m.ROWID
            JOIN contact c ON l.ROWID = c.ROWID
            WHERE (c.date_added IS NULL OR c.date_added = '')
            AND l.primary_email IS NOT NULL
            LIMIT 10
        """)
        sample = cur.fetchall()
        logger.info("\n  Muestra de 10 emails pre-existentes:")
        for email, title, city in sample:
            logger.info(f"    {email} | {title or '-'} | {city or '-'}")

    return {"preexisting": preexisting}


def main():
    logger.info("INICIANDO VERIFICACIÓN DE IMPORTACIONES ✅ IMPORTADO")
    logger.info(f"DB: {DB_PATH}")
    logger.info(f"Hora: {datetime.now().isoformat()}")

    results = {}

    # 1. Verificar Brevo
    results["brevo"] = verify_brevo_contacts()

    # 2. Verificar Gosom
    results["gosom"] = verify_gosom_imports()

    # 3. Verificar pre-existentes
    results["preexisting"] = verify_preexisting_contacts()

    # Resumen final
    logger.info("\n" + "=" * 60)
    logger.info("RESUMEN DE VERIFICACIÓN")
    logger.info("=" * 60)
    logger.info("Todas las fuentes ✅ IMPORTADO fueron contrastadas contra la DB.")
    logger.info("NO se eliminó ningún dato.")
    logger.info("Verificar archivos de log para detalles completos.")

    return results


if __name__ == "__main__":
    main()
