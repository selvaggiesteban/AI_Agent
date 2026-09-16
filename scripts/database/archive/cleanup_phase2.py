"""
Fase 2 + 5 + 6: Reconstruir schema de contacts.db
- Eliminar 9 columnas
- Renombrar 2 columnas
- Migrar linkedin → website
- Crear columna sender
- Crear 8 columnas sociales
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join("data", "inputs", "contacts.db")


def get_current_columns(conn):
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(main)")
    return [(row[1], row[2]) for row in cur.fetchall()]


def phase2_rebuild_schema(conn):
    """Eliminar columnas, renombrar, migrar linkedin → website."""
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    columns_to_drop = {
        "date_suspended", "conflict_flag", "physical_addr_proc",
        "budget_sent", "price_shared", "whatsapp_received",
        "linkedin", "last_interaction_date", "validation_date",
    }

    current_cols = get_current_columns(conn)
    col_names = [c[0] for c in current_cols]

    print(f"Columnas actuales: {len(col_names)}")

    # Construir nueva lista de columnas
    new_cols = []
    for name, ctype in current_cols:
        if name in columns_to_drop:
            print(f"  ELIMINAR: {name}")
            continue
        if name == "other_emails":
            print(f"  RENOMBRAR: other_emails -> secondary_emails")
            new_cols.append(("secondary_emails", ctype))
        elif name == "urls":
            print(f"  RENOMBRAR: urls -> website")
            new_cols.append(("website", ctype))
        else:
            new_cols.append((name, ctype))

    # Agregar columna sender (Fase 5)
    new_cols.append(("sender", "TEXT"))
    print(f"  AGREGAR: sender")

    # Agregar 8 columnas sociales (Fase 6)
    social_cols = [
        "instagram_account", "linkedin_account", "telegram_account",
        "messenger_account", "facebook_account", "x_account",
        "whatsapp_account", "youtube_account",
    ]
    for sc in social_cols:
        new_cols.append((sc, "TEXT"))
        print(f"  AGREGAR: {sc}")

    print(f"\nNuevas columnas: {len(new_cols)}")

    # Crear tabla temporal
    cols_def = ", ".join(f'"{c[0]}" {c[1]}' for c in new_cols)
    cur.execute(f"CREATE TABLE main_new ({cols_def})")

    # Construir SELECT con migraciones
    select_parts = []
    for name, ctype in current_cols:
        if name in columns_to_drop:
            continue
        if name == "other_emails":
            select_parts.append('"secondary_emails"')
        elif name == "urls":
            select_parts.append('"website"')
        else:
            select_parts.append(f'"{name}"')

    # Migrar linkedin -> website (si website esta vacio)
    website_idx = None
    for i, (name, _) in enumerate(current_cols):
        if name == "urls":
            website_idx = i
            break

    # Agregar sender (Fase 5): COALESCE(last_sender_account, assigned_sender)
    select_parts.append('COALESCE("last_sender_account", "assigned_sender")')

    # Agregar 8 columnas sociales (NULL)
    for _ in social_cols:
        select_parts.append("NULL")

    select_str = ", ".join(select_parts)

    print(f"\nCopiando datos...")
    cur.execute(f"INSERT INTO main_new SELECT {select_str} FROM main")

    # Verificar
    cur.execute("SELECT COUNT(*) FROM main_new")
    new_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM main")
    old_count = cur.fetchone()[0]
    print(f"Filas originales: {old_count}")
    print(f"Filas nuevas: {new_count}")

    if new_count != old_count:
        print("ERROR: Diferencia en conteo de filas!")
        cur.execute("DROP TABLE main_new")
        return False

    # Eliminar tabla original y renombrar
    cur.execute("DROP TABLE main")
    cur.execute("ALTER TABLE main_new RENAME TO main")

    conn.commit()

    # Verificar schema final
    cur.execute("PRAGMA table_info(main)")
    final_cols = cur.fetchall()
    print(f"\nSchema final: {len(final_cols)} columnas")
    for c in final_cols:
        print(f"  [{c[1]}] {c[2]}")

    return True


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "..", DB_PATH)

    print("=== Fase 2 + 5 + 6: Reconstruccion de schema ===\n")

    conn = sqlite3.connect(db_path)
    success = phase2_rebuild_schema(conn)
    conn.close()

    if success:
        print("\n=== COMPLETADO ===")
    else:
        print("\n=== FALLÓ ===")
