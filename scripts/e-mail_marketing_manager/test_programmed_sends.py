import smtplib
import time
import math
import logging
import sys
import os
import schedule
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

# === LOGGING ===
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logs", "campaigns")
os.makedirs(LOG_DIR, exist_ok=True)

log_filename = f"log_programmed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
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

def send_email_smtp(msg):
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"Error SMTP: {e}")
        return False

def create_message(hour):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = TO_EMAIL
    msg['Subject'] = f"{SUBJECT} - Programado {hour}:00"
    body = f"""{BODY}

---
Programado para: {hour}:00 - Lunes 3/Agosto/2026
Enviado desde: {SENDER_EMAIL}
"""
    msg.attach(MIMEText(body, 'plain'))
    return msg

def send_at_hour(hour):
    def job():
        logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] Enviando email programado para {hour}:00")
        msg = create_message(hour)
        success = send_email_smtp(msg)
        if success:
            logger.info(f"[OK] Email enviado a las {datetime.now().strftime('%H:%M:%S')}")
        else:
            logger.error(f"[FALLO] No se pudo enviar a las {datetime.now().strftime('%H:%M:%S')}")
    return job

def main():
    logger.info("=" * 60)
    logger.info("PROGRAMANDO ENVIOS PARA LUNES 3/AGOSTO/2026")
    logger.info(f"Cuenta: {SENDER_EMAIL}")
    logger.info(f"Destino: {TO_EMAIL}")
    logger.info(f"Horario: 7:00 - 13:00")
    logger.info("=" * 60)
    
    for hour in range(7, 14):
        schedule.every().monday.at(f"{hour:02d}:00").do(send_at_hour(hour))
        logger.info(f"Programado: Lunes {hour}:00")
    
    logger.info("\nEsperando horarios de envio...")
    logger.info("Presiona Ctrl+C para detener")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(30)
    except KeyboardInterrupt:
        logger.info("\nPrograma detenido por el usuario")

if __name__ == "__main__":
    main()
