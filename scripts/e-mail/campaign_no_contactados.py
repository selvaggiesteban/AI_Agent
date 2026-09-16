"""
campaign_no_contactados.py — Campaña emails no contactados (deliverability='valid' AND campaigns IS NULL).
12 cuentas envían en paralelo. Cada cuenta envía a sí misma (TO) con 50 contactos en BCC.
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
import argparse
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading

from accounts_config import ACCOUNTS, DB_PATH, SMTP_SERVER, SMTP_PORT, CAMPAIGN, SEND_CONFIG, LOG_DIR

import re

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

def is_valid_email(email: str) -> bool:
    """Valida email con regex estricta."""
    if not email or not email.strip():
        return False
    email = email.strip().lower()
    if not EMAIL_REGEX.match(email):
        return False
    return True

os.makedirs(LOG_DIR, exist_ok=True)
log_filename = f"log_no_contactados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
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

CAMPAIGN_NO_CONTACTADOS = {
    "id": "no_contactados_20260810",
    "title": "No Contactados - Servicio Tecnico",
    "subject": "Servicio Tecnico de Computadoras y Productos de Tecnologia",
    "message": (
        "Hola, buenos dias. "
        "Como estas? Espero que muy bien. "
        "Me comunico facilitando servicio tecnico de computadoras y productos de tecnologia. "
        "Brindamos soluciones tanto para particulares como para comercios y empresas de la zona. "
        "Si necesitás reparacion, mantenimiento o equipamiento, podes contactarnos. "
        "Quedo a disposicion para lo que necesites.\n\n"
        "Saludos cordiales"
    ),
}

def get_already_sent():
    """Lee logs anteriores y retorna set de emails ya enviados."""
    sent = set()
    for pattern in ["log_amba_*.txt", "log_ba_ciclo_*.txt", "log_lanus_cycle_*.txt", "log_national_*.txt", "log_no_contactados_*.txt"]:
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


def get_no_contactados_emails():
    """Obtiene contactos válidos con smtp_processed=1 NO contactados 3-7 agosto 2026."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT l.primary_email, m.title, m.city, m.province
        FROM main m
        JOIN lead l ON m.rowid = l.rowid
        JOIN contact ct ON m.rowid = ct.rowid
        WHERE l.primary_email IS NOT NULL AND l.primary_email != ''
        AND ct.deliverability = 'valid'
        AND ct.smtp_processed = '1'
        AND NOT EXISTS (
            SELECT 1 FROM campaign cp
            WHERE cp.contact_rowid = m.rowid
            AND (
                cp.date LIKE "2026-08-03%" OR cp.date LIKE "2026-08-04%" 
                OR cp.date LIKE "2026-08-05%" OR cp.date LIKE "2026-08-06%" 
                OR cp.date LIKE "2026-08-07%" OR cp.date LIKE "03/08/2026%" 
                OR cp.date LIKE "04/08/2026%" OR cp.date LIKE "05/08/2026%" 
                OR cp.date LIKE "06/08/2026%" OR cp.date LIKE "07/08/2026%"
                OR cp.date LIKE "03.08.2026%" OR cp.date LIKE "04.08.2026%"
                OR cp.date LIKE "05.08.2026%" OR cp.date LIKE "06.08.2026%"
                OR cp.date LIKE "07.08.2026%"
            )
        )
        ORDER BY m.title
        LIMIT 6000
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
    """Envía email con BCC a múltiples destinatarios."""
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
    """Worker que envía una lista de chunks (cada chunk = 50 emails BCC)."""
    delay_gen = sinusoidal_delays()
    stats = {"exito": 0, "fallo": 0}

    logger.info(f"[{account['email']}] Hilo {worker_id} iniciado con {len(chunks)} emails")

    for i, chunk in enumerate(chunks):
        bcc_list = [c["email"] for c in chunk if is_valid_email(c["email"])]
        if not bcc_list:
            logger.warning(f"[{account['email']}] [{i+1}/{len(chunks)}] Lote sin emails válidos, saltando")
            continue
        logger.info(f"[{account['email']}] [{i+1}/{len(chunks)}] Enviando a {len(bcc_list)} contactos BCC")

        success = send_email_bcc(
            account=account,
            to_email=account["email"],
            bcc_emails=bcc_list,
            subject=CAMPAIGN_NO_CONTACTADOS["subject"],
            body=CAMPAIGN_NO_CONTACTADOS["message"],
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


def run_test():
    """Test: 1 email por cuenta a sí misma, sin BCC."""
    logger.info("=" * 60)
    logger.info("TEST: 1 email por cuenta, sin BCC")
    logger.info(f"Cuentas: {len(ACCOUNTS)}")
    logger.info("=" * 60)

    results = {"exito": 0, "fallo": 0}

    for i, account in enumerate(ACCOUNTS, 1):
        logger.info(f"\n--- Cuenta {i}/{len(ACCOUNTS)}: {account['email']} ---")

        success = send_email_bcc(
            account=account,
            to_email=account["email"],
            bcc_emails=[],
            subject=f"TEST - {CAMPAIGN_NO_CONTACTADOS['subject']}",
            body=CAMPAIGN_NO_CONTACTADOS["message"],
        )

        if success:
            logger.info(f"[OK] Email enviado desde {account['email']}")
            results["exito"] += 1
        else:
            logger.error(f"[FALLO] No se pudo enviar desde {account['email']}")
            results["fallo"] += 1

    logger.info("\n" + "=" * 60)
    logger.info("RESUMEN TEST")
    logger.info(f"Exitos: {results['exito']}/{len(ACCOUNTS)}")
    logger.info(f"Fallos: {results['fallo']}/{len(ACCOUNTS)}")
    logger.info("=" * 60)

    return results


def run_dry_run():
    """Dry-run: simula distribución sin enviar."""
    all_contacts = get_no_contactados_emails()
    already_sent = get_already_sent()

    contacts = [c for c in all_contacts if c["email"].lower() not in already_sent]

    logger.info("=" * 60)
    logger.info("DRY-RUN: Simulación de campaña No Contactados")
    logger.info(f"Contactos totales válidos sin campaña: {len(all_contacts)}")
    logger.info(f"Ya enviados (logs previos): {len(already_sent)}")
    logger.info(f"Pendientes: {len(contacts)}")
    logger.info(f"Cuentas: {len(ACCOUNTS)}")
    logger.info(f"BCC por email: 50")
    logger.info("=" * 60)

    if not contacts:
        logger.info("No hay contactos pendientes.")
        return

    BCC_PER_EMAIL = 50
    total_emails_needed = math.ceil(len(contacts) / BCC_PER_EMAIL)
    total_emails_possible = 50 * len(ACCOUNTS)  # sin límite artificial
    total_to_send = min(total_emails_needed, total_emails_possible)

    logger.info(f"Emails necesarios: {total_emails_needed}")
    logger.info(f"Emails posibles (50/cuenta): {total_emails_possible}")
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

    logger.info(f"\nDistribución:")
    for idx, acc in enumerate(ACCOUNTS):
        n = len(account_chunks[idx])
        if n > 0:
            logger.info(f"  {acc['email']}: {n} emails ({n * BCC_PER_EMAIL} contactos)")

    logger.info(f"\nDuración estimada (paralelo): ~{(len(chunks[0]) * 5.5) if chunks else 0:.0f} min")


def main():
    parser = argparse.ArgumentParser(description="Campaign No Contactados - 12 hilos paralelos")
    parser.add_argument("--test", action="store_true", help="Test: 1 email por cuenta, sin BCC")
    parser.add_argument("--dry-run", action="store_true", help="Simular distribución sin enviar")
    args = parser.parse_args()

    if args.test:
        run_test()
    elif args.dry_run:
        run_dry_run()
    else:
        # Campaña completa
        logger.info("=" * 60)
        logger.info("CAMPANA NO CONTACTADOS - 50 BCC POR EMAIL - 12 HILOS PARALELOS")
        logger.info("=" * 60)

        all_contacts = get_no_contactados_emails()
        already_sent = get_already_sent()

        contacts = [c for c in all_contacts if c["email"].lower() not in already_sent]

        # Filtrar solo emails válidos
        contacts = [c for c in contacts if is_valid_email(c["email"])]

        logger.info(f"Contactos totales válidos sin campaña: {len(all_contacts)}")
        logger.info(f"Ya enviados (logs previos): {len(already_sent)}")
        logger.info(f"Pendientes: {len(contacts)}")
        logger.info(f"Cuentas: {len(ACCOUNTS)}")
        logger.info(f"BCC por email: 50")
        logger.info("=" * 60)

        if not contacts:
            logger.info("No hay contactos pendientes.")
            return

        BCC_PER_EMAIL = 50
        total_emails_needed = math.ceil(len(contacts) / BCC_PER_EMAIL)
        total_emails_possible = 50 * len(ACCOUNTS)
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

        logger.info(f"\nDistribución:")
        for idx, acc in enumerate(ACCOUNTS):
            n = len(account_chunks[idx])
            if n > 0:
                logger.info(f"  {acc['email']}: {n} emails ({n * BCC_PER_EMAIL} contactos)")

        logger.info(f"\nIniciando envíos en paralelo...")
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
        logger.info(f"Duración: {duration}")
        logger.info(f"Total emails enviados: {total_to_send}")
        logger.info(f"Total contactos alcanzados: {total_to_send * BCC_PER_EMAIL}")
        logger.info(f"Log: {log_path}")
        logger.info("=" * 60)


if __name__ == "__main__":
    main()