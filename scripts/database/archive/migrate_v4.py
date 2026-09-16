"""
Migración de contacts.db a esquema normalizado v4.

Tablas nuevas:
  main (8 cols): id, title, sector, address, city, province, country, entity_type
  lead (21 cols): rowid->main, primary_email, secondary_emails, website, google_maps, phone, + 8 social
  contact (10 cols): rowid->main, sender, deliverability, email_last_response, last_validation_*, last_subject_received, smtp_processed, form_processed, date_added
  campaign (8 cols): rowid, contact_rowid->main, title, list, subject, sender, date, type
  quote, contract, billing, chat: vacías

Pasos:
  1. Backup (ya hecho)
  2. Renombrar main -> main_old
  3. Crear tablas nuevas
  4. Migrar datos
  5. Parsear campaigns blob -> campaign
  6. Eliminar main_old, campaigns_old
  7. Crear índices
  8. Verificar
"""

import sqlite3
import re
import os
import sys
from datetime import datetime

DB_PATH = os.path.join("data", "inputs", "contacts.db")
CAMPAIGN_SEP = " || "


def parse_campaigns(campaigns_str):
    """Parsea el blob de campaigns y retorna lista de dicts."""
    if not campaigns_str:
        return []
    entries = []
    parts = campaigns_str.split(CAMPAIGN_SEP)
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if "Subj:" in part:
            subj_m = re.search(r"Subj:([^|/]+)", part)
            date_m = re.search(r"Date:([^|/]+)", part)
            sender_m = re.search(r"From:([^|/]+)", part) or re.search(r"Sender:([^|/]+)", part)
            type_m = re.search(r"Type:([^|/]+)", part)
            entries.append({
                "type": type_m.group(1).strip() if type_m else "unknown",
                "subject": subj_m.group(1).strip() if subj_m else "",
                "sender": sender_m.group(1).strip() if sender_m else "",
                "date": date_m.group(1).strip() if date_m else "",
            })
        else:
            fields = part.split(",")
            if len(fields) >= 4:
                entries.append({
                    "type": "old",
                    "subject": fields[2].strip() if len(fields) > 2 else "",
                    "sender": fields[3].strip() if len(fields) > 3 else "",
                    "date": fields[4].strip() if len(fields) > 4 else "",
                })
    return entries


def migrate():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "..", DB_PATH)

    print(f"=== Migración contacts.db ===")
    print(f"DB: {db_path}")
    print(f"Hora inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = OFF")
    conn.execute("BEGIN TRANSACTION")

    try:
        # === PASO 1: Verificar tablas viejas (ya renombradas) ===
        print("[1/8] Verificando tablas viejas...")
        old_tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        if "main_old" in old_tables:
            print("  OK: main_old ya existe (renombrado en intento anterior)")
        else:
            conn.execute("ALTER TABLE main RENAME TO main_old")
            try:
                conn.execute("ALTER TABLE campaigns RENAME TO campaigns_old")
            except:
                pass
            conn.commit()
            print("  OK: main -> main_old")

        # === PASO 2: Crear tablas nuevas (si no existen) ===
        print("\n[2/8] Verificando tablas nuevas...")

        existing = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        print(f"  Tablas existentes: {existing}")

        if "main" not in existing:
            conn.execute("""
                CREATE TABLE main (
                    id TEXT, title TEXT, sector TEXT, address TEXT,
                    city TEXT, province TEXT, country TEXT, entity_type TEXT
                )
            """)
            print("  Created: main")
        else:
            print("  main ya existe")

        if "lead" not in existing:
            conn.execute("""
                CREATE TABLE lead (
                    primary_email TEXT, secondary_emails TEXT, website TEXT,
                    google_maps TEXT, phone TEXT, facebook TEXT, instagram TEXT,
                    messenger TEXT, whatsapp TEXT, linkedin TEXT, telegram TEXT,
                    x TEXT, youtube TEXT
                )
            """)
            print("  Created: lead")
        else:
            print("  lead ya existe")

        if "contact" not in existing:
            conn.execute("""
                CREATE TABLE contact (
                    sender TEXT, deliverability TEXT, email_last_response TEXT,
                    last_validation_date TEXT, last_validation_status TEXT,
                    last_subject_received TEXT, smtp_processed TEXT,
                    form_processed TEXT, date_added TEXT
                )
            """)
            print("  Created: contact")
        else:
            print("  contact ya existe")

        if "campaign" not in existing:
            conn.execute("""
                CREATE TABLE campaign (
                    contact_rowid INTEGER, title TEXT, list_val TEXT,
                    subject TEXT, sender TEXT, date TEXT, type TEXT
                )
            """)
            print("  Created: campaign")
        else:
            print("  campaign ya existe")

        if "quote" not in existing:
            conn.execute("""
                CREATE TABLE quote (
                    contact_rowid INTEGER, quote_number TEXT, description TEXT,
                    amount REAL, currency TEXT, status TEXT, date_created TEXT,
                    date_sent TEXT, date_resolved TEXT, notes TEXT
                )
            """)
            print("  Created: quote")
        else:
            print("  quote ya existe")

        if "contract" not in existing:
            conn.execute("""
                CREATE TABLE contract (
                    contact_rowid INTEGER, contract_number TEXT, description TEXT,
                    amount REAL, currency TEXT, status TEXT, date_start TEXT,
                    date_end TEXT, date_signed TEXT, payment_terms TEXT, notes TEXT
                )
            """)
            print("  Created: contract")
        else:
            print("  contract ya existe")

        if "billing" not in existing:
            conn.execute("""
                CREATE TABLE billing (
                    contact_rowid INTEGER, invoice_number TEXT, contract_rowid INTEGER,
                    amount REAL, currency TEXT, status TEXT, date_issued TEXT,
                    date_due TEXT, date_paid TEXT, payment_method TEXT, notes TEXT
                )
            """)
            print("  Created: billing")
        else:
            print("  billing ya existe")

        if "chat" not in existing:
            conn.execute("""
                CREATE TABLE chat (
                    contact_rowid INTEGER, platform TEXT, direction TEXT,
                    message TEXT, timestamp TEXT, status TEXT, agent TEXT
                )
            """)
            print("  Created: chat")
        else:
            print("  chat ya existe")

        conn.commit()

        # === PASO 3: Migrar datos ===
        print("\n[3/8] Migrando datos de main_old -> main + lead + contact...")

        main_count = conn.execute("SELECT COUNT(*) FROM main").fetchone()[0]
        if main_count > 0:
            print(f"  main ya tiene {main_count:,} filas, saltando insercion")
        else:
            conn.execute("""
                INSERT INTO main (id, title, sector, address, city, province, country, entity_type)
                SELECT NULL, title, sector, address, city, province, country, entity_type
                FROM main_old
            """)
            main_count = conn.execute("SELECT COUNT(*) FROM main").fetchone()[0]
            print(f"  OK: main -> {main_count:,} filas")

        lead_count = conn.execute("SELECT COUNT(*) FROM lead").fetchone()[0]
        if lead_count > 0:
            print(f"  lead ya tiene {lead_count:,} filas, saltando insercion")
        else:
            conn.execute("""
                INSERT INTO lead (primary_email, secondary_emails, website, google_maps, phone)
                SELECT primary_email, secondary_emails, website, google_maps, phone
                FROM main_old
            """)
            lead_count = conn.execute("SELECT COUNT(*) FROM lead").fetchone()[0]
            print(f"  OK: lead -> {lead_count:,} filas")

        contact_count = conn.execute("SELECT COUNT(*) FROM contact").fetchone()[0]
        if contact_count > 0:
            print(f"  contact ya tiene {contact_count:,} filas, saltando insercion")
        else:
            conn.execute("""
                INSERT INTO contact (sender, deliverability, email_last_response, last_validation_date,
                                     last_validation_status, last_subject_received, smtp_processed,
                                     form_processed, date_added)
                SELECT sender, deliverability, email_last_response, last_validation_date,
                       last_validation_status, last_subject_received, smtp_processed,
                       form_processed, date_added
                FROM main_old
            """)
            contact_count = conn.execute("SELECT COUNT(*) FROM contact").fetchone()[0]
            print(f"  OK: contact -> {contact_count:,} filas")

        conn.commit()

        # === PASO 4: Parsear campaigns blob -> campaign ===
        print("\n[4/8] Parseando campaigns blob -> campaign...")

        campaign_count = conn.execute("SELECT COUNT(*) FROM campaign").fetchone()[0]
        if campaign_count > 0:
            print(f"  campaign ya tiene {campaign_count:,} filas, saltando")
        else:
            campaigns_rows = conn.execute(
                "SELECT ROWID, campaigns, list FROM main_old WHERE campaigns IS NOT NULL AND campaigns != ''"
            ).fetchall()

            campaign_inserts = []
            for rowid, campaigns_str, list_val in campaigns_rows:
                entries = parse_campaigns(campaigns_str)
                for e in entries:
                    campaign_inserts.append((
                        rowid,  # contact_rowid
                        "",  # title (no disponible en blob)
                        list_val or "",  # list_val
                        e["subject"],
                        e["sender"],
                        e["date"],
                        e["type"],
                    ))

            conn.executemany("""
                INSERT INTO campaign (contact_rowid, title, list_val, subject, sender, date, type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, campaign_inserts)

            campaign_count = conn.execute("SELECT COUNT(*) FROM campaign").fetchone()[0]
            print(f"  OK: campaign -> {campaign_count:,} filas (de {len(campaigns_rows):,} contactos)")

            # Migrar list restante (contactos con list pero sin campaigns)
            conn.execute("""
                INSERT INTO campaign (contact_rowid, title, list_val, subject, sender, date, type)
                SELECT ROWID, '', list, '', '', '', 'list_only'
                FROM main_old
                WHERE list IS NOT NULL AND list != ''
                AND ROWID NOT IN (SELECT DISTINCT contact_rowid FROM campaign WHERE list_val != '')
            """)
            final_campaign_count = conn.execute("SELECT COUNT(*) FROM campaign").fetchone()[0]
            print(f"  OK: campaign total -> {final_campaign_count:,} filas")

        conn.commit()

        # === PASO 5: Eliminar tablas viejas ===
        print("\n[5/8] Eliminando tablas viejas...")
        conn.execute("DROP TABLE main_old")
        try:
            conn.execute("DROP TABLE campaigns_old")
        except:
            pass
        conn.commit()
        print("  OK: main_old, campaigns_old eliminadas")

        # === PASO 6: Crear índices ===
        print("\n[6/8] Creando índices...")

        indexes = [
            ("idx_main_sector", "main", "sector"),
            ("idx_main_city", "main", "city"),
            ("idx_main_country", "main", "country"),
            ("idx_lead_email", "lead", "primary_email"),
            ("idx_lead_phone", "lead", "phone"),
            ("idx_contact_sender", "contact", "sender"),
            ("idx_contact_deliverability", "contact", "deliverability"),
            ("idx_contact_smtp", "contact", "smtp_processed"),
            ("idx_camp_contact", "campaign", "contact_rowid"),
            ("idx_camp_subject", "campaign", "subject"),
            ("idx_camp_sender", "campaign", "sender"),
            ("idx_camp_date", "campaign", "date"),
            ("idx_camp_type", "campaign", "type"),
            ("idx_camp_title", "campaign", "title"),
        ]

        for idx_name, tbl, col in indexes:
            conn.execute(f"CREATE INDEX {idx_name} ON {tbl} ({col})")
        conn.commit()
        print(f"  OK: {len(indexes)} índices creados")

        # === PASO 7: Verificación ===
        print("\n[7/8] Verificando integridad...")

        tables = ["main", "lead", "contact", "campaign", "quote", "contract", "billing", "chat"]
        for tbl in tables:
            count = conn.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
            print(f"  {tbl}: {count:,} filas")

        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        print(f"\n  integrity_check: {integrity}")

        # Verificar FKs (campaign.contact_rowid -> main.ROWID)
        orphans = conn.execute("""
            SELECT COUNT(*) FROM campaign c
            LEFT JOIN main m ON c.contact_rowid = m.ROWID
            WHERE m.ROWID IS NULL
        """).fetchone()[0]
        print(f"  campaign FKs huérfanas: {orphans}")

        # Verificar que main y lead tienen misma cantidad
        main_vs_lead = conn.execute("SELECT COUNT(*) FROM main").fetchone()[0] == conn.execute("SELECT COUNT(*) FROM lead").fetchone()[0]
        print(f"  main == lead (1:1): {main_vs_lead}")

        # Verificar tipos de campaign
        types = conn.execute("SELECT type, COUNT(*) FROM campaign GROUP BY type ORDER BY COUNT(*) DESC").fetchall()
        print(f"\n  Tipos de campaña:")
        for t, c in types:
            print(f"    {t}: {c:,}")

        # === PASO 8: Stats finales ===
        print("\n[8/8] Estadísticas finales...")

        # Tamaño de DB
        db_size = os.path.getsize(db_path)
        print(f"  Tamaño DB: {db_size / (1024*1024):.2f} MB")

        # Columnas por tabla
        for tbl in tables:
            cols = conn.execute(f"PRAGMA table_info({tbl})").fetchall()
            print(f"  {tbl}: {len(cols)} columnas")

        # Índices
        idx_count = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND sql IS NOT NULL").fetchone()[0]
        print(f"  Total índices: {idx_count}")

        conn.close()

        print(f"\n=== MIGRACIÓN COMPLETADA ===")
        print(f"Hora fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return True

    except Exception as e:
        print(f"\n*** ERROR: {e}")
        print("Ejecutando ROLLBACK...")
        conn.rollback()
        conn.close()
        raise


if __name__ == "__main__":
    migrate()
