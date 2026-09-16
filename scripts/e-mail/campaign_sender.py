"""
campaign_sender.py — Motor de envio de campanas de email marketing.
Envia emails via SMTP con delay senoide entre envios.
Uso:
    python campaign_sender.py                    # Ejecuta campana completa
    python campaign_sender.py --test             # Test: 1 email por cuenta, sin BCC
    python campaign_sender.py --test --dry-run   # Solo muestra lo que hariamos
"""

import smtplib
import time
import math
import sqlite3
import logging
import sys
import os
import argparse
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from itertools import cycle

from accounts_config import (
    ACCOUNTS, DB_PATH, SMTP_SERVER, SMTP_PORT,
    CAMPAIGN, SEND_CONFIG, LOG_DIR,
)


# === LOGGING ===
os.makedirs(LOG_DIR, exist_ok=True)
log_filename = f"log_{CAMPAIGN['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
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


# === DELAY SENOIDE ===
def sinusoidal_delays(min_d=1, max_d=10):
    """Genera delays senoidales: 1,2,3,...,10,9,...,2,1,2,..."""
    cycle_list = list(range(min_d, max_d + 1)) + list(range(max_d - 1, min_d, -1))
    while True:
        for d in cycle_list:
            yield d


# === QUERY DB ===
def get_target_emails(campaign, db_path):
    """Obtiene emails objetivo segun el target de la campana."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    if campaign["target"] == "buenos_aires_valid":
        query = """
            SELECT l.primary_email
            FROM main m
            JOIN lead l ON m.rowid = l.rowid
            JOIN contact ct ON m.rowid = ct.rowid
            WHERE l.primary_email IS NOT NULL
              AND l.primary_email != ''
              AND ct.deliverability = 'valid'
              AND (m.province = 'Provincia de Buenos Aires'
                   OR m.province = 'Cdad. Autonoma de Buenos Aires'
                   OR m.province LIKE '%Buenos Aires%')
        """
    elif campaign["target"] == "all_valid":
        query = """
            SELECT l.primary_email
            FROM lead l
            JOIN contact ct ON l.rowid = ct.rowid
            WHERE l.primary_email IS NOT NULL
              AND l.primary_email != ''
              AND ct.deliverability = 'valid'
        """
    else:
        raise ValueError(f"Target desconocido: {campaign['target']}")

    c.execute(query)
    emails = [row[0].strip() for row in c.fetchall() if row[0] and row[0].strip()]
    conn.close()
    return emails


# === ENVIO SMTP ===
def send_email(account, to_email, subject, body, bcc_list=None):
    """Envia un email via SMTP_SSL."""
    try:
        msg = MIMEMultipart()
        msg["From"] = account["email"]
        msg["To"] = to_email
        msg["Subject"] = subject

        if bcc_list:
            msg["Bcc"] = ", ".join(bcc_list)

        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.login(account["email"], account["app_password"])
            server.send_message(msg)

        return True
    except Exception as e:
        logger.error(f"[{account['email']}] ERROR: {e}")
        return False


# === TEST MODE ===
def run_test(dry_run=False):
    """Test: envia 1 email por cuenta a si misma, sin BCC."""
    logger.info("=" * 60)
    logger.info("TEST: 1 email por cuenta, sin BCC")
    logger.info(f"Cuentas: {len(ACCOUNTS)}")
    logger.info("=" * 60)

    results = {"exito": 0, "fallo": 0}

    for i, account in enumerate(ACCOUNTS, 1):
        logger.info(f"\n--- Cuenta {i}/{len(ACCOUNTS)}: {account['email']} ---")

        if dry_run:
            logger.info(f"[DRY-RUN] Enviaria email a {account['email']}")
            results["exito"] += 1
            continue

        success = send_email(
            account=account,
            to_email=account["email"],
            subject=f"TEST - {CAMPAIGN['subject']}",
            body=CAMPAIGN["message"],
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


# === CAMPAIGN MODE ===
def run_campaign(dry_run=False):
    """Ejecuta la campana completa con BCC y delay senoide."""
    logger.info("=" * 60)
    logger.info(f"CAMPANA: {CAMPAIGN['title']}")
    logger.info("=" * 60)

    # 1. Consultar emails objetivo
    emails = get_target_emails(CAMPAIGN, DB_PATH)
    logger.info(f"Emails objetivo: {len(emails)}")

    if not emails:
        logger.error("No hay emails objetivo. Abortando.")
        return

    # 2. Dividir entre cuentas (round-robin)
    bcc_size = SEND_CONFIG["bcc_per_email"]
    batches = [emails[i:i + bcc_size] for i in range(0, len(emails), bcc_size)]
    logger.info(f"Lotes totales: {len(batches)} ({bcc_size} BCC c/u)")

    # 3. Calcular tiempo estimado
    avg_delay = (SEND_CONFIG["delay_min"] + SEND_CONFIG["delay_max"]) / 2
    est_minutes = len(batches) * avg_delay
    logger.info(f"Tiempo estimado: {est_minutes:.0f} min ({est_minutes/60:.1f} h)")

    if dry_run:
        logger.info("[DRY-RUN] Simulando envios...")
        for i, batch in enumerate(batches[:5], 1):
            logger.info(f"  Lote {i}: {len(batch)} destinatarios")
        if len(batches) > 5:
            logger.info(f"  ... y {len(batches) - 5} lotes mas")
        return

    # 4. Ejecutar envios
    delay_gen = sinusoidal_delays(SEND_CONFIG["delay_min"], SEND_CONFIG["delay_max"])
    account_cycle = cycle(ACCOUNTS)
    start_time = datetime.now()
    stats = {"enviados": 0, "exitos": 0, "fallos": 0}

    for i, batch in enumerate(batches, 1):
        account = next(account_cycle)

        logger.info(f"\n--- Lote {i}/{len(batches)} ---")
        logger.info(f"Cuenta: {account['email']}")
        logger.info(f"Destinatarios BCC: {len(batch)}")
        logger.info(f"Hora: {datetime.now().strftime('%H:%M:%S')}")

        success = send_email(
            account=account,
            to_email=SEND_CONFIG["to_email"],
            subject=CAMPAIGN["subject"],
            body=CAMPAIGN["message"],
            bcc_list=batch,
        )

        stats["enviados"] += 1
        if success:
            stats["exitos"] += 1
            logger.info(f"[OK] Lote {i} enviado")
        else:
            stats["fallos"] += 1
            logger.error(f"[FALLO] Lote {i} fallo")

        # Delay entre envios
        if i < len(batches):
            delay_min = next(delay_gen)
            delay_sec = delay_min * 60
            next_send = datetime.now() + timedelta(seconds=delay_sec)
            logger.info(f"[WAIT] Proximo envio en {delay_min} min ({next_send.strftime('%H:%M:%S')})")
            time.sleep(delay_sec)

    # 5. Resumen final
    end_time = datetime.now()
    duration = end_time - start_time

    logger.info("\n" + "=" * 60)
    logger.info("RESUMEN CAMPANA")
    logger.info(f"Campana: {CAMPAIGN['title']}")
    logger.info(f"Inicio: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Fin: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Duracion: {duration}")
    logger.info(f"Lotes enviados: {stats['enviados']}")
    logger.info(f"Exitos: {stats['exitos']}")
    logger.info(f"Fallos: {stats['fallos']}")
    logger.info(f"Destinatarios alcanzados: {stats['exitos'] * bcc_size}")
    logger.info(f"Log: {log_path}")
    logger.info("=" * 60)

    return stats


# === MAIN ===
def main():
    parser = argparse.ArgumentParser(description="Campaign Sender")
    parser.add_argument("--test", action="store_true", help="Test: 1 email por cuenta, sin BCC")
    parser.add_argument("--dry-run", action="store_true", help="Simular sin enviar")
    args = parser.parse_args()

    if args.test:
        run_test(dry_run=args.dry_run)
    else:
        run_campaign(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
