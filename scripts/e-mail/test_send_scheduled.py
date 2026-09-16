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
START_HOUR = 7
END_HOUR = 13
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
    """Genera delay senoide entre 1 y 10 minutos.
    Patrón: 1,2,3,4,5,6,7,8,9,10,9,8,7,6,5,4,3,2,1,2,3,..."""
    cycle = list(range(MIN_DELAY, MAX_DELAY + 1)) + list(range(MAX_DELAY - 1, MIN_DELAY, -1))
    while True:
        for d in cycle:
            yield d

# === ENVIO SMTP ===
def send_email_smtp(msg):
    """Envía un email via SMTP_SSL."""
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"Error SMTP: {e}")
        return False

def create_batch_message(batch_recipients, batch_num, total_batches):
    """Crea un mensaje MIME con destinatario propio y BCC para el lote."""
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = SENDER_EMAIL
    msg['Subject'] = f"{SUBJECT} (Lote {batch_num}/{total_batches})"
    
    bcc_str = ", ".join(batch_recipients)
    msg['Bcc'] = bcc_str
    
    body_with_info = f"""{BODY}

---
Lote {batch_num}/{total_batches}
Destinatarios BCC: {len(batch_recipients)}
Enviado desde: {SENDER_EMAIL}
Fecha/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
    msg.attach(MIMEText(body_with_info, 'plain'))
    return msg

def calculate_batches(total_contacts, batch_size):
    """Calcula el número total de lotes."""
    return math.ceil(total_contacts / batch_size)

def is_within_schedule():
    """Verifica si estamos dentro del horario programado."""
    now = datetime.now()
    return START_HOUR <= now.hour < END_HOUR

# === MAIN ===
def run_scheduled_sends():
    """Ejecuta envíos programados con delay senoide."""
    logger.info("=" * 60)
    logger.info("INICIANDO SISTEMA DE ENVÍOS PROGRAMADOS")
    logger.info(f"Cuenta: {SENDER_EMAIL}")
    logger.info(f"Destino: {TO_EMAIL}")
    logger.info(f"Asunto: {SUBJECT}")
    logger.info(f"Horario: {START_HOUR}:00 - {END_HOUR}:00")
    logger.info(f"Delay: {MIN_DELAY}-{MAX_DELAY} min (senoide)")
    logger.info("=" * 60)
    
    # Calcular lotes
    total_batches = calculate_batches(BATCH_SIZE, BATCH_SIZE)
    
    # Crear lista de destinatarios BCC (para prueba, usamos emails ficticios)
    # En producción, estos vendrían de contacts.db
    test_recipients = [f"test{i}@example.com" for i in range(BATCH_SIZE)]
    
    delay_gen = sinusoidal_delay()
    batch_count = 0
    start_time = datetime.now()
    
    logger.info(f"Iniciando envíos a las {start_time.strftime('%H:%M:%S')}")
    logger.info(f"Lotes programados: {total_batches}")
    
    while is_within_schedule():
        batch_count += 1
        current_batch = test_recipients[:BATCH_SIZE]
        
        logger.info(f"\n--- LOTE {batch_count}/{total_batches} ---")
        logger.info(f"Hora actual: {datetime.now().strftime('%H:%M:%S')}")
        logger.info(f"Destinatarios BCC: {len(current_batch)}")
        
        # Crear mensaje
        msg = create_batch_message(current_batch, batch_count, total_batches)
        
        # Enviar
        success = send_email_smtp(msg)
        
        if success:
            logger.info(f"[OK] Lote {batch_count} enviado exitosamente")
        else:
            logger.error(f"[FALLO] Lote {batch_count} fallo")
        
        # Calcular próximo delay
        if batch_count < total_batches:
            delay_min = next(delay_gen)
            delay_sec = delay_min * 60
            
            next_send = datetime.now() + timedelta(seconds=delay_sec)
            logger.info(f"[WAIT] Proximo envio en {delay_min} min ({next_send.strftime('%H:%M:%S')})")
            
            # Esperar
            time.sleep(delay_sec)
        else:
            logger.info("[DONE] Todos los lotes procesados")
            break
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("\n" + "=" * 60)
    logger.info("RESUMEN DE EJECUCIÓN")
    logger.info(f"Inicio: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Fin: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Duración: {duration}")
    logger.info(f"Lotes enviados: {batch_count}")
    logger.info(f"Log: {log_path}")
    logger.info("=" * 60)

if __name__ == "__main__":
    run_scheduled_sends()
