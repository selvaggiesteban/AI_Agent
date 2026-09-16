"""
Fase 3: Normalizar datos existentes en contacts.db
- Reemplazar vacios "" por NULL
- Limpiar country (N/D, S/N, numeros)
- Normalizar deliverability
- Normalizar last_validation_status
- Normalizar entity_type
- Normalizar smtp_processed
- Normalizar email_last_response
- Fix encoding en title
- Fix name-doubling en title
"""

import sqlite3
import os
import re
from datetime import datetime

DB_PATH = os.path.join("data", "inputs", "contacts.db")


def normalize_empty_strings(conn):
    """Reemplazar cadenas vacias por NULL en 8 columnas."""
    cur = conn.cursor()
    columns = ["title", "sector", "phone", "city", "province", "address", "google_maps", "email_last_response"]
    total = 0
    for col in columns:
        cur.execute(f'UPDATE main SET {col} = NULL WHERE {col} = ""')
        total += cur.rowcount
        print(f"  {col}: {cur.rowcount} vacios -> NULL")
    conn.commit()
    print(f"Total vacios eliminados: {total}")


def normalize_website(conn):
    """Renombrada de urls: cadenas vacias -> NULL."""
    cur = conn.cursor()
    cur.execute('UPDATE main SET website = NULL WHERE website = ""')
    print(f"  website: {cur.rowcount} vacios -> NULL")
    conn.commit()


def normalize_country(conn):
    """Limpiar datos sucios en country."""
    cur = conn.cursor()
    junk_values = ["N/D", "S/N"]
    total = 0
    for val in junk_values:
        cur.execute("UPDATE main SET country = NULL WHERE country = ?", (val,))
        total += cur.rowcount
        print(f"  country '{val}': {cur.rowcount} -> NULL")
    # Numeros 1-20
    for i in range(1, 21):
        cur.execute("UPDATE main SET country = NULL WHERE country = ?", (str(i),))
        total += cur.rowcount
        if cur.rowcount > 0:
            print(f"  country '{i}': {cur.rowcount} -> NULL")
    # Normalizar Espana -> Espana (con eñe)
    cur.execute("UPDATE main SET country = 'España' WHERE country = 'Espana'")
    total += cur.rowcount
    print(f"  country 'Espana' -> 'Espana': {cur.rowcount}")
    conn.commit()
    print(f"Total country limpiados: {total}")


def normalize_deliverability(conn):
    """Normalizar valores de deliverability."""
    cur = conn.cursor()
    mappings = {
        "falta primer envio SMTP": "pending",
        "Fallo SMTP/Limite": "smtp_fail",
        "Dominio Invalido/DNS Error": "invalid_domain",
    }
    total = 0
    for old, new in mappings.items():
        cur.execute("UPDATE main SET deliverability = ? WHERE deliverability = ?", (new, old))
        total += cur.rowcount
        print(f"  deliverability '{old}' -> '{new}': {cur.rowcount}")
    conn.commit()
    print(f"Total deliverability normalizados: {total}")


def normalize_validation_status(conn):
    """Normalizar valores de last_validation_status."""
    cur = conn.cursor()
    mappings = {
        "validated": "valid",
        "VALID": "valid",
        "INVALID_DOMAIN": "invalid_domain",
        "INVALID_SYNTAX": "invalid_syntax",
        "DNS_ERROR: resolve() got an unexpected keyword argument 'timeout'": "dns_error",
        "DNS_WARN:TypeError": "dns_warn",
    }
    total = 0
    for old, new in mappings.items():
        cur.execute("UPDATE main SET last_validation_status = ? WHERE last_validation_status = ?", (new, old))
        total += cur.rowcount
        print(f"  validation_status '{old}' -> '{new}': {cur.rowcount}")
    conn.commit()
    print(f"Total validation_status normalizados: {total}")


def normalize_entity_type(conn):
    """Normalizar valores de entity_type."""
    cur = conn.cursor()
    mappings = {
        "Organizacion con fines de lucro": "empresa",
        "Contacto suelto": "individual",
        "Profesional independiente": "individual",
        "Organizacion sin fines de lucro": "ong",
        "Empresa": "empresa",
    }
    total = 0
    for old, new in mappings.items():
        cur.execute("UPDATE main SET entity_type = ? WHERE entity_type = ?", (new, old))
        total += cur.rowcount
        print(f"  entity_type '{old}' -> '{new}': {cur.rowcount}")
    # No clasificado -> NULL
    cur.execute("UPDATE main SET entity_type = NULL WHERE entity_type = 'No clasificado'")
    total += cur.rowcount
    print(f"  entity_type 'No clasificado' -> NULL: {cur.rowcount}")
    conn.commit()
    print(f"Total entity_type normalizados: {total}")


def normalize_smtp_processed(conn):
    """Normalizar valores de smtp_processed."""
    cur = conn.cursor()
    cur.execute('UPDATE main SET smtp_processed = NULL WHERE smtp_processed = "0"')
    print(f"  smtp_processed '0' -> NULL: {cur.rowcount}")
    cur.execute('UPDATE main SET smtp_processed = NULL WHERE smtp_processed = "INVALID"')
    print(f"  smtp_processed 'INVALID' -> NULL: {cur.rowcount}")
    conn.commit()


def normalize_email_last_response(conn):
    """Normalizar valores de email_last_response."""
    cur = conn.cursor()
    mappings = {
        "SMTP_OK": "delivered",
        "SMTP_FAIL": "failed",
        "pending_reply": "pending",
    }
    total = 0
    for old, new in mappings.items():
        cur.execute("UPDATE main SET email_last_response = ? WHERE email_last_response = ?", (new, old))
        total += cur.rowcount
        print(f"  email_last_response '{old}' -> '{new}': {cur.rowcount}")
    conn.commit()
    print(f"Total email_last_response normalizados: {total}")


def fix_title_encoding(conn):
    """Fix mojibake en title (UTF-8 doble)."""
    cur = conn.cursor()
    # Buscar patrones de mojibake comunes
    mojibake_patterns = [
        ("Ã±", "ñ"), ("Ã©", "é"), ("Ã¡", "á"), ("Ã³", "ó"),
        ("Ã­", "í"), ("Ã¼", "ü"), ("Ã!", "ñ"), ("Â«", "«"),
        ("Â»", "»"), ("Ã'", "á"), ("Ã´", "ó"), ("Ã¨", "è"),
        ("Ã ", "à"), ("Ã¢", "â"), ("Ã¤", "ä"), ("Ã¶", "ö"),
        ("Ã¼", "ü"), ("Ã§", "ç"), ("Ã®", "î"), ("Ã´", "ô"),
    ]
    total = 0
    for bad, good in mojibake_patterns:
        cur.execute(f"UPDATE main SET title = REPLACE(title, ?, ?) WHERE title LIKE ?", (bad, good, f"%{bad}%"))
        if cur.rowcount > 0:
            total += cur.rowcount
            print(f"  title mojibake '{bad}' -> '{good}': {cur.rowcount}")
    conn.commit()
    print(f"Total title encoding fixes: {total}")


def fix_title_namedoubling(conn):
    """Fix name-doubling en title (ej: 'Carlos Luengo Carlos Luengo')."""
    cur = conn.cursor()
    cur.execute("SELECT ROWID, title FROM main WHERE title IS NOT NULL")
    rows = cur.fetchall()
    total = 0
    for rowid, title in rows:
        words = title.split()
        if len(words) >= 2:
            half = len(words) // 2
            if words[:half] == words[half:] and len(words) >= 4:
                new_title = " ".join(words[:half])
                cur.execute("UPDATE main SET title = ? WHERE ROWID = ?", (new_title, rowid))
                total += 1
    conn.commit()
    print(f"Total title name-doubling fixes: {total}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "..", DB_PATH)

    print("=== Fase 3: Normalizar datos existentes ===\n")

    conn = sqlite3.connect(db_path)

    print("--- 3a. Vacios -> NULL ---")
    normalize_empty_strings(conn)

    print("\n--- 3b. Website vacios -> NULL ---")
    normalize_website(conn)

    print("\n--- 3c. Country ---")
    normalize_country(conn)

    print("\n--- 3d. Deliverability ---")
    normalize_deliverability(conn)

    print("\n--- 3e. Validation status ---")
    normalize_validation_status(conn)

    print("\n--- 3f. Entity type ---")
    normalize_entity_type(conn)

    print("\n--- 3g. Smtp processed ---")
    normalize_smtp_processed(conn)

    print("\n--- 3h. Email last response ---")
    normalize_email_last_response(conn)

    print("\n--- 3i. Title encoding ---")
    fix_title_encoding(conn)

    print("\n--- 3j. Title name-doubling ---")
    fix_title_namedoubling(conn)

    conn.close()
    print("\n=== COMPLETADO ===")
