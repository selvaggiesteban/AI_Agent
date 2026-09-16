"""
campaign_sender_retry_fallos.py — Reintento de contactos fallidos AMBA 4-ago + BA-CABA 3-ago.

Identifica en contacts.db los contactos que figuro como [FALLO] en los logs
log_amba_20260804_103719.txt y log_ba_ciclo_20260803_135251.txt, los filtra
por:
  - Ya enviados en otra campana (presencia en campaign o en logs [OK])
  - deliverability invalid/blacklisted
  - Corruptos / formato invalido / placeholders
y los reenvia uno a uno (sin BCC) con delay senoidal 1-10-1 min entre email.

Uso (miercoles 5 de agosto, tarde, despues de las 16:33 cuando venza
la rolling 24h window del retry 16:11):

    cd scripts/e-mail_marketing_manager
    python campaign_sender_retry_fallos.py
    python campaign_sender_retry_fallos.py --dry-run    # solo lista, no envia
"""

import smtplib
import time
import sqlite3
import logging
import sys
import os
import re
import glob
import argparse
from datetime import datetime, timedelta
from email.mime.text import MIMEText

from accounts_config import (
    ACCOUNTS, DB_PATH, SMTP_SERVER, SMTP_PORT,
    CAMPAIGN, SEND_CONFIG, LOG_DIR,
)

os.makedirs(LOG_DIR, exist_ok=True)
log_filename = f"log_retry_fallos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
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


LIST_VAL = "RETRY-FALLOS-05082026"
CAMPAIGN_TYPE = "retry_servicio_tecnico"

JUNK_PATTERNS = [
    r"%20",
    r"\.png", r"\.jpg", r"\.jpeg", r"\.gif",
    r"cropped-", r"recurso-",
    r"@2x", r"@3x",
    r"\.comhttp", r"\.arlin", r"\.comr",
    r"username@", r"correo@", r"^u003e",
    r"^m@cyrv\.yn$", r"^f@faisalman\.com$",
    r"@domain\.com", r"@website\.com",
    r"@example\.com", r"@test\.com", r"@email\.com",
]


def get_already_sent_all():
    """Lee todos los logs de campaign y retorna set de emails con [OK]."""
    sent = set()
    for pattern in [
        "log_amba_*.txt",
        "log_ba_ciclo_*.txt",
        "log_lanus_cycle_*.txt",
        "log_national_*.txt",
        "log_retry_fallos_*.txt",
    ]:
        for filepath in glob.glob(os.path.join(LOG_DIR, pattern)):
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        if "[OK]" in line:
                            parts = line.strip().split("[OK]")
                            if len(parts) == 2:
                                email = parts[1].strip().lower()
                                if "@" in email:
                                    sent.add(email)
            except Exception:
                pass
    return sent


def get_failed_from_logs():
    """Extrae emails unicos que figuran como [FALLO] en los logs de intento."""
    failed = set()
    target_logs = [
        "log_amba_20260804_103719.txt",
        "log_ba_ciclo_20260803_135251.txt",
    ]
    for fname in target_logs:
        filepath = os.path.join(LOG_DIR, fname)
        if not os.path.exists(filepath):
            logger.warning(f"Log no encontrado: {filepath}")
            continue
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if "[FALLO]" in line:
                    m = re.search(r"\[FALLO\]\s+(.+?)\s*$", line)
                    if m:
                        email = m.group(1).strip()
                        if "@" in email:
                            failed.add(email)
    return failed


def is_corrupt(email):
    """True si el email tiene patrones de basura/scraping."""
    for p in JUNK_PATTERNS:
        if re.search(p, email, re.IGNORECASE):
            return True
    if len(email) < 7 or len(email) > 80:
        return True
    return False


def get_retry_eligible(failed, already_sent):
    """
    Toma el set de failed y consulta la DB. Retorna lista de tuplas
    (rowid, primary_email) que:
      - No estan en already_sent
      - No estan en taboo (corruptos)
      - No tienen campaign previa
      - deliverability IN (valid, pending, generic, NULL)
    """
    if not failed:
        return []
    failed_clean = [e for e in failed if not is_corrupt(e)]
    logger.info(f"Fallos unicos totales: {len(failed)}")
    logger.info(f"Fallos tras descartar corruptos: {len(failed_clean)}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    placeholders = ",".join(["?"] * len(failed_clean))
    q = f"""
        SELECT l.rowid, l.primary_email, c.deliverability,
               (SELECT COUNT(*) FROM campaign cp
                  WHERE cp.contact_rowid = l.rowid) AS c_count
        FROM lead l
        LEFT JOIN contact c ON c.rowid = l.rowid
        WHERE l.primary_email IN ({placeholders})
        ORDER BY l.rowid
    """
    cur.execute(q, failed_clean)
    db_rows = cur.fetchall()
    conn.close()

    logger.info(f"Encontrados en DB: {len(db_rows)}")

    eligible = []
    for rowid, email, deliv, c_count in db_rows:
        lower = email.lower()
        if lower in already_sent:
            logger.info(f"[SKIP-OK] {email} ya tuvo [OK] en otra campana")
            continue
        if c_count > 0:
            logger.info(f"[SKIP-CAMPAIGN] {email} tiene {c_count} entradas en campaign")
            continue
        if deliv and deliv.lower() in ("invalid", "blacklisted", "smtp_fail"):
            logger.info(f"[SKIP-DELIV] {email} deliverability={deliv}")
            continue
        eligible.append((rowid, email))
    return eligible


def sinusoidal_delays():
    """Generador de delays senoidales: 1,2,3,...,10,9,...,2,1 (simetrico, 19 steps)."""
    cycle_list = list(range(1, 11)) + list(range(9, 0, -1))
    while True:
        for d in cycle_list:
            yield d


def send_individual(account, to_email, subject, body):
    """Envia email individual (sin BCC) con MIMEText."""
    try:
        msg = MIMEText(body, "plain", "utf-8")
        msg["From"] = account["email"]
        msg["To"] = to_email
        msg["Subject"] = subject
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.login(account["email"], account["app_password"])
            server.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"[{account['email']}] ERROR SMTP: {e}")
        return False


def enrich_campaign_db(eligible, account_used):
    """Inserta rows en campaign table con list_val=RETRY-FALLOS-05082026."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    today = datetime.now().strftime("%d/%m/%Y")
    inserted = 0
    for rowid, email in eligible:
        try:
            cur.execute("""
                INSERT INTO campaign
                  (contact_rowid, title, list_val, subject, sender,
                   date, type, campaign_id, email_used, message)
                VALUES (?, ?, ?, ?, ?, ?, ?, NULL, ?, ?)
            """, (
                rowid,
                CAMPAIGN["title"],
                LIST_VAL,
                CAMPAIGN["subject"],
                account_used,
                today,
                CAMPAIGN_TYPE,
                email,
                CAMPAIGN["message"],
            ))
            inserted += 1
        except Exception as e:
            logger.error(f"[DB] Fila {rowid} no insertada: {e}")
    conn.commit()
    conn.close()
    logger.info(f"[DB] {inserted} filas insertadas en campaign (list_val={LIST_VAL})")
    return inserted


def main():
    parser = argparse.ArgumentParser(description="Reintento de fallos AMBA/BA-CABA")
    parser.add_argument("--dry-run", action="store_true",
                        help="Solo lista los targets, no envia")
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("REINTENTO DE FALLOS - AMBA 4-ago + BA-CABA 3-ago")
    logger.info(f"Lista: {LIST_VAL}")
    logger.info(f"Tipo:  {CAMPAIGN_TYPE}")
    logger.info(f"Hora inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    failed = get_failed_from_logs()
    already_sent = get_already_sent_all()
    eligible = get_retry_eligible(failed, already_sent)

    logger.info(f"A reintentar: {len(eligible)} emails")
    if not eligible:
        logger.info("No hay emails pendientes para reenviar. Fin.")
        return

    for i, (rowid, email) in enumerate(eligible, 1):
        logger.info(f"  [{i:02d}] rowid={rowid} {email}")

    if args.dry_run:
        logger.info("[DRY-RUN] No se envia. Fin.")
        return

    # 15 emails: distribuir entre primeras cuentas (capacidad libre: tarde 5 ago,
    # ventana 24h desde retry 16:11 ya expira a las 16:33 del 5/8).
    # Usamos solo 1 cuenta para evitar problemas (15 emails = 15 recipients).
    primary_account = ACCOUNTS[0]
    delay_gen = sinusoidal_delays()

    logger.info("=" * 60)
    logger.info(f"Cuenta emisora: {primary_account['email']}")
    logger.info(f"Total envios individuales: {len(eligible)}")
    logger.info("=" * 60)

    stats = {"exito": 0, "fallo": 0}
    sent_rowids = []
    start_time = datetime.now()

    for i, (rowid, email) in enumerate(eligible, 1):
        logger.info(f"[{primary_account['email']}] [{i}/{len(eligible)}] Enviando a {email}")
        ok = send_individual(
            account=primary_account,
            to_email=email,
            subject=CAMPAIGN["subject"],
            body=CAMPAIGN["message"],
        )
        if ok:
            stats["exito"] += 1
            sent_rowids.append(rowid)
            logger.info(f"[{primary_account['email']}] [OK] {email}")
        else:
            stats["fallo"] += 1
            logger.error(f"[{primary_account['email']}] [FALLO] {email}")
        if i < len(eligible):
            delay_min = next(delay_gen)
            next_send = datetime.now() + timedelta(seconds=delay_min * 60)
            logger.info(f"[WAIT] Próximo en {delay_min} min ({next_send.strftime('%H:%M:%S')})")
            time.sleep(delay_min * 60)

    end_time = datetime.now()
    duration = end_time - start_time

    # Enriquecer DB solo con los OK
    if sent_rowids:
        sent_eligible = [(r, e) for r, e in eligible if r in sent_rowids]
        enrich_campaign_db(sent_eligible, primary_account["email"])

    logger.info("\n" + "=" * 60)
    logger.info("REINTENTO COMPLETADO")
    logger.info(f"Inicio: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Fin:    {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Duracion: {duration}")
    logger.info(f"Exitos: {stats['exito']}")
    logger.info(f"Fallos: {stats['fallo']}")
    logger.info(f"Log: {log_path}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
