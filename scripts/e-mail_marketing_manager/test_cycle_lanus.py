"""
test_cycle_lanus.py — Un ciclo completo de delay senoide a contactos de Lanus.
12 cuentas envian en paralelo. Cada cuenta envia 18 emails (ciclo 1-10-1).
Total: 12 x 18 = 216 emails.
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
from itertools import cycle

from accounts_config import ACCOUNTS, DB_PATH, SMTP_SERVER, SMTP_PORT, CAMPAIGN, SEND_CONFIG, LOG_DIR

os.makedirs(LOG_DIR, exist_ok=True)
log_filename = f"log_lanus_cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
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
    pattern = os.path.join(LOG_DIR, "log_lanus_cycle_*.txt")
    for filepath in glob.glob(pattern):
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


def get_lanus_emails():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT l.primary_email FROM main m
        JOIN lead l ON m.rowid = l.rowid
        JOIN contact ct ON m.rowid = ct.rowid
        WHERE l.primary_email IS NOT NULL AND l.primary_email != ''
        AND ct.deliverability = 'valid'
        AND (m.city LIKE 'Lan%' OR m.city LIKE 'B1824%' OR m.city LIKE 'B1822%' OR m.city LIKE 'B1825%')
        ORDER BY m.title''')
    emails = [row[0].strip() for row in c.fetchall() if row[0] and row[0].strip()]
    conn.close()
    return emails


def send_email(account, to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = account["email"]
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain", "utf-8"))
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.login(account["email"], account["app_password"])
            server.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"[{account['email']}] ERROR: {e}")
        return False


def sinusoidal_delays():
    cycle_list = list(range(1, 11)) + list(range(9, 1, -1))
    while True:
        for d in cycle_list:
            yield d


def worker(account, emails, worker_id):
    delay_gen = sinusoidal_delays()
    stats = {"exito": 0, "fallo": 0}

    logger.info(f"[{account['email']}] Hilo {worker_id} iniciado con {len(emails)} contactos")

    for i, email in enumerate(emails):
        logger.info(f"[{account['email']}] [{i+1}/{len(emails)}] Enviando a {email}")

        success = send_email(
            account=account,
            to_email=email,
            subject=CAMPAIGN["subject"],
            body=CAMPAIGN["message"],
        )

        if success:
            stats["exito"] += 1
            logger.info(f"[{account['email']}] [OK] {email}")
        else:
            stats["fallo"] += 1
            logger.error(f"[{account['email']}] [FALLO] {email}")

        if i < len(emails) - 1:
            delay_min = next(delay_gen)
            delay_sec = delay_min * 60
            next_send = datetime.now() + timedelta(seconds=delay_sec)
            logger.info(f"[{account['email']}] [WAIT] Proximo en {delay_min} min ({next_send.strftime('%H:%M:%S')})")
            time.sleep(delay_sec)

    logger.info(f"[{account['email']}] Hilo {worker_id} finalizado - Exitos: {stats['exito']}, Fallos: {stats['fallo']}")
    return stats


def main():
    import threading

    all_emails = get_lanus_emails()
    already_sent = get_already_sent()

    emails = [e for e in all_emails if e.lower() not in already_sent]

    logger.info("=" * 60)
    logger.info("CICLO COMPLETO LANUS - 12 CUENTAS")
    logger.info(f"Contactos totales: {len(all_emails)}")
    logger.info(f"Ya enviados: {len(already_sent)}")
    logger.info(f"Pendientes: {len(emails)}")
    logger.info(f"Cuentas: {len(ACCOUNTS)}")
    logger.info(f"Limite por cuenta: 18 emails (ciclo senoide)")
    logger.info(f"Total a enviar: {min(len(emails), 18 * len(ACCOUNTS))}")
    logger.info("=" * 60)

    if not emails:
        logger.info("No hay contactos pendientes. Todos ya recibieron el mensaje.")
        return

    emails_per_account = 18
    total_to_send = min(len(emails), emails_per_account * len(ACCOUNTS))
    selected_emails = emails[:total_to_send]

    account_chunks = []
    for i in range(len(ACCOUNTS)):
        start = i * emails_per_account
        end = start + emails_per_account
        chunk = selected_emails[start:end]
        if chunk:
            account_chunks.append((ACCOUNTS[i], chunk))

    logger.info(f"\nDistribucion:")
    for acc, chunk in account_chunks:
        logger.info(f"  {acc['email']}: {len(chunk)} emails")

    logger.info(f"\nIniciando envios...")
    start_time = datetime.now()

    threads = []
    for i, (acc, chunk) in enumerate(account_chunks):
        t = threading.Thread(target=worker, args=(acc, chunk, i+1))
        t.start()
        threads.append(t)
        time.sleep(0.5)

    for t in threads:
        t.join()

    end_time = datetime.now()
    duration = end_time - start_time

    logger.info("\n" + "=" * 60)
    logger.info("CICLO COMPLETADO")
    logger.info(f"Inicio: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Fin: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Duracion: {duration}")
    logger.info(f"Total enviados: {total_to_send}")
    logger.info(f"Log: {log_path}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
