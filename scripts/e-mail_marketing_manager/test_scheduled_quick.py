import smtplib
import time
import math
import logging
import sys
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# === CONFIGURACION ===
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "wwwlanuscomputacion@gmail.com"
SENDER_PASSWORD = "szbm rxyk kodl ilgn"
TO_EMAIL = "selvaggiesteban@gmail.com"
SUBJECT = "prueba"
BODY = "prueba"
BATCH_SIZE = 50
MIN_DELAY = 1
MAX_DELAY = 10

# === LOGGING ===
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs", "campaigns")
os.makedirs(LOG_DIR, exist_ok=True)

log_filename = f"log_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
log_path = os.path.join(LOG_DIR, log_filename)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_path, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# === DELAY SENOIDE ===
def sinusoidal_delay():
    """Genera delay senoide entre 1 y 10 minutos."""
    cycle = list(range(MIN_DELAY, MAX_DELAY + 1)) + list(range(MAX_DELAY - 1, MIN_DELAY, -1))
    while True:
        for d in cycle:
            yield d

# === ENVIO SMTP ===
def send_email_smtp(msg):
    """Envia un email via SMTP_SSL."""
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"Error SMTP: {e}")
        return False

def create_batch_message(batch_num, total_batches):
    """Crea un mensaje MIME con destinatario propio y BCC."""
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = SENDER_EMAIL
    msg['Subject'] = f"{SUBJECT} (Lote {batch_num}/{total_batches})"
    
    test_recipients = [TO_EMAIL] * BATCH_SIZE
    bcc_str = ", ".join(test_recipients)
    msg['Bcc'] = bcc_str
    
    body_with_info = f"""{BODY}

---
Lote {batch_num}/{total_batches}
Destinatarios BCC: {len(test_recipients)}
Enviado desde: {SENDER_EMAIL}
Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    msg.attach(MIMEText(body_with_info, 'plain'))
    return msg

# === MAIN ===
def run_test():
    """Ejecuta 3 lotes de prueba con delay senoide."""
    total_batches = 3
    
    logger.info("=" * 60)
    logger.info("TEST: ENVIOS CON DELAY SENOIDE")
    logger.info(f"Cuenta: {SENDER_EMAIL}")
    logger.info(f"Destino: {TO_EMAIL}")
    logger.info(f"Lotes: {total_batches}")
    logger.info(f"Delay: {MIN_DELAY}-{MAX_DELAY} min (senoide)")
    logger.info("=" * 60)
    
    delay_gen = sinusoidal_delay()
    start_time = datetime.now()
    
    for batch_count in range(1, total_batches + 1):
        logger.info(f"\n--- LOTE {batch_count}/{total_batches} ---")
        logger.info(f"Hora actual: {datetime.now().strftime('%H:%M:%S')}")
        
        msg = create_batch_message(batch_count, total_batches)
        success = send_email_smtp(msg)
        
        if success:
            logger.info(f"[OK] Lote {batch_count} enviado")
        else:
            logger.error(f"[FALLO] Lote {batch_count} fallo")
        
        if batch_count < total_batches:
            delay_min = next(delay_gen)
            delay_sec = delay_min * 60
            next_send = datetime.now() + timedelta(seconds=delay_sec)
            logger.info(f"[WAIT] Proximo envio en {delay_min} min ({next_send.strftime('%H:%M:%S')})")
            time.sleep(delay_sec)
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("\n" + "=" * 60)
    logger.info("RESUMEN DEL TEST")
    logger.info(f"Inicio: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Fin: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Duracion: {duration}")
    logger.info(f"Lotes enviados: {total_batches}")
    logger.info(f"Log: {log_path}")
    logger.info("=" * 60)

if __name__ == "__main__":
    run_test()
