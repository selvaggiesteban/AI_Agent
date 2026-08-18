"""
Fase 11: Verificacion final
"""

import sqlite3
import os

DB_PATH = os.path.join("data", "inputs", "contacts.db")


def verify(conn):
    """Verificacion completa de la DB."""
    cur = conn.cursor()

    # 1. Integrity check
    cur.execute("PRAGMA integrity_check")
    integrity = cur.fetchone()[0]
    print(f"Integrity: {integrity}")

    # 2. Row count
    cur.execute("SELECT COUNT(*) FROM main")
    rows = cur.fetchone()[0]
    print(f"\nTotal rows: {rows}")

    # 3. Column count
    cur.execute("PRAGMA table_info(main)")
    columns = cur.fetchall()
    print(f"Columns: {len(columns)}")

    # 4. Null stats per column
    print("\nNull counts:")
    for col in columns:
        col_name = col[1]
        cur.execute(f"SELECT COUNT(*) FROM main WHERE {col_name} IS NULL OR {col_name} = ''")
        nulls = cur.fetchone()[0]
        if nulls > 0:
            print(f"  {col_name}: {nulls}")

    # 5. Country distribution
    print("\nCountry distribution:")
    cur.execute("SELECT country, COUNT(*) as cnt FROM main WHERE country IS NOT NULL GROUP BY country ORDER BY cnt DESC LIMIT 10")
    for r in cur.fetchall():
        print(f"  {r[0]}: {r[1]}")

    # 6. Entity type distribution
    print("\nEntity type distribution:")
    cur.execute("SELECT entity_type, COUNT(*) as cnt FROM main WHERE entity_type IS NOT NULL GROUP BY entity_type ORDER BY cnt DESC")
    for r in cur.fetchall():
        print(f"  {r[0]}: {r[1]}")

    # 7. Deliverability distribution
    print("\nDeliverability distribution:")
    cur.execute("SELECT deliverability, COUNT(*) as cnt FROM main WHERE deliverability IS NOT NULL GROUP BY deliverability ORDER BY cnt DESC")
    for r in cur.fetchall():
        print(f"  {r[0]}: {r[1]}")

    # 8. Sender distribution
    print("\nSender distribution:")
    cur.execute("SELECT sender, COUNT(*) as cnt FROM main WHERE sender IS NOT NULL GROUP BY sender ORDER BY cnt DESC")
    for r in cur.fetchall():
        print(f"  {r[0]}: {r[1]}")

    # 9. Tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cur.fetchall()
    print(f"\nTables: {len(tables)}")
    for t in tables:
        print(f"  {t[0]}")

    # 10. Indexes
    cur.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%' ORDER BY name")
    indexes = cur.fetchall()
    print(f"\nIndexes: {len(indexes)}")

    # 11. Campaigns stats
    cur.execute("SELECT COUNT(*) FROM main WHERE campaigns IS NOT NULL AND campaigns != ''")
    with_campaigns = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM main WHERE list IS NOT NULL")
    with_list = cur.fetchone()[0]
    print(f"\nWith campaigns: {with_campaigns}")
    print(f"With list: {with_list}")

    # 12. Sample row
    print("\nSample row:")
    cur.execute("SELECT * FROM main LIMIT 1")
    row = cur.fetchone()
    for i, val in enumerate(row):
        if val:
            print(f"  {columns[i][1]}: {str(val)[:80]}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "..", DB_PATH)

    print("=== Fase 11: Verificacion final ===\n")

    conn = sqlite3.connect(db_path)
    verify(conn)
    conn.close()

    print("\n=== COMPLETADO ===")
