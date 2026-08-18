"""
Fase 9: Crear 5 tablas nuevas
- social_networks
- quotes
- contracts
- billing
- chats
"""

import sqlite3
import os

DB_PATH = os.path.join("data", "inputs", "contacts.db")


def create_tables(conn):
    """Crear las 5 tablas nuevas."""
    cur = conn.cursor()

    # social_networks
    cur.execute("""
        CREATE TABLE IF NOT EXISTS social_networks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_email TEXT,
            platform TEXT,
            profile_url TEXT,
            username TEXT,
            status TEXT,
            last_checked TEXT,
            date_added TEXT
        )
    """)
    print("  social_networks creada")

    # quotes
    cur.execute("""
        CREATE TABLE IF NOT EXISTS quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_email TEXT,
            quote_number TEXT,
            subject TEXT,
            amount REAL,
            currency TEXT,
            status TEXT,
            date_created TEXT,
            date_sent TEXT,
            date_resolved TEXT,
            notes TEXT
        )
    """)
    print("  quotes creada")

    # contracts
    cur.execute("""
        CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_email TEXT,
            contract_number TEXT,
            subject TEXT,
            amount REAL,
            currency TEXT,
            status TEXT,
            date_start TEXT,
            date_end TEXT,
            date_signed TEXT,
            payment_terms TEXT,
            notes TEXT
        )
    """)
    print("  contracts creada")

    # billing
    cur.execute("""
        CREATE TABLE IF NOT EXISTS billing (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_email TEXT,
            invoice_number TEXT,
            contract_id INTEGER,
            amount REAL,
            currency TEXT,
            status TEXT,
            date_issued TEXT,
            date_due TEXT,
            date_paid TEXT,
            payment_method TEXT,
            notes TEXT
        )
    """)
    print("  billing creada")

    # chats
    cur.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_email TEXT,
            platform TEXT,
            direction TEXT,
            message TEXT,
            timestamp TEXT,
            status TEXT,
            agent TEXT
        )
    """)
    print("  chats creada")

    conn.commit()

    # Verificar
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cur.fetchall()
    print(f"\nTablas en la DB: {len(tables)}")
    for t in tables:
        print(f"  {t[0]}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "..", DB_PATH)

    print("=== Fase 9: Crear 5 tablas nuevas ===\n")

    conn = sqlite3.connect(db_path)
    create_tables(conn)
    conn.close()

    print("\n=== COMPLETADO ===")
