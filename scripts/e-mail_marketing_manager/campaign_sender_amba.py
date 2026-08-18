"""
campaign_sender_amba.py — Campana AMBA (Buenos Aires + CABA + AMBA) 4 de agosto.
12 cuentas envian en paralelo. Cada cuenta envia a si misma (TO)
con 50 contactos de AMBA en BCC, incluyendo emails secundarios.
Delay senoide 1-10-1 min entre emails.
"""

import smtplib
import time
import math
import sqlite3
import logging
import sys
import os
import glob
import re
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from accounts_config import ACCOUNTS, DB_PATH, SMTP_SERVER, SMTP_PORT, CAMPAIGN, SEND_CONFIG, LOG_DIR

os.makedirs(LOG_DIR, exist_ok=True)
log_filename = f"log_amba_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
log_path = os.path.join(LOG_DIR, log_filename)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_path, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)


JUNK_SECONDARY = {
    "secondary_emails", "tu@email.com", "email@email.com",
    "tuemail@gmail.com", "test@test.com", "ejemplo@ejemplo.com",
    "none", "n/a", "null", "", " ",
    "support@domain.com", "user@website.com", "info@domain.com",
    "admin@domain.com", "contact@domain.com", "hello@domain.com",
    "mail@domain.com", "office@domain.com", "team@domain.com",
}

JUNK_DOMAINS = {"domain.com", "website.com", "example.com", "test.com", "email.com"}


def get_already_sent():
    """Lee logs anteriores y retorna set de emails ya enviados."""
    sent = set()
    for pattern in ["log_amba_*.txt", "log_ba_ciclo_*.txt", "log_lanus_cycle_*.txt", "log_national_*.txt"]:
        filepath_pattern = os.path.join(LOG_DIR, pattern)
        for filepath in glob.glob(filepath_pattern):
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if "[OK]" in line:
                            parts = line.strip().split("[OK]")
                            if len(parts) == 2:
                                email = parts[1].strip()
                                if "@" in email:
                                    sent.add(email.lower())
            except Exception:
                pass
    return sent


def parse_secondary_emails(raw):
    """Parsea secondary_emails y retorna lista de emails validos (max 5 por contacto)."""
    if not raw or raw.strip().lower() in JUNK_SECONDARY:
        return []
    parts = re.split(r"[;,]", raw)
    valid = []
    for p in parts:
        email = p.strip().lower()
        if (
            email
            and "@" in email
            and email not in JUNK_SECONDARY
            and len(email) > 5
            and len(email) < 80
            and not any(d in email for d in JUNK_DOMAINS)
        ):
            valid.append(email)
    return valid[:5]


def get_amba_emails():
    """Obtiene contactos validos de AMBA (Buenos Aires + CABA + ciudades AMBA)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT l.primary_email, l.secondary_emails, m.title, m.city, m.province
        FROM main m
        JOIN lead l ON m.rowid = l.rowid
        JOIN contact ct ON m.rowid = ct.rowid
        WHERE l.primary_email IS NOT NULL AND l.primary_email != ''
        AND ct.deliverability IN ('valid', 'pending', 'generic')
        AND (
            m.province LIKE '%Buenos Aires%'
            OR m.province LIKE '%Autonoma%'
            OR m.province LIKE '%Autónoma%'
            OR m.province LIKE '%Cdad.%'
            OR m.province LIKE '%Ciudad Autonoma%'
            OR m.province LIKE '%Capital Federal%'
            OR m.province LIKE '%Gran Buenos Aires%'
            OR m.province LIKE '%Metropolitana%'
            OR (
                (m.province IS NULL OR m.province = '')
                AND m.city IN (
                    'Lanús','Avellaneda','Lomas de Zamora','Quilmes',
                    'Almirante Brown','Esteban Echeverría','La Matanza',
                    'Tres de Febrero','Vicente López','San Isidro',
                    'San Martín','Ituzaingó','Hurlingham','Morón',
                    'Merlo','Moreno','La Plata','Berazategui',
                    'Florencio Varela','Presidente Perón','San Vicente'
                )
            )
        )
        ORDER BY m.title
    """)
    contacts = []
    for row in c.fetchall():
        email = row[0].strip() if row[0] else ""
        if email and "@" in email:
            contacts.append({
                "email": email,
                "secondary": parse_secondary_emails(row[1]),
                "title": row[2] or "",
                "city": row[3] or "",
                "province": row[4] or "",
            })
    conn.close()
    return contacts


def send_email_bcc(account, to_email, bcc_emails, subject, body):
    """Envia email con BCC a multiples destinatarios."""
    try:
        msg = MIMEMultipart()
        msg["From"] = account["email"]
        msg["To"] = to_email
        msg["Subject"] = subject
        msg["Bcc"] = ", ".join(bcc_emails)
        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.login(account["email"], account["app_password"])
            server.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"[{account['email']}] ERROR: {e}")
        return False


def sinusoidal_delays():
    """Generador de delays senoidales: 1,2,3,...,10,9,...,2,1 (simetrico)"""
    cycle_list = list(range(1, 11)) + list(range(9, 0, -1))
    while True:
        for d in cycle_list:
            yield d


def worker(account, chunks, worker_id):
    """Worker que envia una lista de chunks (cada chunk = 50 emails BCC)."""
    delay_gen = sinusoidal_delays()
    stats = {"exito": 0, "fallo": 0}

    logger.info(f"[{account['email']}] Hilo {worker_id} iniciado con {len(chunks)} emails")

    for i, chunk in enumerate(chunks):
        bcc_list = [c["email"] for c in chunk]
        logger.info(f"[{account['email']}] [{i+1}/{len(chunks)}] Enviando a {len(bcc_list)} contactos BCC")

        success = send_email_bcc(
            account=account,
            to_email=account["email"],
            bcc_emails=bcc_list,
            subject=CAMPAIGN["subject"],
            body=CAMPAIGN["message"],
        )

        if success:
            stats["exito"] += 1
            for c in chunk:
                logger.info(f"[{account['email']}] [OK] {c['email']}")
        else:
            stats["fallo"] += 1
            for c in chunk:
                logger.error(f"[{account['email']}] [FALLO] {c['email']}")

        if i < len(chunks) - 1:
            delay_min = next(delay_gen)
            delay_sec = delay_min * 60
            next_send = datetime.now() + timedelta(seconds=delay_sec)
            logger.info(f"[{account['email']}] [WAIT] Proximo en {delay_min} min ({next_send.strftime('%H:%M:%S')})")
            time.sleep(delay_sec)

    logger.info(f"[{account['email']}] Hilo {worker_id} finalizado - Exitos: {stats['exito']}, Fallos: {stats['fallo']}")
    return stats


def main():
    import threading

    all_contacts = get_amba_emails()
    already_sent = get_already_sent()

    contacts = [c for c in all_contacts if c["email"].lower() not in already_sent]

    secondary_pool = []
    seen_secondary = set()
    for c in contacts:
        for sec in c["secondary"]:
            if sec not in already_sent and sec not in seen_secondary:
                seen_secondary.add(sec)
                secondary_pool.append({"email": sec, "title": c["title"], "city": c["city"], "province": c["province"]})

    all_targets = contacts + secondary_pool

    logger.info("=" * 60)
    logger.info("CAMPANA AMBA - 50 BCC POR EMAIL - 4 AGOSTO 2026")
    logger.info(f"Contactos primarios AMBA: {len(all_contacts)}")
    logger.info(f"Ya enviados (logs previos): {len(already_sent)}")
    logger.info(f"Primarios pendientes: {len(contacts)}")
    logger.info(f"Secundarios disponibles: {len(secondary_pool)}")
    logger.info(f"TOTAL targets: {len(all_targets)}")
    logger.info(f"Cuentas: {len(ACCOUNTS)}")
    logger.info(f"BCC por email: 50")
    logger.info("=" * 60)

    if not all_targets:
        logger.info("No hay contactos pendientes.")
        return

    BCC_PER_EMAIL = 50
    emails_per_account = 18
    total_emails_needed = math.ceil(len(all_targets) / BCC_PER_EMAIL)
    total_emails_possible = emails_per_account * len(ACCOUNTS)
    total_to_send = min(total_emails_needed, total_emails_possible)

    logger.info(f"Emails necesarios: {total_emails_needed}")
    logger.info(f"Emails posibles: {total_emails_possible}")
    logger.info(f"Emails a enviar: {total_to_send}")

    chunks = []
    for i in range(0, len(all_targets), BCC_PER_EMAIL):
        chunk = all_targets[i:i + BCC_PER_EMAIL]
        if chunk:
            chunks.append(chunk)

    chunks = chunks[:total_to_send]

    account_chunks = {i: [] for i in range(len(ACCOUNTS))}
    for i, chunk in enumerate(chunks):
        account_idx = i % len(ACCOUNTS)
        account_chunks[account_idx].append(chunk)

    logger.info(f"\nDistribucion:")
    for idx, acc in enumerate(ACCOUNTS):
        n = len(account_chunks[idx])
        if n > 0:
            logger.info(f"  {acc['email']}: {n} emails ({n * BCC_PER_EMAIL} contactos)")

    logger.info(f"\nIniciando envios...")
    start_time = datetime.now()

    threads = []
    for i, acc in enumerate(ACCOUNTS):
        if account_chunks[i]:
            t = threading.Thread(target=worker, args=(acc, account_chunks[i], i + 1))
            t.start()
            threads.append(t)
            time.sleep(0.5)

    for t in threads:
        t.join()

    end_time = datetime.now()
    duration = end_time - start_time

    logger.info("\n" + "=" * 60)
    logger.info("CAMPANA COMPLETADA")
    logger.info(f"Inicio: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Fin: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Duracion: {duration}")
    logger.info(f"Total emails enviados: {total_to_send}")
    logger.info(f"Total contactos alcanzados: {total_to_send * BCC_PER_EMAIL}")
    logger.info(f"Log: {log_path}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
