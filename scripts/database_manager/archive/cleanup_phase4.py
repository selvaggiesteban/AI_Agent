"""
Fase 4: Eliminar filas con emails junk/test/placeholders
"""

import sqlite3
import os

DB_PATH = os.path.join("data", "inputs", "contacts.db")


def delete_junk_emails(conn):
    """Eliminar filas con emails junk."""
    cur = conn.cursor()

    # Patrones exactos de email (case insensitive via LOWER)
    exact_junks = [
        "tunombre@email.com",
        "usuario@dominio.com",
        "nombre@ejemplo.com",
        "john@doe.com",
        "info@yourdomain.com",
        "info@website.com",
        "hola@miempresa.es",
        "email@example.com",
        "ejemplo@mail.com",
        "email@ejemplo.com",
        "nombre@mail.com",
        "theratio_interior@mail.com",
    ]

    # Dominios junk
    junk_domains = [
        "example.com",
        "ejemplo.com",
    ]

    # Substrings en email (que sean el email completo, no substrings)
    # sentry y wixpress aparecen en el dominio
    junk_domain_substrings = [
        "sentry",
        "wixpress",
    ]

    total = 0

    # Eliminar emails exactos
    for email in exact_junks:
        cur.execute("DELETE FROM main WHERE LOWER(primary_email) = ?", (email.lower(),))
        if cur.rowcount > 0:
            print(f"  DELETE '{email}': {cur.rowcount}")
            total += cur.rowcount

    # Eliminar por dominio exacto
    for domain in junk_domains:
        cur.execute("DELETE FROM main WHERE LOWER(primary_email) LIKE ?", (f"%@{domain}",))
        if cur.rowcount > 0:
            print(f"  DELETE *@{domain}: {cur.rowcount}")
            total += cur.rowcount

    # Eliminar por substring en dominio (sentry, wixpress)
    for substr in junk_domain_substrings:
        cur.execute("DELETE FROM main WHERE LOWER(primary_email) LIKE ?", (f"%{substr}%",))
        if cur.rowcount > 0:
            print(f"  DELETE *{substr}*: {cur.rowcount}")
            total += cur.rowcount

    conn.commit()

    # Verificar
    cur.execute("SELECT COUNT(*) FROM main")
    remaining = cur.fetchone()[0]
    print(f"\nFilas eliminadas: {total}")
    print(f"Filas restantes: {remaining}")

    return total


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "..", DB_PATH)

    print("=== Fase 4: Deduplicar emails junk ===\n")

    conn = sqlite3.connect(db_path)
    deleted = delete_junk_emails(conn)
    conn.close()

    print(f"\n=== COMPLETADO: {deleted} filas eliminadas ===")
