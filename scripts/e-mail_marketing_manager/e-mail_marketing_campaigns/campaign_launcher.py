import os
import json
import sqlite3
import imaplib
import smtplib
import re
import shutil
import threading
import time
import logging
from email.message import EmailMessage
from itertools import cycle
from pathlib import Path
from dotenv import load_dotenv

# Configuración de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Cargar variables de entorno
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

# CONFIGURACIÓN DE RUTAS
DB_PATH = BASE_DIR / "data" / "inputs" / "contacts.db"
BACKUP_PATH = DB_PATH.with_name("contacts_old.db")

# --- VARIABLES DE CAMPAÑA (Configurables) ---
ASUNTO_CAMPAÑA = "Propuesta de Colaboración Estratégica"
MENSAJE_CAMPAÑA = """Hola, espero que estés bien. Te escribo para presentarte..."""
LISTA_EMAILS = "ejemplo1@gmail.com, ejemplo2@hotmail.com" # Delimitados por coma
LISTA_DOMINIOS = "google.com, linkedin.com" # Delimitados por coma

# --- LÓGICA DE BASE DE DATOS ---

def setup_db():
    """Realiza backup y asegura que las columnas existan."""
    logger.info("Iniciando preparación de base de datos...")
    if DB_PATH.exists():
        shutil.copy2(DB_PATH, BACKUP_PATH)
        logger.info(f"Backup creado en {BACKUP_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verificar columnas
    cursor.execute("PRAGMA table_info(main)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if "Otros_Emails" not in columns:
        cursor.execute("ALTER TABLE main ADD COLUMN Otros_Emails TEXT")
        logger.info("Columna 'Otros_Emails' añadida.")
    
    if "last_sender_account" not in columns:
        cursor.execute("ALTER TABLE main ADD COLUMN last_sender_account TEXT")
        logger.info("Columna 'last_sender_account' añadida.")
        
    conn.commit()
    conn.close()

def update_contact_emails(principal_email, discovered_emails):
    """Actualiza el campo Otros_Emails sin duplicados."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT Otros_Emails FROM main WHERE Email_Principal = ?", (principal_email,))
    row = cursor.fetchone()
    
    existing = set()
    if row and row[0]:
        existing = set(row[0].split(','))
        
    new_emails = set(discovered_emails) - existing - {principal_email}
    
    if new_emails:
        updated = list(existing | new_emails)
        cursor.execute("UPDATE main SET Otros_Emails = ? WHERE Email_Principal = ?", (','.join(updated), principal_email))
        conn.commit()
        
    conn.close()

# --- MOTOR IMAP (EXTRACCIÓN) ---

def extract_emails_from_text(text):
    return re.findall(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+', text.lower())

def imap_worker(account):
    """Extrae contactos de una cuenta específica."""
    try:
        server_addr = account['imap_server']
        user = account['email']
        password = account['password']
        
        logger.info(f"Conectando a IMAP: {user}...")
        mail = imaplib.IMAP4_SSL(server_addr)
        mail.login(user, password)
        mail.select("inbox")
        
        # Buscar correos recientes (últimas 24h para no saturar cada vez, o ALL para primera vez)
        status, messages = mail.search(None, 'ALL')
        if status != 'OK': return
        
        msg_ids = messages[0].split()[-50:] # Procesar los últimos 50 por seguridad en cada ciclo
        
        for msg_id in msg_ids:
            res, msg_data = mail.fetch(msg_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Extraer de cabeceras
                    senders = extract_emails_from_text(msg.get("From", ""))
                    recipients = extract_emails_from_text(msg.get("To", ""))
                    
                    # Extraer del cuerpo si es posible
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode(errors='ignore')
                                break
                    else:
                        body = msg.get_payload(decode=True).decode(errors='ignore')
                    
                    body_emails = extract_emails_from_text(body)
                    
                    # Consolidar y guardar (en este ejemplo simplificado, asociamos al primer remitente)
                    all_found = set(senders + recipients + body_emails)
                    if senders:
                        update_contact_emails(senders[0], list(all_found))
        
        mail.logout()
        logger.info(f"Finalizada extracción IMAP para {user}")
    except Exception as e:
        logger.error(f"Error en IMAP worker ({user}): {e}")

# --- MOTOR SMTP (ENVÍO) ---

def send_email(account, to_email, subject, message):
    """Envía un correo individual."""
    try:
        msg = EmailMessage()
        msg.set_content(message)
        msg["Subject"] = subject
        msg["From"] = account['email']
        msg["To"] = to_email
        
        with smtplib.SMTP_SSL(account['smtp_server'], 465) as smtp:
            smtp.login(account['email'], account['password'])
            smtp.send_message(msg)
        return True
    except Exception as e:
        logger.error(f"Error enviando a {to_email} desde {account['email']}: {e}")
        return False

def campaign_worker(accounts, email_list_str):
    """Gestiona el envío de la campaña con rotación."""
    recipients = [e.strip() for e in email_list_str.split(',') if e.strip()]
    account_pool = cycle(accounts)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for recipient in recipients:
        # 1. Determinar remitente
        cursor.execute("SELECT last_sender_account FROM main WHERE Email_Principal = ?", (recipient,))
        row = cursor.fetchone()
        
        sender_account = None
        if row and row[0]:
            # Intentar encontrar la cuenta configurada que coincida
            sender_account = next((a for a in accounts if a['email'] == row[0]), None)
            
        if not sender_account:
            sender_account = next(account_pool)
            
        # 2. Enviar
        logger.info(f"Enviando campaña a {recipient} desde {sender_account['email']}...")
        success = send_email(sender_account, recipient, ASUNTO_CAMPAÑA, MENSAJE_CAMPAÑA)
        
        if success:
            # 3. Actualizar DB
            cursor.execute("UPDATE main SET last_sender_account = ? WHERE Email_Principal = ?", 
                           (sender_account['email'], recipient))
            conn.commit()
            
    conn.close()
    logger.info("Campaña de Email Marketing finalizada.")

# --- MOTOR FORMULARIOS ---

def forms_worker(domain_list_str):
    """Inicia el procesamiento de formularios usando form_tester."""
    domains = [d.strip() for d in domain_list_str.split(',') if d.strip()]
    if not domains: return
    
    logger.info(f"Iniciando procesamiento de {len(domains)} formularios...")
    try:
        # Importación dinámica para evitar errores si el módulo no está disponible
        from form_tester.src.pipeline_runner import PipelineRunner
        import asyncio
        
        async def run_forms():
            runner = PipelineRunner()
            # Simulamos los objetos necesarios que espera el runner
            from form_tester.src.shared import stats, evidence_logger, FormSubmitter, SMTPSender
            await runner.run(domains, stats, evidence_logger, FormSubmitter(), SMTPSender())
            
        asyncio.run(run_forms())
    except ImportError:
        logger.error("Módulo form_tester no encontrado o incompleto.")
    except Exception as e:
        logger.error(f"Error en motor de formularios: {e}")

# --- ORQUESTADOR PRINCIPAL ---

def main():
    setup_db()
    
    accounts_json = os.getenv("EMAIL_ACCOUNTS")
    if not accounts_json:
        logger.error("No se encontró la variable EMAIL_ACCOUNTS en el .env")
        return
    
    accounts = json.loads(accounts_json)
    
    # 1. Ejecutar Campaña SMTP (Secuencial)
    logger.info("--- INICIANDO FASE 1: CAMPAÑA SMTP ---")
    campaign_worker(accounts, LISTA_EMAILS)
    
    # 2. Ejecutar Extracción IMAP (Secuencial - una cuenta tras otra)
    logger.info("--- INICIANDO FASE 2: EXTRACCIÓN IMAP ---")
    for acc in accounts:
        imap_worker(acc)
        
    # 3. Ejecutar Procesamiento de Formularios (Secuencial)
    logger.info("--- INICIANDO FASE 3: PROCESAMIENTO DE FORMULARIOS ---")
    forms_worker(LISTA_DOMINIOS)
    
    logger.info("--- TODAS LAS TAREAS FINALIZADAS SECUENCIALMENTE ---")

if __name__ == "__main__":
    main()    
    # 1. Ejecutar Campaña SMTP (Secuencial)
    logger.info("--- INICIANDO FASE 1: CAMPAÑA SMTP ---")
    campaign_worker(accounts, LISTA_EMAILS)
    
    # 2. Ejecutar Extracción IMAP (Secuencial - una cuenta tras otra)
    logger.info("--- INICIANDO FASE 2: EXTRACCIÓN IMAP ---")
    for acc in accounts:
        imap_worker(acc)
        
    # 3. Ejecutar Procesamiento de Formularios (Secuencial)
    logger.info("--- INICIANDO FASE 3: PROCESAMIENTO DE FORMULARIOS ---")
    forms_worker(LISTA_DOMINIOS)
    
    logger.info("--- TODAS LAS TAREAS FINALIZADAS SECUENCIALMENTE ---")

if __name__ == "__main__":
    main()
