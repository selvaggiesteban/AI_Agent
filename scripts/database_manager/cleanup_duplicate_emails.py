"""
Limpieza eficiente de emails duplicados y placeholders en contacts.db
"""

import os
import re
import sqlite3

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(PROJECT_ROOT, "data", "inputs", "contacts.db")

PLACEHOLDER_EXACT = [
    "tu@email.com", "usuario@dominio.com", "nombre@ejemplo.com",
    "john@doe.com", "info@yourdomain.com", "info@website.com",
    "hola@miempresa.es", "email@example.com", "ejemplo@mail.com",
    "email@ejemplo.com", "nombre@mail.com", "theratio_interior@mail.com",
    "your@email.com", "test@test.com", "admin@admin.com",
]

IMAGE_FILE_PATTERN = re.compile(r'@2x.*\.(webp|png|jpg|jpeg|gif|svg|bmp)$', re.IGNORECASE)


def cleanup(conn):
    cur = conn.cursor()
    total_deleted = 0

    # 1. Placeholders exactos
    placeholders = tuple(e.lower() for e in PLACEHOLDER_EXACT)
    cur.execute(f"SELECT ROWID FROM lead WHERE LOWER(primary_email) IN ({','.join('?'*len(placeholders))})", placeholders)
    pids = [r[0] for r in cur.fetchall()]
    for rid in pids:
        cur.execute("DELETE FROM contact WHERE ROWID = ?", (rid,))
        cur.execute("DELETE FROM lead WHERE ROWID = ?", (rid,))
        cur.execute("DELETE FROM main WHERE ROWID = ?", (rid,))
    print(f"  Placeholders: {len(pids)} eliminados")
    total_deleted += len(pids)

    # 2. Filenames de imagen
    cur.execute("SELECT ROWID, primary_email FROM lead WHERE primary_email IS NOT NULL")
    all_leads = cur.fetchall()
    img_ids = [rid for rid, email in all_leads if email and IMAGE_FILE_PATTERN.search(email)]
    for rid in img_ids:
        cur.execute("DELETE FROM contact WHERE ROWID = ?", (rid,))
        cur.execute("DELETE FROM lead WHERE ROWID = ?", (rid,))
        cur.execute("DELETE FROM main WHERE ROWID = ?", (rid,))
    print(f"  Filenames imagen: {len(img_ids)} eliminados")
    total_deleted += len(img_ids)
    conn.commit()

    # 3. Emails duplicados - batch approach
    cur.execute("""
        SELECT ROWID, primary_email FROM lead
        WHERE primary_email IS NOT NULL
    """)
    all_rows = cur.fetchall()
    email_to_rowids = {}
    for rid, email in all_rows:
        key = email.strip().lower()
        email_to_rowids.setdefault(key, []).append(rid)

    dup_emails = {k: v for k, v in email_to_rowids.items() if len(v) > 1}
    print(f"  Emails duplicados: {len(dup_emails)} grupos")

    ids_to_delete = []
    for email, rowids in dup_emails.items():
        # Get info for each rowid to decide which to keep
        if len(rowids) > 100:
            # For very large groups, just keep the first ROWID
            ids_to_delete.extend(rowids[1:])
            continue

        placeholders_q = ",".join("?" * len(rowids))
        cur.execute(f"""
            SELECT m.ROWID, m.title, l.website, l.phone
            FROM main m JOIN lead l ON m.ROWID = l.ROWID
            WHERE m.ROWID IN ({placeholders_q})
        """, rowids)
        rows = cur.fetchall()
        scored = [(sum(1 for v in [t, w, p] if v and str(v).strip()), rid) for rid, t, w, p in rows]
        scored.sort(reverse=True)
        ids_to_delete.extend(r[1] for r in scored[1:])

    # Batch delete
    batch_size = 500
    for i in range(0, len(ids_to_delete), batch_size):
        batch = ids_to_delete[i:i+batch_size]
        q = ",".join("?" * len(batch))
        cur.execute(f"DELETE FROM contact WHERE ROWID IN ({q})", batch)
        cur.execute(f"DELETE FROM lead WHERE ROWID IN ({q})", batch)
        cur.execute(f"DELETE FROM main WHERE ROWID IN ({q})", batch)
    print(f"  Duplicados eliminados: {len(ids_to_delete)}")
    total_deleted += len(ids_to_delete)
    conn.commit()

    # 4. Secondary emails duplicadas
    cur.execute("SELECT ROWID, secondary_emails FROM lead WHERE secondary_emails IS NOT NULL")
    cleaned = 0
    for rowid, sec in cur.fetchall():
        if not sec or ";" not in sec:
            continue
        emails = [e.strip().lower() for e in sec.split(";") if e.strip()]
        unique = list(dict.fromkeys(emails))
        if len(unique) != len(emails):
            cur.execute("UPDATE lead SET secondary_emails = ? WHERE ROWID = ?", (";".join(unique), rowid))
            cleaned += 1
    conn.commit()
    print(f"  Secondary emails limpiadas: {cleaned}")

    return total_deleted


def main():
    print("=" * 60)
    print("LIMPIEZA DE EMAILS DUPLICADOS Y PLACEHOLDERS")
    print("=" * 60)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    deleted = cleanup(conn)
    conn.close()

    print(f"\nTotal eliminado: {deleted}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM main")
    remaining = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM lead WHERE primary_email IS NOT NULL")
    with_email = cur.fetchone()[0]
    cur.execute("SELECT COUNT(DISTINCT LOWER(primary_email)) FROM lead WHERE primary_email IS NOT NULL")
    unique_emails = cur.fetchone()[0]
    conn.close()

    print(f"\nContactos restantes: {remaining}")
    print(f"Con email: {with_email}")
    print(f"Emails unicos: {unique_emails}")
    print("=" * 60)


if __name__ == "__main__":
    main()
