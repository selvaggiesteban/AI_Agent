"""
import_vcf.py — Importa contactos WhatsApp (VCF) a contacts.db
Fuente: data/inputs/whatsapp_backup/WhatsApp/vCards/*.vcf
NO BORRA ARCHIVOS ORIGINALES. Solo lee e inserta.
"""

import os
import sys
import re
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_PATH, SOURCES
from utils import (
    is_valid_email, fix_mojibake, get_connection,
    get_contact_by_email, insert_contact, setup_logging
)

logger = setup_logging("import_vcf")


def parse_vcf(filepath: str) -> dict:
    """Parsea archivo VCF y extrae datos del contacto"""
    data = {
        "title": None,
        "phone": None,
        "email": None,
        "website": None,
        "organization": None,
    }

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"  Error leyendo {filepath}: {e}")
        return data

    lines = content.split('\n')
    for line in lines:
        line = line.strip()

        # Nombre (FN o N)
        if line.startswith('FN:') or line.startswith('N:'):
            name = line.split(':', 1)[1].strip()
            if name and not name.startswith(';'):
                data["title"] = fix_mojibake(name)

        # Teléfono
        if 'TEL' in line and ':' in line:
            phone = line.split(':', 1)[1].strip()
            if phone:
                data["phone"] = phone

        # Email
        if 'EMAIL' in line and ':' in line:
            email = line.split(':', 1)[1].strip()
            if email and is_valid_email(email):
                data["email"] = email.lower()

        # Organización
        if 'ORG' in line and ':' in line:
            org = line.split(':', 1)[1].strip().rstrip(';')
            if org:
                data["organization"] = fix_mojibake(org)

        # Website
        if 'URL' in line and ':' in line:
            url = line.split(':', 1)[1].strip()
            if url:
                data["website"] = url

    # Si no hay título pero hay organización, usar organización
    if not data["title"] and data["organization"]:
        data["title"] = data["organization"]

    # Si no hay título, usar nombre del archivo
    if not data["title"]:
        basename = os.path.splitext(os.path.basename(filepath))[0]
        data["title"] = fix_mojibake(basename)

    return data


def import_vcf_files():
    """Importa todos los archivos VCF del directorio de WhatsApp"""
    vcards_dir = SOURCES["whatsapp_vcards"]
    if not os.path.exists(vcards_dir):
        logger.error(f"Directorio no encontrado: {vcards_dir}")
        return

    vcf_files = [f for f in os.listdir(vcards_dir) if f.endswith('.vcf')]
    logger.info(f"Encontrados {len(vcf_files)} archivos VCF en {vcards_dir}")

    stats = {"total": len(vcf_files), "imported": 0, "skipped": 0, "errors": 0, "with_email": 0, "phone_only": 0}

    with get_connection() as conn:
        for i, vcf_file in enumerate(vcf_files, 1):
            filepath = os.path.join(vcards_dir, vcf_file)
            data = parse_vcf(filepath)

            if not data["title"] and not data["phone"] and not data["email"]:
                logger.warning(f"  [{i}/{len(vcf_files)}] SKIP (sin datos): {vcf_file}")
                stats["skipped"] += 1
                continue

            # Determinar entity_type
            entity_type = "individual"  # WhatsApp contacts son personas

            # Preparar datos para inserción
            contact_data = {
                "title": data["title"],
                "phone": data["phone"],
                "primary_email": data["email"],
                "website": data["website"],
                "entity_type": entity_type,
                "sector": None,
                "address": None,
                "city": None,
                "province": None,
                "country": None,
            }

            # Verificar si ya existe por email
            if data["email"]:
                existing = get_contact_by_email(conn, data["email"])
                if existing:
                    logger.debug(f"  [{i}/{len(vcf_files)}] SKIP (email existente): {data['email']}")
                    stats["skipped"] += 1
                    continue
                stats["with_email"] += 1
            else:
                stats["phone_only"] += 1

            # Insertar
            try:
                rowid = insert_contact(conn, contact_data)
                stats["imported"] += 1
                logger.info(f"  [{i}/{len(vcf_files)}] OK: {data['title']} | {data['phone'] or '-'} | {data['email'] or '-'}")
            except Exception as e:
                logger.error(f"  [{i}/{len(vcf_files)}] ERROR: {vcf_file}: {e}")
                stats["errors"] += 1

    logger.info("\n" + "=" * 60)
    logger.info("RESUMEN IMPORTACIÓN VCF")
    logger.info("=" * 60)
    logger.info(f"  Total archivos: {stats['total']}")
    logger.info(f"  Importados: {stats['imported']}")
    logger.info(f"  Skip (duplicados/sin datos): {stats['skipped']}")
    logger.info(f"  Errores: {stats['errors']}")
    logger.info(f"  Con email: {stats['with_email']}")
    logger.info(f"  Solo teléfono: {stats['phone_only']}")
    logger.info("NO se eliminó ningún archivo original.")

    return stats


if __name__ == "__main__":
    import_vcf_files()
