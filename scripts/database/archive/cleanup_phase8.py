"""
Fase 8: Normalizar columna list
- Contactos CON campaigns -> list = concatenar asuntos unicos separados por coma
- Contactos SIN campaigns -> list = NULL
"""

import sqlite3
import os

DB_PATH = os.path.join("data", "inputs", "contacts.db")


def normalize_list(conn):
    """Normalizar list basado en subjects de campaigns."""
    cur = conn.cursor()

    # Primero, poner todos los list en NULL
    cur.execute("UPDATE main SET list = NULL")
    print(f"Todos los list puestos en NULL: {cur.rowcount}")

    # Ahora, para contactos con campaigns, extraer subjects y concatenar
    cur.execute("SELECT ROWID, campaigns FROM main WHERE campaigns IS NOT NULL AND campaigns != ''")
    rows = cur.fetchall()
    print(f"Contactos con campaigns: {len(rows)}")

    updated = 0
    for rowid, campaigns in rows:
        entries = campaigns.split(" || ")
        subjects = set()

        for entry in entries:
            entry = entry.strip()
            if not entry:
                continue

            # Formato: campaign, list, subject, sender, date, response
            # El subject es el 3er campo (index 2)
            parts = entry.split(",")
            if len(parts) >= 3:
                subject = parts[2].strip()
                if subject and subject != "Desconocido" and subject != "":
                    subjects.add(subject)

        if subjects:
            list_value = ", ".join(sorted(subjects))
            cur.execute("UPDATE main SET list = ? WHERE ROWID = ?", (list_value, rowid))
            updated += 1

    conn.commit()
    print(f"List actualizados con subjects: {updated}")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "..", DB_PATH)

    print("=== Fase 8: Normalizar list ===\n")

    conn = sqlite3.connect(db_path)
    normalize_list(conn)
    conn.close()

    # Verificar
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM main WHERE list IS NOT NULL")
    with_list = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM main WHERE list IS NULL")
    without_list = cur.fetchone()[0]
    print(f"\nCon list: {with_list}")
    print(f"Sin list: {without_list}")

    # Muestra
    cur.execute("SELECT primary_email, list FROM main WHERE list IS NOT NULL LIMIT 5")
    print("\nMuestra:")
    for r in cur.fetchall():
        print(f"  {r[0]}: {r[1]}")

    conn.close()
    print("\n=== COMPLETADO ===")
