"""
Generador unificado de 5 CSVs desde Gmail.
IMAP robusto: socket timeout, batch 50, reconnect 500, retry+continue.
NO usa SentCollector ni BounceAnalyzer — IMAP directo con protección.
"""
import os
import sys
import csv
import re
import socket
import imaplib
import email
import sqlite3
import json
import time
from pathlib import Path
from email.header import decode_header
from datetime import datetime
from dotenv import load_dotenv

# Timeout global IMAP — evita cuelgues indefinidos
socket.setdefaulttimeout(30)

# Fix Unicode en Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ── Paths ──
from core.paths import PROJECT_ROOT, INPUTS_DIR, OUTPUTS_DIR, LOGS_DIR
load_dotenv(PROJECT_ROOT / ".env")

# Fixed GMAIL_CSV_OUTPUT to match core.paths logic if possible,
# but the script uses a specific subfolder for gmail_csv
GMAIL_CSV_OUTPUT = OUTPUTS_DIR / "gmail_csv"
GMAIL_CSV_OUTPUT.mkdir(parents=True, exist_ok=True)

DB_PATH = INPUTS_DIR / "contacts.db"
CAMPAIGN_DB = LOGS_DIR / "campaigns" / "marketing_memory.db"

# ── Credenciales desde accounts_config.py ──
from accounts_config import ACCOUNTS as CONFIG_ACCOUNTS

# ACCOUNTS = [(email, app_password)] para IMAP
ACCOUNTS = [(acc["email"], acc["app_password"].replace(" ", "")) for acc in CONFIG_ACCOUNTS]

# ── Helpers ──
def clean_header(header_val):
    if not header_val: return ""
    try:
        decoded = decode_header(header_val)
        parts = []
        for content, charset in decoded:
            if isinstance(content, bytes):
                parts.append(content.decode(charset or 'utf-8', errors='ignore'))
            else: parts.append(str(content))
        return "".join(parts)
    except: return str(header_val)

def get_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload: body = payload.decode(errors='ignore')
                break
    else:
        payload = msg.get_payload(decode=True)
        if payload: body = payload.decode(errors='ignore')
    return body

def imap_connect(email_addr, password):
    """Conexión IMAP con timeout."""
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(email_addr, password)
    return mail

def fetch_with_retry(mail, chunk_str, email_addr, password, folder, label=""):
    """FETCH con retry + reconnect + backoff. Devuelve (data, mail). Si falla retry, devuelve (None, mail)."""
    try:
        status, data = mail.fetch(chunk_str, "(RFC822)")
        return data, mail
    except Exception as e1:
        err_str = str(e1).lower()
        is_quota = "overquota" in err_str or "bandwidth" in err_str or "exceeded command" in err_str
        wait = 15 if is_quota else 2
        print(f"    [!] {label}FETCH error, esperando {wait}s: {e1}", flush=True)
        time.sleep(wait)
        try: mail.logout()
        except: pass
        try:
            mail = imap_connect(email_addr, password)
            mail.select(folder, readonly=True)
            if is_quota:
                time.sleep(5)  # extra pause before retry after quota error
            status, data = mail.fetch(chunk_str, "(RFC822)")
            return data, mail
        except Exception as e2:
            print(f"    [!] {label}Retry falló: {e2}", flush=True)
            if "overquota" in str(e2).lower() or "bandwidth" in str(e2).lower():
                print(f"    [!] {label}OVERQUOTA persistente, esperando 60s...", flush=True)
                time.sleep(60)
            return None, mail

AUTO_REPLY_PATTERNS = [
    "auto-reply", "auto_reply", "autoresponder", "out of office", "fuera de la oficina",
    "vacation", "ausente", "no estaré", "no estaré disponible", "away from",
    "automatic reply", "respuesta automática", "mailer-daemon", "noreply", "no-reply",
    "postmaster", "daemon", "bounce", "undeliver", "failed", "delivery status"
]

def is_auto_reply(msg):
    """Filtra auto-replies, bounces, notificaciones."""
    from_addr = clean_header(msg.get('From') or '').lower()
    subject = clean_header(msg.get('Subject') or '').lower()
    reply_to = clean_header(msg.get('Reply-To') or '').lower()
    auto_submitted = clean_header(msg.get('Auto-Submitted') or '').lower()

    if auto_submitted and auto_submitted != 'no':
        return True

    combined = f"{from_addr} {subject} {reply_to}"
    for p in AUTO_REPLY_PATTERNS:
        if p in combined:
            return True
    return False

# ═══════════════════════════════════════════
# CSV 1: Todos los destinatarios (Enviados) — IMAP directo
# ═══════════════════════════════════════════
def csv1_destinatarios():
    print("\n[CSV 1] Extrayendo TODOS los destinatarios de enviados...", flush=True)
    all_records = []

    for email_addr, password in ACCOUNTS:
        try:
            mail = imap_connect(email_addr, password)
            # Encontrar carpeta Sent
            status, folders = mail.list()
            sent_folder = '"[Gmail]/Sent Mail"'
            for f in folders:
                f_str = f.decode()
                if '\\Sent' in f_str:
                    sent_folder = f_str.split(' "/" ')[-1]
                    break

            mail.select(sent_folder, readonly=True)
            status, messages = mail.search(None, "ALL")
            msg_ids = messages[0].split()
            print(f"    [*] {email_addr}: {len(msg_ids)} mensajes enviados", flush=True)

            for i in range(0, len(msg_ids), 50):
                # Progreso
                if i > 0 and i % 250 == 0:
                    print(f"    [.] CSV1 progreso: {i}/{len(msg_ids)} | {len(all_records)} registros", flush=True)
                # Reconectar cada 500
                if i > 0 and i % 500 == 0:
                    try: mail.logout()
                    except: pass
                    mail = imap_connect(email_addr, password)
                    mail.select(sent_folder, readonly=True)

                chunk = msg_ids[i:i+50]
                chunk_str = ",".join(m.decode() for m in chunk)
                data, mail = fetch_with_retry(mail, chunk_str, email_addr, password, sent_folder, "CSV1 ")
                if data is None:
                    continue
                time.sleep(0.2)  # rate-limit entre batches

                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = clean_header(msg.get('Subject', '(Sin Asunto)'))
                        to_raw = clean_header(msg.get('To', '(Desconocido)'))
                        body = get_body(msg)
                        date = str(msg.get('Date'))

                        # Separar múltiples destinatarios
                        dests = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', to_raw.lower())
                        if not dests:
                            dests = [to_raw.lower().strip('<>., ')]

                        for d in dests:
                            all_records.append({
                                "Cuenta_Remitente": email_addr,
                                "Destinatario": d.strip(),
                                "Asunto": subject,
                                "Fecha": date,
                                "Snippet": " ".join(body.split())[:200]
                            })

            try: mail.logout()
            except: pass
            print(f"    [+] {email_addr}: completado", flush=True)
        except Exception as e:
            print(f"    [-] Error en {email_addr}: {e}", flush=True)

    output = GMAIL_CSV_OUTPUT / "csv1_destinatarios.csv"
    headers = ["Cuenta_Remitente", "Destinatario", "Asunto", "Fecha", "Snippet"]
    with open(output, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(all_records)

    unique_dests = len(set(r["Destinatario"] for r in all_records))
    print(f"[CSV 1] ✅ {len(all_records)} registros | {unique_dests} destinatarios únicos → {output}", flush=True)
    return all_records

# ═══════════════════════════════════════════
# CSV 2: Todos los remitentes (Recibidos)
# ═══════════════════════════════════════════
def csv2_remitentes():
    print("\n[CSV 2] Extrayendo TODOS los remitentes de recibidos...", flush=True)
    all_senders = []

    for email_addr, password in ACCOUNTS:
        try:
            mail = imap_connect(email_addr, password)
            mail.select("inbox", readonly=True)

            status, messages = mail.search(None, "ALL")
            msg_ids = messages[0].split()
            print(f"    [*] {email_addr}: {len(msg_ids)} mensajes en inbox", flush=True)

            for i in range(0, len(msg_ids), 50):
                # Progreso cada 250 mensajes
                if i > 0 and i % 250 == 0:
                    print(f"    [.] CSV2 progreso: {i}/{len(msg_ids)} | {len(all_senders)} registros", flush=True)
                # Reconectar cada 500
                if i > 0 and i % 500 == 0:
                    try: mail.logout()
                    except: pass
                    mail = imap_connect(email_addr, password)
                    mail.select("inbox", readonly=True)

                chunk = msg_ids[i:i+50]
                chunk_str = ",".join(m.decode() for m in chunk)
                data, mail = fetch_with_retry(mail, chunk_str, email_addr, password, "inbox", "CSV2 ")
                if data is None:
                    continue
                time.sleep(0.2)  # rate-limit entre batches

                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        from_raw = clean_header(msg.get('From', ''))
                        from_emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', from_raw.lower())
                        from_name = re.sub(r'<[^>]+>', '', from_raw).strip('" ').strip()
                        from_email = from_emails[0] if from_emails else from_raw.strip().lower()

                        all_senders.append({
                            "Cuenta_Destinataria": email_addr,
                            "Remitente_Email": from_email,
                            "Remitente_Nombre": from_name,
                            "Asunto": clean_header(msg.get('Subject', '')),
                            "Fecha": str(msg.get('Date')),
                        })

            try: mail.logout()
            except: pass
            print(f"    [+] {email_addr}: procesado", flush=True)
        except Exception as e:
            print(f"    [-] Error en {email_addr}: {e}", flush=True)

    output = GMAIL_CSV_OUTPUT / "csv2_remitentes.csv"
    headers = ["Cuenta_Destinataria", "Remitente_Email", "Remitente_Nombre", "Asunto", "Fecha"]
    with open(output, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(all_senders)

    unique_senders = len(set(r["Remitente_Email"] for r in all_senders))
    print(f"[CSV 2] ✅ {len(all_senders)} registros | {unique_senders} remitentes únicos → {output}", flush=True)
    return all_senders

# ═══════════════════════════════════════════
# CSV 3: Mensajes pendientes de respuesta + Borrador IA
# ═══════════════════════════════════════════
def csv3_pendientes_respuesta():
    print("\n[CSV 3] Detectando mensajes pendientes de respuesta...", flush=True)

    # Paso 1: Recolectar a quién ya respondimos (de enviados, IMAP directo)
    replied_to = set()
    for email_addr, password in ACCOUNTS:
        try:
            mail = imap_connect(email_addr, password)
            status, folders = mail.list()
            sent_folder = '"[Gmail]/Sent Mail"'
            for f in folders:
                f_str = f.decode()
                if '\\Sent' in f_str:
                    sent_folder = f_str.split(' "/" ')[-1]
                    break

            mail.select(sent_folder, readonly=True)
            status, messages = mail.search(None, "ALL")
            msg_ids = messages[0].split()

            for i in range(0, len(msg_ids), 50):
                if i > 0 and i % 500 == 0:
                    try: mail.logout()
                    except: pass
                    mail = imap_connect(email_addr, password)
                    mail.select(sent_folder, readonly=True)

                chunk = msg_ids[i:i+50]
                chunk_str = ",".join(m.decode() for m in chunk)
                data, mail = fetch_with_retry(mail, chunk_str, email_addr, password, sent_folder, "CSV3-sent ")
                if data is None:
                    continue
                time.sleep(0.2)  # rate-limit entre batches

                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        to_raw = clean_header(msg.get('To', ''))
                        dests = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', to_raw.lower())
                        replied_to.update(d for d in dests)

            try: mail.logout()
            except: pass
        except Exception as e:
            print(f"    [-] Error enviados {email_addr}: {e}", flush=True)

    print(f"    [*] Ya respondimos a {len(replied_to)} destinatarios únicos", flush=True)

    # Paso 2: Leer inbox, encontrar mensajes SIN respuesta
    pending = []
    for email_addr, password in ACCOUNTS:
        try:
            mail = imap_connect(email_addr, password)
            mail.select("inbox", readonly=True)

            status, messages = mail.search(None, "ALL")
            msg_ids = messages[0].split()

            for i in range(0, len(msg_ids), 50):
                if i > 0 and i % 500 == 0:
                    try: mail.logout()
                    except: pass
                    mail = imap_connect(email_addr, password)
                    mail.select("inbox", readonly=True)

                chunk = msg_ids[i:i+50]
                chunk_str = ",".join(m.decode() for m in chunk)
                data, mail = fetch_with_retry(mail, chunk_str, email_addr, password, "inbox", "CSV3-inbox ")
                if data is None:
                    continue
                time.sleep(0.2)  # rate-limit entre batches

                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        if is_auto_reply(msg):
                            continue

                        from_raw = clean_header(msg.get('From', ''))
                        from_emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', from_raw.lower())
                        from_email = from_emails[0] if from_emails else from_raw.strip().lower()

                        if from_email in replied_to:
                            continue

                        our_emails = {a[0] for a in ACCOUNTS}
                        if from_email in our_emails:
                            continue

                        body = get_body(msg)
                        subject = clean_header(msg.get('Subject', ''))

                        draft = generate_draft(from_email, subject, body[:500])

                        pending.append({
                            "Cuenta_Destinataria": email_addr,
                            "Remitente": from_email,
                            "Asunto": subject,
                            "Fecha": str(msg.get('Date')),
                            "Snippet": " ".join(body.split())[:200],
                            "Borrador_Respuesta_IA": draft
                        })

            try: mail.logout()
            except: pass
        except Exception as e:
            print(f"    [-] Error inbox {email_addr}: {e}", flush=True)

    # Deduplicar por remitente
    seen_senders = {}
    for p in pending:
        key = p["Remitente"]
        if key not in seen_senders:
            seen_senders[key] = p

    final = list(seen_senders.values())

    output = GMAIL_CSV_OUTPUT / "csv3_pendientes_respuesta.csv"
    headers = ["Cuenta_Destinataria", "Remitente", "Asunto", "Fecha", "Snippet", "Borrador_Respuesta_IA"]
    with open(output, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(final)

    print(f"[CSV 3] ✅ {len(final)} mensajes pendientes de respuesta → {output}", flush=True)
    return final

def generate_draft(sender_email, subject, body_snippet):
    """Genera borrador contextual básico."""
    es_markers = sum(1 for w in ["hola", "gracias", "consulta", "pregunta", "precio", "disponible", "servicio", "producto"] if w in body_snippet.lower())
    en_markers = sum(1 for w in ["hello", "thank", "question", "price", "available", "service", "product", "inquiry"] if w in body_snippet.lower())

    if es_markers >= en_markers:
        return f"Estimado/a, gracias por su mensaje sobre '{subject[:50]}'. Me pongo en contacto prontamente para atender su consulta. Saludos, Esteban."
    else:
        return f"Dear Sir/Madam, thank you for your message regarding '{subject[:50]}'. I will get back to you shortly. Best regards, Esteban."

# ═══════════════════════════════════════════
# CSV 4: Campañas email marketing + listas
# ═══════════════════════════════════════════
def csv4_campanas():
    print("\n[CSV 4] Extrayendo campañas y listas de contacto...", flush=True)
    campaigns = []

    # Fuente 1: marketing_memory.db
    for db_path in [CAMPAIGN_DB, Path("logs/marketing_memory.db"), Path("logs/campaigns/marketing_memory.db")]:
        if db_path.exists():
            try:
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("SELECT name, subject, message_path, contact_list_path, last_used FROM campaigns")
                for row in cursor.fetchall():
                    recipients = ""
                    if row[3] and os.path.exists(row[3]):
                        try:
                            with open(row[3], 'r', encoding='utf-8') as f:
                                recipients = str(sum(1 for line in f if line.strip()))
                        except: pass

                    message_preview = ""
                    if row[2] and os.path.exists(row[2]):
                        try:
                            with open(row[2], 'r', encoding='utf-8') as f:
                                message_preview = f.read()[:300]
                        except: pass

                    campaigns.append({
                        "Fuente": "memory_db",
                        "Campaña": row[0] or "",
                        "Asunto": row[1] or "",
                        "Cantidad_Destinatarios": recipients,
                        "Lista_Contactos": row[3] or "",
                        "Mensaje_Preview": message_preview,
                        "Fecha": row[4] or ""
                    })
                conn.close()
            except Exception as e:
                print(f"    [-] Error DB {db_path}: {e}", flush=True)

    # Fuente 2: contacts.db
    if DB_PATH.exists():
        try:
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(main)")
            columns = [col[1] for col in cursor.fetchall()]

            if 'campaigns' in columns and 'primary_email' in columns:
                cursor.execute("""
                    SELECT campaigns, COUNT(*) as cnt,
                           GROUP_CONCAT(DISTINCT primary_email) as sample_emails
                    FROM main
                    WHERE campaigns IS NOT NULL AND campaigns != ''
                    GROUP BY campaigns
                """)
                for row in cursor.fetchall():
                    campaign_name = row[0] if row[0] else ""
                    count = row[1] if row[1] else 0
                    sample = (row[2] or "")[:500]

                    campaigns.append({
                        "Fuente": "contacts_db",
                        "Campaña": campaign_name,
                        "Asunto": "",
                        "Cantidad_Destinatarios": str(count),
                        "Lista_Contactos": sample,
                        "Mensaje_Preview": "",
                        "Fecha": ""
                    })
            conn.close()
        except Exception as e:
            print(f"    [-] Error contacts.db: {e}", flush=True)

    # Fuente 3: Archivos de lista en data/contacts
    contacts_dir = ROOT / "data" / "contacts"
    if contacts_dir.exists():
        for csv_file in contacts_dir.glob("*.csv"):
            try:
                with open(csv_file, 'r', encoding='utf-8-sig') as f:
                    count = sum(1 for line in f) - 1
                campaigns.append({
                    "Fuente": "archivo_csv",
                    "Campaña": csv_file.stem,
                    "Asunto": "",
                    "Cantidad_Destinatarios": str(max(0, count)),
                    "Lista_Contactos": str(csv_file),
                    "Mensaje_Preview": "",
                    "Fecha": ""
                })
            except: pass

    # Fuente 4: Logs de campaña
    log_dir = ROOT / "logs" / "campaigns"
    if log_dir.exists():
        for log_file in log_dir.glob("log_*.txt"):
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
                found = email_pattern.findall(content)
                campaigns.append({
                    "Fuente": "log_campaña",
                    "Campaña": log_file.stem,
                    "Asunto": "",
                    "Cantidad_Destinatarios": str(len(found)),
                    "Lista_Contactos": "; ".join(found[:20]),
                    "Mensaje_Preview": content[:300],
                    "Fecha": datetime.fromtimestamp(os.path.getmtime(log_file)).strftime('%Y-%m-%d %H:%M')
                })
            except: pass

    # Fuente 5: identity_map.json
    idmap_path = ROOT / "data" / "inputs" / "identity_map.json"
    if not idmap_path.exists():
        idmap_path = ROOT / "identity_map.json"
    if not idmap_path.exists():
        idmap_path = Path("identity_map.json")
    if idmap_path.exists():
        try:
            with open(idmap_path, 'r', encoding='utf-8') as f:
                idmap = json.load(f)
            campaigns.append({
                "Fuente": "identity_map",
                "Campaña": "identity_map",
                "Asunto": "",
                "Cantidad_Destinatarios": str(len(idmap)),
                "Lista_Contactos": "; ".join(list(idmap.keys())[:20]),
                "Mensaje_Preview": json.dumps({k: idmap[k] for k in list(idmap.keys())[:5]}, indent=2),
                "Fecha": ""
            })
        except: pass

    output = GMAIL_CSV_OUTPUT / "csv4_campanas_email_marketing.csv"
    headers = ["Fuente", "Campaña", "Asunto", "Cantidad_Destinatarios", "Lista_Contactos", "Mensaje_Preview", "Fecha"]
    with open(output, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(campaigns)

    print(f"[CSV 4] ✅ {len(campaigns)} registros de campañas → {output}", flush=True)
    return campaigns

# ═══════════════════════════════════════════
# CSV 5: Estado de delivery / rebotes — IMAP directo
# ═══════════════════════════════════════════
def csv5_delivery_status():
    print("\n[CSV 5] Analizando estado de delivery (rebotes)...", flush=True)
    all_bounces = []

    NOT_FOUND_STRINGS = [
        "no se ha encontrado", "address couldn't be found", "does not exist",
        "user unknown", "no such user", "invalid recipient", "recipient not found",
        "unknown user", "no mailbox", "delivery failed", "couldn't be found",
        "no existe", "destinatario no encontrado", "recipient does not exist"
    ]
    BLOCKED_STRINGS = [
        "bloqueado", "message blocked", "message rejected", "spam",
        "policy rejection", "blacklisted", "denied", "rejected by",
        "contenido restringido", "rejected for policy reasons"
    ]
    CONNECTION_STRINGS = [
        "connection", "timeout", "unreachable", "host not found",
        "dns", "no route to host", "connection refused", "connection timed out"
    ]
    QUOTA_STRINGS = [
        "quota", "mailbox full", "over quota", "storage limit",
        "buzón lleno", "excede el límite"
    ]

    RECIPIENT_PATTERNS = [
        r"wasn't delivered to\s+([^\s,<]+)",
        r"Tu mensaje no se ha entregado a\s+([^\s,<]+)",
        r"Your message to\s+([^\s,<]+)",
        r"couldn't be delivered to\s+([^\s,<]+)",
        r"no se pudo entregar a\s+([^\s,<]+)",
        r"delivery to the following recipient failed\s+([^\s,<]+)",
        r"failed recipient:\s+([^\s,<]+)",
        r"<([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})>",
    ]

    for email_addr, password in ACCOUNTS:
        try:
            mail = imap_connect(email_addr, password)
            mail.select("inbox")

            status, messages = mail.search(None, '(FROM "mailer-daemon")')
            msg_ids = messages[0].split()
            print(f"    [*] {email_addr}: {len(msg_ids)} mensajes mailer-daemon", flush=True)

            for idx, m_id in enumerate(msg_ids):
                try:
                    # Reconectar cada 500
                    if idx > 0 and idx % 500 == 0:
                        try: mail.logout()
                        except: pass
                        mail = imap_connect(email_addr, password)
                        mail.select("inbox")
                        # Re-search después de reconectar
                        status, messages = mail.search(None, '(FROM "mailer-daemon")')
                        msg_ids = messages[0].split()

                    status, data = mail.fetch(m_id, "(RFC822)")
                    msg = email.message_from_bytes(data[0][1])
                    body = get_body(msg)
                    body_lower = body.lower()
                    subject = clean_header(msg.get('Subject', ''))
                    date = str(msg.get('Date'))

                    # Extraer email rebotado
                    bounced_email = ""
                    for p in RECIPIENT_PATTERNS:
                        match = re.search(p, body, re.I)
                        if match:
                            bounced_email = match.group(1).strip('<>.,;').lower()
                            break

                    if not bounced_email:
                        emails_found = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', body)
                        for ef in emails_found:
                            if ef.lower() not in [email_addr.lower(), "mailer-daemon@googlemail.com", "mailer-daemon@google.com"]:
                                bounced_email = ef.lower()
                                break

                    # Clasificar
                    reason = "Desconocido"
                    detail = ""
                    if any(s in body_lower for s in NOT_FOUND_STRINGS):
                        reason = "No Encontrado"
                        detail = "Email inexistente / dirección inválida"
                    elif any(s in body_lower for s in BLOCKED_STRINGS):
                        reason = "Bloqueado"
                        detail = "Mensaje bloqueado por política anti-spam"
                    elif any(s in body_lower for s in CONNECTION_STRINGS):
                        reason = "Error de Conexión"
                        detail = "Problema DNS / servidor inalcanzable"
                    elif any(s in body_lower for s in QUOTA_STRINGS):
                        reason = "Buzón Lleno"
                        detail = "Cuota de almacenamiento excedida"

                    smtp_match = re.search(r'(\d{3})\s+[\d.]+\s+', body)
                    smtp_code = smtp_match.group(1) if smtp_match else ""

                    if bounced_email:
                        all_bounces.append({
                            "Cuenta_Remitente": email_addr,
                            "Destinatario_Fallido": bounced_email,
                            "Razón": reason,
                            "Detalle": detail,
                            "Código_SMTP": smtp_code,
                            "Asunto_Original": subject,
                            "Fecha_Bounce": date,
                            "Fragmento": " ".join(body.split())[:300]
                        })
                except socket.timeout:
                    print(f"    [!] CSV5 timeout en msg {idx}, saltando", flush=True)
                    continue
                except Exception as e:
                    continue

            try: mail.logout()
            except: pass
        except Exception as e:
            print(f"    [-] Error bounce {email_addr}: {e}", flush=True)

    # Deduplicar por destinatario
    seen = {}
    for b in all_bounces:
        key = b["Destinatario_Fallido"]
        if key not in seen:
            seen[key] = b

    final = list(seen.values())

    output = GMAIL_CSV_OUTPUT / "csv5_delivery_status.csv"
    headers = ["Cuenta_Remitente", "Destinatario_Fallido", "Razón", "Detalle", "Código_SMTP", "Asunto_Original", "Fecha_Bounce", "Fragmento"]
    with open(output, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(final)

    by_reason = {}
    for b in final:
        by_reason[b["Razón"]] = by_reason.get(b["Razón"], 0) + 1

    print(f"[CSV 5] ✅ {len(final)} destinatarios con entrega fallida → {output}", flush=True)
    for reason, count in sorted(by_reason.items(), key=lambda x: -x[1]):
        print(f"    - {reason}: {count}", flush=True)
    return final

# ═══════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════
def main():
    print("=" * 60, flush=True)
    print(" GENERADOR DE 5 CSVs DESDE GMAIL", flush=True)
    print(f" Cuentas: {len(ACCOUNTS)}", flush=True)
    print(f" Output: {GMAIL_CSV_OUTPUT}", flush=True)
    print(f" IMAP Timeout: 30s | Batch: 50 | Reconnect: 500", flush=True)
    print("=" * 60, flush=True)

    start = datetime.now()

    csv1_destinatarios()
    print("    [⏳] Pausa 10s para respetar rate limits...", flush=True); time.sleep(10)
    csv2_remitentes()
    print("    [⏳] Pausa 10s para respetar rate limits...", flush=True); time.sleep(10)
    csv3_pendientes_respuesta()
    csv4_campanas()
    print("    [⏳] Pausa 10s para respetar rate limits...", flush=True); time.sleep(10)
    csv5_delivery_status()

    elapsed = (datetime.now() - start).total_seconds()
    print("\n" + "=" * 60, flush=True)
    print(f" COMPLETADO en {elapsed:.1f}s", flush=True)
    print(f" Archivos en: {GMAIL_CSV_OUTPUT}", flush=True)
    print("=" * 60, flush=True)

if __name__ == "__main__":
    main()
