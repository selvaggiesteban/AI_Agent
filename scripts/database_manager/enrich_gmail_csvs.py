"""
Enriquece contacts.db con datos de Gmail CSVs (csv1-csv5).

Campos actualizados en main:
- campaigns: append de toda actividad Gmail (sent, received, pending, campaign, bounce)
- last_interaction_date: fecha más reciente de email enviado/recibido
- email_last_response: 'pending_reply' si tiene borrador IA
- deliverability: 'invalid' para bounces
- last_subject_received: asunto del último email recibido
- last_sender_account: última cuenta involucrada

Formato en campaigns:
  Type:sent|From:cuenta|To:dest|Subj:asunto|Date:fecha|Snip:preview
  Type:received|From:remitente|To:cuenta|Name:nombre|Subj:asunto|Date:fecha|Snip:preview
  Type:pending|From:remitente|Subj:asunto|Date:fecha|Snip:preview|Draft:borrador
  Type:campaign|Name:campaña|Subj:asunto|Count:n|Date:fecha|Preview:msg|Lista:emails
  Type:bounce|To:email|Reason:razon|Detail:detalle|Code:codigo|Date:fecha|Frag:fragmento
"""

import sqlite3
import csv
import os
import re
from datetime import datetime

DB_PATH = os.path.join("data", "inputs", "contacts.db")
CSV_DIR = os.path.join("data", "outputs", "gmail_csv")

JUNK_PATTERNS = [
    "sentry", "wixpress", "example", "test", "demo",
    "@2x.png", ".js", "username@domain", "your@mail",
    "juan.perez", "beispiel", "ejemplo", "mysite",
]

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

SEPARATOR = " || "


def is_valid_email(email):
    if not email or not EMAIL_RE.match(email):
        return False
    email_lower = email.lower()
    return not any(p in email_lower for p in JUNK_PATTERNS)


def decode_subject(subj):
    if not subj:
        return ""
    if subj.startswith("=?utf-8?q?") or subj.startswith("=?UTF-8?Q?"):
        decoded = subj.replace("=?utf-8?q?", "").replace("=?UTF-8?Q?", "").rstrip("?=")
        decoded = decoded.replace("_", " ")
        import quopri
        try:
            decoded = quopri.decodestring(decoded.encode()).decode("utf-8", errors="ignore")
        except Exception:
            pass
        return decoded
    return subj


def safe_field(val, max_len=None):
    if not val:
        return ""
    val = str(val).replace("|", "/").replace("\n", " ").replace("\r", "")
    if max_len and len(val) > max_len:
        val = val[:max_len] + "..."
    return val


def parse_date_to_iso(date_str):
    if not date_str:
        return None
    date_str = date_str.strip()
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %z (%Z)",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    return date_str


def get_csv_path(csv_dir, filename):
    for f in os.listdir(csv_dir):
        if f.startswith(filename):
            return os.path.join(csv_dir, f)
    return None


def load_csv1(csv_dir):
    """csv1_destinatarios: emails ENVIADOS por tus cuentas."""
    path = get_csv_path(csv_dir, "csv1_destinatarios")
    if not path:
        print("[WARN] csv1_destinatarios no encontrado")
        return {}

    entries = {}
    with open(path, encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames
        for row in reader:
            dest = (row.get(cols[1]) or "").strip().lower()
            if not is_valid_email(dest):
                continue

            cuenta = safe_field(row.get(cols[0]))
            asunto = safe_field(decode_subject(row.get(cols[2])), 200)
            fecha = parse_date_to_iso(row.get(cols[3]))
            snippet = safe_field(row.get(cols[4]), 300)

            entry = f"Type:sent|From:{cuenta}|To:{dest}|Subj:{asunto}|Date:{fecha}|Snip:{snippet}"

            if dest not in entries:
                entries[dest] = []
            entries[dest].append(entry)

    print(f"[INFO] CSV1: {len(entries)} destinatarios con emails enviados")
    return entries


def load_csv2(csv_dir):
    """csv2_remitentes: emails RECIBIDOS en tus cuentas."""
    path = get_csv_path(csv_dir, "csv2_remitentes")
    if not path:
        print("[WARN] csv2_remitentes no encontrado")
        return {}

    entries = {}
    with open(path, encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames
        for row in reader:
            remitente = (row.get(cols[1]) or "").strip().lower()
            if not is_valid_email(remitente):
                continue

            cuenta = safe_field(row.get(cols[0]))
            nombre = safe_field(row.get(cols[2]))
            asunto = safe_field(decode_subject(row.get(cols[3])), 200)
            fecha = parse_date_to_iso(row.get(cols[4]))

            entry = f"Type:received|From:{remitente}|To:{cuenta}|Name:{nombre}|Subj:{asunto}|Date:{fecha}"

            if remitente not in entries:
                entries[remitente] = []
            entries[remitente].append(entry)

    print(f"[INFO] CSV2: {len(entries)} remitentes con emails recibidos")
    return entries


def load_csv3(csv_dir):
    """csv3_pendientes_respuesta: emails sin respuesta + borrador IA."""
    path = get_csv_path(csv_dir, "csv3_pendientes_respuesta")
    if not path:
        print("[WARN] csv3_pendientes_respuesta no encontrado")
        return {}

    entries = {}
    with open(path, encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames
        for row in reader:
            remitente = (row.get(cols[1]) or "").strip().lower()
            if not is_valid_email(remitente):
                continue

            asunto = safe_field(decode_subject(row.get(cols[2])), 200)
            fecha = parse_date_to_iso(row.get(cols[3]))
            snippet = safe_field(row.get(cols[4]), 300)
            draft = safe_field(row.get(cols[5]), 500)

            entry = f"Type:pending|From:{remitente}|Subj:{asunto}|Date:{fecha}|Snip:{snippet}|Draft:{draft}"

            if remitente not in entries:
                entries[remitente] = []
            entries[remitente].append(entry)

    print(f"[INFO] CSV3: {len(entries)} pendientes de respuesta")
    return entries


def load_csv4(csv_dir):
    """csv4_campanas_email_marketing: campañas de email marketing."""
    path = get_csv_path(csv_dir, "csv4_campanas_email_marketing")
    if not path:
        print("[WARN] csv4_campanas_email_marketing no encontrado")
        return {}

    entries = {}
    with open(path, encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames
        for row in reader:
            lista = (row.get(cols[4]) or "").strip()
            if not lista:
                continue

            campana = safe_field(row.get(cols[1]))
            asunto = safe_field(decode_subject(row.get(cols[2])), 200)
            count = safe_field(row.get(cols[3]))
            preview = safe_field(row.get(cols[5]), 300)
            fecha = parse_date_to_iso(row.get(cols[6]))

            entry = f"Type:campaign|Name:{campana}|Subj:{asunto}|Count:{count}|Date:{fecha}|Preview:{preview}|Lista:{safe_field(lista, 500)}"

            emails = [e.strip().lower() for e in lista.split(",") if e.strip()]
            for email in emails:
                if not is_valid_email(email):
                    continue
                if email not in entries:
                    entries[email] = []
                entries[email].append(entry)

    print(f"[INFO] CSV4: {len(entries)} contactos en campañas")
    return entries


def load_csv5(csv_dir):
    """csv5_delivery_status: bounces / emails fallidos."""
    path = get_csv_path(csv_dir, "csv5_delivery_status")
    if not path:
        print("[WARN] csv5_delivery_status no encontrado")
        return {}

    entries = {}
    with open(path, encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        cols = reader.fieldnames
        for row in reader:
            fallido = (row.get(cols[1]) or "").strip().lower()
            if not is_valid_email(fallido):
                continue

            razon = safe_field(row.get(cols[2]))
            detalle = safe_field(row.get(cols[3]), 300)
            codigo = safe_field(row.get(cols[4]))
            asunto = safe_field(decode_subject(row.get(cols[5])), 200)
            fecha = parse_date_to_iso(row.get(cols[6]))
            fragmento = safe_field(row.get(cols[7]), 300)

            entry = f"Type:bounce|To:{fallido}|Reason:{razon}|Detail:{detalle}|Code:{codigo}|Date:{fecha}|Frag:{fragmento}"

            if fallido not in entries:
                entries[fallido] = []
            entries[fallido].append(entry)

    print(f"[INFO] CSV5: {len(entries)} emails con bounce")
    return entries


def enrich(db_path, csv1, csv2, csv3, csv4, csv5):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT ROWID, primary_email, campaigns, last_interaction_date, email_last_response, deliverability, last_subject_received, last_sender_account FROM main")
    db_rows = {}
    for row in cur.fetchall():
        if row[1]:
            db_rows[row[1].lower().strip()] = {
                "rowid": row[0],
                "campaigns": row[2] or "",
                "last_interaction_date": row[3] or "",
                "email_last_response": row[4] or "",
                "deliverability": row[5] or "",
                "last_subject_received": row[6] or "",
                "last_sender_account": row[7] or "",
            }

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    updated = 0
    inserted = 0

    all_emails = set(list(csv1.keys()) + list(csv2.keys()) + list(csv3.keys()) + list(csv4.keys()) + list(csv5.keys()))

    for email in all_emails:
        if email in db_rows:
            row = db_rows[email]
            rowid = row["rowid"]

            new_entries = []
            new_dates = []
            new_subjects = []
            new_senders = []
            bounce_found = False
            pending_found = False

            if email in csv1:
                new_entries.extend(csv1[email])
                for e in csv1[email]:
                    m = re.search(r"Date:([^|]*)", e)
                    if m:
                        new_dates.append(m.group(1).strip())
                    m = re.search(r"From:([^|]*)", e)
                    if m:
                        new_senders.append(m.group(1).strip())

            if email in csv2:
                new_entries.extend(csv2[email])
                for e in csv2[email]:
                    m = re.search(r"Date:([^|]*)", e)
                    if m:
                        new_dates.append(m.group(1).strip())
                    m = re.search(r"Subj:([^|]*)", e)
                    if m:
                        new_subjects.append(m.group(1).strip())
                    m = re.search(r"To:([^|]*)", e)
                    if m:
                        new_senders.append(m.group(1).strip())

            if email in csv3:
                new_entries.extend(csv3[email])
                pending_found = True
                for e in csv3[email]:
                    m = re.search(r"Date:([^|]*)", e)
                    if m:
                        new_dates.append(m.group(1).strip())

            if email in csv4:
                new_entries.extend(csv4[email])

            if email in csv5:
                new_entries.extend(csv5[email])
                bounce_found = True

            existing_campaigns = row["campaigns"]
            if new_entries:
                new_str = SEPARATOR.join(new_entries)
                if existing_campaigns:
                    campaigns_final = existing_campaigns + SEPARATOR + new_str
                else:
                    campaigns_final = new_str
            else:
                campaigns_final = existing_campaigns

            valid_dates = [d for d in new_dates if d and d != "None"]
            last_date = row["last_interaction_date"]
            if valid_dates:
                max_date = max(valid_dates)
                if not last_date or max_date > last_date:
                    last_date = max_date

            last_subject = row["last_subject_received"]
            if new_subjects:
                last_subject = new_subjects[-1]

            last_sender = row["last_sender_account"]
            if new_senders:
                last_sender = new_senders[-1]

            email_response = row["email_last_response"]
            if pending_found and not email_response:
                email_response = "pending_reply"

            deliverability = row["deliverability"]
            if bounce_found and deliverability != "invalid":
                deliverability = "invalid"

            cur.execute(
                """UPDATE main SET
                    campaigns = ?,
                    last_interaction_date = ?,
                    email_last_response = ?,
                    deliverability = ?,
                    last_subject_received = ?,
                    last_sender_account = ?,
                    date_updated = ?
                WHERE ROWID = ?""",
                (campaigns_final, last_date, email_response, deliverability, last_subject, last_sender, now, rowid),
            )
            updated += 1
        else:
            entries = []
            dates = []
            subjects = []
            senders = []
            bounce_found = False
            pending_found = False

            if email in csv1:
                entries.extend(csv1[email])
                for e in csv1[email]:
                    m = re.search(r"Date:([^|]*)", e)
                    if m:
                        dates.append(m.group(1).strip())
                    m = re.search(r"From:([^|]*)", e)
                    if m:
                        senders.append(m.group(1).strip())

            if email in csv2:
                entries.extend(csv2[email])
                for e in csv2[email]:
                    m = re.search(r"Date:([^|]*)", e)
                    if m:
                        dates.append(m.group(1).strip())
                    m = re.search(r"Subj:([^|]*)", e)
                    if m:
                        subjects.append(m.group(1).strip())
                    m = re.search(r"To:([^|]*)", e)
                    if m:
                        senders.append(m.group(1).strip())

            if email in csv3:
                entries.extend(csv3[email])
                pending_found = True
                for e in csv3[email]:
                    m = re.search(r"Date:([^|]*)", e)
                    if m:
                        dates.append(m.group(1).strip())

            if email in csv4:
                entries.extend(csv4[email])

            if email in csv5:
                entries.extend(csv5[email])
                bounce_found = True

            campaigns_str = SEPARATOR.join(entries) if entries else None
            valid_dates = [d for d in dates if d and d != "None"]
            last_date = max(valid_dates) if valid_dates else None
            last_subject = subjects[-1] if subjects else None
            last_sender = senders[-1] if senders else None
            email_response = "pending_reply" if pending_found else None
            deliverability = "invalid" if bounce_found else None

            cur.execute(
                """INSERT INTO main (primary_email, campaigns, last_interaction_date, email_last_response, deliverability, last_subject_received, last_sender_account, date_added, date_updated)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (email, campaigns_str, last_date, email_response, deliverability, last_subject, last_sender, now, now),
            )
            inserted += 1

    conn.commit()

    cur.execute("SELECT COUNT(*) FROM main")
    total = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM main WHERE campaigns IS NOT NULL AND campaigns != ""')
    with_campaigns = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM main WHERE last_interaction_date IS NOT NULL AND last_interaction_date != ""')
    with_date = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM main WHERE email_last_response IS NOT NULL AND email_last_response != ""')
    with_response = cur.fetchone()[0]
    cur.execute('SELECT COUNT(*) FROM main WHERE deliverability = "invalid"')
    with_invalid = cur.fetchone()[0]

    print(f"\n--- VERIFICACION ---")
    print(f"Total contactos: {total}")
    print(f"Con campaigns: {with_campaigns}")
    print(f"Con last_interaction_date: {with_date}")
    print(f"Con email_last_response: {with_response}")
    print(f"Con deliverability=invalid: {with_invalid}")
    print(f"\n--- RESULTADO ---")
    print(f"Actualizados: {updated}")
    print(f"Nuevos insertados: {inserted}")

    conn.close()
    return updated, inserted


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "..", "..", DB_PATH)
    csv_dir = os.path.join(script_dir, "..", "..", CSV_DIR)

    print("=== Enriquecimiento Gmail CSVs ===\n")

    print("--- Cargando CSVs ---")
    csv1 = load_csv1(csv_dir)
    csv2 = load_csv2(csv_dir)
    csv3 = load_csv3(csv_dir)
    csv4 = load_csv4(csv_dir)
    csv5 = load_csv5(csv_dir)

    print("\n--- Enriqueciendo DB ---")
    updated, inserted = enrich(db_path, csv1, csv2, csv3, csv4, csv5)

    print(f"\n=== COMPLETADO: {updated} actualizados, {inserted} nuevos insertados ===")
