import os
import time
import smtplib
import imaplib
import email
import json
import threading
import datetime
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import logging

# Cargar variables de entorno
load_dotenv()

# Rutas configurables
BASE_DIR = os.getcwd()
LOG_DIR = os.path.join(BASE_DIR, "logs", "campaigns")
MESSAGE_PATH = os.getenv("MESSAGE", os.path.join(BASE_DIR, "scripts", "templates", "mensaje_seguimiento.md"))
if not os.path.isabs(MESSAGE_PATH):
    MESSAGE_PATH = os.path.join(BASE_DIR, MESSAGE_PATH)


# CAMBIO DINÁMICO: Detectar si es Argentina o España según variables de entorno
LIST_FILE = os.getenv("CONTACT_LIST_FILE", "spain_followup_29052026.txt")
MAP_FILE = os.getenv("IDENTITY_MAP_FILE", "identity_map.json")

CONTACT_LIST_PATH = os.path.join(LOG_DIR, LIST_FILE)
IDENTITY_MAP_PATH = os.path.join(LOG_DIR, MAP_FILE)

CAMPAIGN_ID = os.getenv("CAMPAIGN_ID", "29052026")
SUBJECT = "Buenos días"

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_filename = f"log_{CAMPAIGN_ID}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
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

SMTP_ACCOUNTS = []
accounts_json = os.getenv("EMAIL_ACCOUNTS")
if accounts_json:
    SMTP_ACCOUNTS = json.loads(accounts_json)

stats = {"enviadas": 0, "entregados": 0, "errores": 0}
stats_lock = threading.Lock()

def get_delays():
    cycle = list(range(1, 11)) + list(range(9, 1, -1))
    while True:
        for d in cycle: yield d

def send_email(account, recipient, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'], msg['To'], msg['Subject'] = account['email'], recipient, subject
        msg.attach(MIMEText(body, 'plain'))
        smtp_server = account.get('smtp_server', 'smtp.gmail.com')
        with smtplib.SMTP_SSL(smtp_server, 465, timeout=30) as server:
            server.login(account['email'], account['password'])
            server.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"[{account['email']}] ERROR enviando a {recipient}: {e}")
        return False

def worker(account, all_contacts, campaign_message):
    delay_gen = get_delays()
    identity_map = {}
    if os.path.exists(IDENTITY_MAP_PATH):
        with open(IDENTITY_MAP_PATH, "r", encoding="utf-8") as f:
            identity_map = json.load(f)
    
    my_contacts = [c for c in all_contacts if identity_map.get(c.lower()) == account['email'].lower()]
    if not my_contacts:
        logger.info(f"[{account['email']}] Sin contactos asignados. Hilo terminado.")
        return
        
    logger.info(f"[{account['email']}] Hilo iniciado con {len(my_contacts)} contactos.")
    for i, contact in enumerate(my_contacts):
        success = send_email(account, contact, SUBJECT, campaign_message)
        with stats_lock:
            stats["enviadas"] += 1
            if success: stats["entregados"] += 1
            else: stats["errores"] += 1
        
        status = "EXITO" if success else "FALLO"
        logger.info(f"[{account['email']}] [{status}] {contact}")
        
        if i < len(my_contacts) - 1:
            delay = next(delay_gen)
            logger.info(f"[{account['email']}] Esperando {delay} min antes del siguiente...")
            time.sleep(delay * 60)

if __name__ == "__main__":
    try:
        if not os.path.exists(MESSAGE_PATH):
            raise FileNotFoundError(f"No se encuentra la plantilla: {MESSAGE_PATH}")
        if not os.path.exists(CONTACT_LIST_PATH):
            raise FileNotFoundError(f"No se encuentra la lista de contactos: {CONTACT_LIST_PATH}")

        with open(MESSAGE_PATH, 'r', encoding='utf-8') as f:
            campaign_message = f.read()
        with open(CONTACT_LIST_PATH, 'r', encoding='utf-8') as f:
            all_contacts = [line.strip() for line in f if line.strip()]
        
        logger.info(f"=== CAMPAÑA {CAMPAIGN_ID} INICIADA ===")
        logger.info(f"Archivo de contactos: {LIST_FILE}")
        logger.info(f"Objetivo: {len(all_contacts)} contactos usando {len(SMTP_ACCOUNTS)} cuentas.")
        
        threads = []
        for acc in SMTP_ACCOUNTS:
            t = threading.Thread(target=worker, args=(acc, all_contacts, campaign_message))
            t.start()
            threads.append(t)
            
        for t in threads:
            t.join()
            
        logger.info(f"=== CAMPAÑA FINALIZADA ===")
        logger.info(f"Enviados: {stats['enviadas']} | Entregados: {stats['entregados']} | Errores: {stats['errores']}")
        
    except Exception as e:
        logger.error(f"FALLO CRÍTICO: {e}")
