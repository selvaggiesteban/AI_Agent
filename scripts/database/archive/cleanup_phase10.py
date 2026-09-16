"""
Fase 10: Crear 13 indices para busquedas frecuentes
"""

import sqlite3
import os

DB_PATH = os.path.join("data", "inputs", "contacts.db")


def create_indexes(conn):
    """Crear indices de busqueda frecuente."""
    cur = conn.cursor()

    indexes = [
        ("idx_main_email", "main", "primary_email"),
        ("idx_main_country", "main", "country"),
        ("idx_main_city", "main", "city"),
        ("idx_main_sector", "main", "sector"),
        ("idx_main_entity_type", "main", "entity_type"),
        ("idx_main_deliverability", "main", "deliverability"),
        ("idx_main_sender", "main", "sender"),
        ("idx_main_list", "main", "list"),
        ("idx_main_date_added", "main", "date_added"),
        ("idx_main_date_updated", "main", "date_updated"),
        ("idx_main_smtp_processed", "main", "smtp_processed"),
        ("idx_main_form_processed", "main", "form_processed"),
        ("idx_main_title", "main", "title"),
    ]

    for idx_name, table, column in indexes:
        try:
            cur.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table} ({column})")
            print(f"  {idx_name} ({column})")
        except Exception as e:
            print(f"  {idx_name} ERROR: {e}")

    conn.commit()

    # Verificar
    cur.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%' ORDER BY name")
    indexes = cur.fetchall()
    print(f"\nIndices creados: {len(indexes)}")
    for idx in indexes:
        print(f"  {idx[0]}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "..", DB_PATH)

    print("=== Fase 10: Crear 13 indices ===\n")

    conn = sqlite3.connect(db_path)
    create_indexes(conn)
    conn.close()

    print("\n=== COMPLETADO ===")
