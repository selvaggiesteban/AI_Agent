"""
utils.py — Funciones compartidas para enriquecimiento de contacts.db
Validación, encoding, conexión a DB, logging
"""

import os
import re
import csv
import json
import sqlite3
import logging
from datetime import datetime
from contextlib import contextmanager
from typing import Optional, List, Dict, Any, Set

# === CONFIG ===
from config import DB_PATH, LOG_DIR

# === EMAIL VALIDATION ===
EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

JUNK_PATTERNS = [
    "sentry", "wixpress", "example", "test", "demo",
    "@2x.png", "@2x.webp", ".js", "username@domain", "your@mail",
    "juan.perez", "beispiel", "ejemplo", "mysite",
]

AUTO_REPLY_PATTERNS = [
    "noreply", "no-reply", "mailer-daemon", "postmaster", "abuse",
    "auto-reply", "donotreply", "auto_submit",
]

PLACEHOLDER_EMAILS = {
    "tunombre@email.com", "usuario@dominio.com", "nombre@ejemplo.com",
    "john@doe.com", "info@yourdomain.com", "info@website.com",
    "hola@miempresa.es", "email@example.com", "ejemplo@mail.com",
    "email@ejemplo.com", "nombre@mail.com", "theratio_interior@mail.com",
}

# === MOJIBAKE (DOUBLE-ENCODED UTF-8) ===
MOJIBAKE_MAP = {
    "\u00c3\u00b1": "\u00f1",  # Ã± -> ñ
    "\u00c3\u00a9": "\u00e9",  # Ã© -> é
    "\u00c3\u00a1": "\u00e1",  # Ã¡ -> á
    "\u00c3\u00b3": "\u00f3",  # Ã³ -> ó
    "\u00c3\u00ad": "\u00ed",  # Ã­ -> í
    "\u00c3\u00bc": "\u00fc",  # Ã¼ -> ü
    "\u00c3\u00a0": "\u00e0",  # Ã  -> à
    "\u00c3\u00a8": "\u00e8",  # Ã¨ -> è
    "\u00c3\u00b2": "\u00f2",  # Ã´ -> ò
    "\u00c3\u00a2": "\u00e2",  # Ã¢ -> â
    "\u00c3\u00a4": "\u00e4",  # Ã¤ -> ä
    "\u00c3\u00b6": "\u00f6",  # Ã¶ -> ö
    "\u00c3\u00a7": "\u00e7",  # Ã§ -> ç
    "\u00c3\u00ae": "\u00ee",  # Ã® -> î
    "\u00c2\u00b0": "\u00b0",  # Â° -> °
    "\u00c2\u00ba": "\u00ba",  # Âº -> º
    "\u00c2\u00b7": "",        # Â· -> (remove)
}

MOJIBAKE_DETECT_CHARS = ["\u00c3", "\u00c2"]


# === FUNCIONES DE EMAIL ===

def is_valid_email(email: str) -> bool:
    """Valida email con regex + blacklist + auto-reply + placeholders"""
    if not email or not email.strip():
        return False
    email = email.strip().lower()
    if not EMAIL_REGEX.match(email):
        return False
    for p in JUNK_PATTERNS:
        if p in email:
            return False
    for p in AUTO_REPLY_PATTERNS:
        if p in email:
            return False
    if email in PLACEHOLDER_EMAILS:
        return False
    return True


def parse_emails_field(raw: str) -> List[str]:
    """Parsea campo de múltiples emails (separados por ; , o espacio)"""
    if not raw or not raw.strip():
        return []
    # Separar por ; , o espacio
    parts = re.split(r'[;,;\s]+', raw.strip())
    valid = []
    for p in parts:
        p = p.strip().strip('"').strip("'")
        if is_valid_email(p):
            valid.append(p.lower())
    return list(dict.fromkeys(valid))  # deduplicar preservando orden


def split_emails(primary: str, secondary: str) -> tuple:
    """Divide emails en primary y secondary (lista semicolon-separated)"""
    all_emails = []
    if primary and is_valid_email(primary):
        all_emails.append(primary.lower())
    if secondary:
        for e in parse_emails_field(secondary):
            if e not in all_emails:
                all_emails.append(e)
    if not all_emails:
        return None, None
    return all_emails[0], ";".join(all_emails[1:]) if len(all_emails) > 1 else None


# === FUNCIONES DE ENCODING ===

def fix_mojibake(text: str) -> Optional[str]:
    """Corrige mojibake (double-encoded UTF-8)"""
    if not text:
        return text
    if not any(c in text for c in MOJIBAKE_DETECT_CHARS):
        return text
    result = text
    for bad, good in MOJIBAKE_MAP.items():
        result = result.replace(bad, good)
    return result


def fix_website(url: str) -> Optional[str]:
    """Normaliza URL de website"""
    if not url or not url.strip():
        return None
    url = url.strip()
    if url.lower() in ("website", "http://website", "https://website"):
        return None
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url


# === CONEXION A BASE DE DATOS ===

@contextmanager
def get_connection(db_path: str = None):
    """Context manager para conexión SQLite con WAL mode"""
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def validate_schema(conn: sqlite3.Connection, table: str, required_columns: List[str]) -> Set[str]:
    """Verifica que las columnas existan en la tabla. Retorna columnas faltantes."""
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    existing = {row[1] for row in cur.fetchall()}
    missing = set(required_columns) - existing
    if missing:
        logging.warning(f"Columnas faltantes en {table}: {missing}")
    return missing


def get_contact_by_email(conn: sqlite3.Connection, email: str) -> Optional[Dict]:
    """Busca contacto por email primario. Retorna dict con ROWID + todos los campos."""
    cur = conn.cursor()
    cur.execute("""
        SELECT m.ROWID,
               m.title, m.sector, m.address, m.city, m.province, m.country, m.entity_type,
               l.primary_email, l.secondary_emails, l.website, l.google_maps, l.phone,
               l.facebook, l.instagram, l.messenger, l.whatsapp, l.linkedin, l.telegram, l.x, l.youtube,
               c.sender, c.deliverability, c.email_last_response, c.date_added
        FROM main m
        JOIN lead l ON m.ROWID = l.ROWID
        JOIN contact c ON m.ROWID = c.ROWID
        WHERE l.primary_email = ?
    """, (email.lower(),))
    row = cur.fetchone()
    if not row:
        return None
    return {
        "rowid": row[0],
        "title": row[1], "sector": row[2], "address": row[3], "city": row[4],
        "province": row[5], "country": row[6], "entity_type": row[7],
        "primary_email": row[8], "secondary_emails": row[9], "website": row[10],
        "google_maps": row[11], "phone": row[12],
        "facebook": row[13], "instagram": row[14], "messenger": row[15],
        "whatsapp": row[16], "linkedin": row[17], "telegram": row[18],
        "x": row[19], "youtube": row[20],
        "sender": row[21], "deliverability": row[22], "email_last_response": row[23],
        "date_added": row[24],
    }


def insert_contact(conn: sqlite3.Connection, data: Dict) -> int:
    """Inserta contacto nuevo en las 3 tablas (main + lead + contact). Retorna ROWID."""
    cur = conn.cursor()
    now = datetime.now().isoformat()

    cur.execute("""
        INSERT INTO main (title, sector, address, city, province, country, entity_type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        fix_mojibake(data.get("title")),
        fix_mojibake(data.get("sector")),
        fix_mojibake(data.get("address")),
        fix_mojibake(data.get("city")),
        fix_mojibake(data.get("province")),
        fix_mojibake(data.get("country")),
        data.get("entity_type", "empresa"),
    ))
    rowid = cur.lastrowid

    email = data.get("primary_email")
    secondary = data.get("secondary_emails")
    if email and not secondary:
        email, secondary = split_emails(email, None)

    cur.execute("""
        INSERT INTO lead (primary_email, secondary_emails, website, google_maps, phone,
                          facebook, instagram, messenger, whatsapp, linkedin, telegram, x, youtube)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        email, secondary,
        fix_website(data.get("website")),
        data.get("google_maps"),
        data.get("phone"),
        data.get("facebook"), data.get("instagram"), data.get("messenger"),
        data.get("whatsapp"), data.get("linkedin"), data.get("telegram"),
        data.get("x"), data.get("youtube"),
    ))

    cur.execute("""
        INSERT INTO contact (sender, deliverability, email_last_response, date_added)
        VALUES (?, ?, ?, ?)
    """, (
        data.get("sender"),
        data.get("deliverability"),
        data.get("email_last_response"),
        now,
    ))

    return rowid


def update_contact_field(conn: sqlite3.Connection, rowid: int, table: str, field: str, value: Any) -> bool:
    """Actualiza un campo específico solo si el actual está vacío"""
    if value is None or value == "":
        return False
    cur = conn.cursor()
    cur.execute(f"SELECT {field} FROM {table} WHERE ROWID = ?", (rowid,))
    current = cur.fetchone()
    if current and current[0] is not None and current[0] != "":
        return False  # Ya tiene dato, no sobrescribir
    cur.execute(f"UPDATE {table} SET {field} = ? WHERE ROWID = ?", (value, rowid))
    return True


# === LOGGING ===

def setup_logging(name: str, log_file: str = None) -> logging.Logger:
    """Configura logging para scripts de enriquecimiento"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler
    if log_file:
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


# === ESTADÍSTICAS ===

def get_db_stats(conn: sqlite3.Connection) -> Dict:
    """Retorna estadísticas completas de la DB"""
    cur = conn.cursor()
    stats = {}
    stats["total"] = cur.execute("SELECT COUNT(*) FROM main").fetchone()[0]

    for table in ["main", "lead", "contact"]:
        cur.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cur.fetchall()]
        for col in columns:
            if col in ("facebook", "instagram", "messenger", "whatsapp", "linkedin", "telegram", "x", "youtube"):
                continue  # Skip social media (ya sabemos que están vacías)
            cur.execute(f"SELECT COUNT(*) FROM {table} WHERE {col} IS NOT NULL AND {col} != ''")
            count = cur.fetchone()[0]
            stats[f"{table}.{col}"] = count

    stats["campaigns"] = cur.execute("SELECT COUNT(*) FROM campaign").fetchone()[0]
    return stats
