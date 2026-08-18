"""
campaign_sender_ba.py — Campana BA/CABA con 50 BCC por email.
12 cuentas envian en paralelo. Cada cuenta envia a si misma (TO)
con 50 contactos de Buenos Aires/CABA en BCC.
Delay senoide 1-10-1 min entre emails.
"""

import smtplib
import time
import math
import sqlite3
import logging
import sys
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from accounts_config import ACCOUNTS, DB_PATH, SMTP_SERVER, SMTP_PORT, CAMPAIGN, SEND_CONFIG, LOG_DIR

os.makedirs(LOG_DIR, exist_ok=True)
log_filename = f"log_ba_ciclo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
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


def get_already_sent():
    """Lee logs anteriores y retorna set de emails ya enviados."""
    import glob
    sent = set()
    for pattern in ["log_ba_ciclo_*.txt", "log_lanus_cycle_*.txt"]:
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


def get_ba_caba_emails():
    """Obtiene contactos validos de Buenos Aires y CABA."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT l.primary_email, m.title, m.city, m.province
        FROM main m
        JOIN lead l ON m.rowid = l.rowid
        JOIN contact ct ON m.rowid = ct.rowid
        WHERE l.primary_email IS NOT NULL AND l.primary_email != ''
        AND ct.deliverability = 'valid'
        AND (
            m.province LIKE '%Buenos Aires%'
            OR m.province LIKE '%CABA%'
            OR m.province LIKE '%Ciudad Autonoma%'
            OR m.province LIKE '%Cdad.%'
            OR m.province = 'Capital Federal'
        )
        ORDER BY m.title
    """)
    contacts = []
    for row in c.fetchall():
        email = row[0].strip() if row[0] else ""
        if email and "@" in email:
            contacts.append({
                "email": email,
                "title": row[1] or "",
                "city": row[2] or "",
                "province": row[3] or "",
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
    """Generador de delays senoidales: 1,2,3,...,10,9,...,2"""
    cycle_list = list(range(1, 11)) + list(range(9, 1, -1))
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

    all_contacts = get_ba_caba_emails()
    already_sent = get_already_sent()

    contacts = [c for c in all_contacts if c["email"].lower() not in already_sent]

    logger.info("=" * 60)
    logger.info("CAMPANA BA/CABA - 50 BCC POR EMAIL")
    logger.info(f"Contactos totales BA/CABA: {len(all_contacts)}")
    logger.info(f"Ya enviados: {len(already_sent)}")
    logger.info(f"Pendientes: {len(contacts)}")
    logger.info(f"Cuentas: {len(ACCOUNTS)}")
    logger.info(f"BCC por email: 50")
    logger.info("=" * 60)

    if not contacts:
        logger.info("No hay contactos pendientes.")
        return

    BCC_PER_EMAIL = 50
    emails_per_account = 18
    total_emails_needed = math.ceil(len(contacts) / BCC_PER_EMAIL)
    total_emails_possible = emails_per_account * len(ACCOUNTS)
    total_to_send = min(total_emails_needed, total_emails_possible)

    logger.info(f"Emails necesarios: {total_emails_needed}")
    logger.info(f"Emails posibles: {total_emails_possible}")
    logger.info(f"Emails a enviar: {total_to_send}")

    chunks = []
    for i in range(0, len(contacts), BCC_PER_EMAIL):
        chunk = contacts[i:i + BCC_PER_EMAIL]
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
