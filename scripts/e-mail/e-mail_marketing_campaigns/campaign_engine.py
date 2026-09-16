import os
import sqlite3
import smtplib
import time
import threading
import logging
import json
import re
import urllib.parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
logger = logging.getLogger(__name__)

# RUTA ACTUALIZADA A LA FUENTE REAL
DB_PATH = "data/inputs/contacts.db"

# --- MÉTODOS ORIGINALES ---

def get_unprocessed_from_db(limit=100):
    """Extrae emails y dominios no procesados de la DB."""
    if not os.path.exists(DB_PATH):
        logger.error(f"Base de datos no encontrada en {DB_PATH}")
        return [], []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    emails, domains = [], []
    try:
        cursor.execute("SELECT primary_email FROM main WHERE (smtp_processed IS NULL OR smtp_processed = '0') AND primary_email IS NOT NULL LIMIT ?", (limit,))
        emails = [r[0] for r in cursor.fetchall()]
        
        cursor.execute("SELECT urls FROM main WHERE (form_processed IS NULL OR form_processed = '0') AND urls IS NOT NULL LIMIT ?", (limit,))
        domains = [r[0] for r in cursor.fetchall()]
    except Exception as e:
        logger.error(f"Error consultando DB: {e}")
        
    conn.close()
    return emails, domains

def mark_processed(email=None, domain=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if email:
        cursor.execute("UPDATE main SET smtp_processed = '1' WHERE primary_email = ?", (email,))
    if domain:
        cursor.execute("UPDATE main SET form_processed = '1' WHERE urls = ?", (domain,))
    conn.commit()
    conn.close()

def run_smtp_logic(emails):
    print(f"[*] Procesando {len(emails)} correos vía SMTP...")
    for email in emails:
        mark_processed(email=email)
        time.sleep(0.1) 

def run_form_logic(domains):
    print(f"[*] Procesando {len(domains)} dominios vía Formularios...")
    for domain in domains:
        mark_processed(domain=domain)
        time.sleep(0.1)

def run_campaign():
    print("=== CENTRAL Marketing Automation: INICIANDO CAMPAÑA DUAL ===")
    emails, domains = get_unprocessed_from_db(limit=500)
    
    t1 = threading.Thread(target=run_smtp_logic, args=(emails,))
    t2 = threading.Thread(target=run_form_logic, args=(domains,))
    
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print("=== CAMPAÑA FINALIZADA ===")

# --- LÓGICA CONSOLIDADA DE SADD (EXTRACCIÓN, FILTRADO Y MAPEO) ---

class CampaignConfigurator:
    @staticmethod
    def get_contacted_emails_from_logs(log_dir="logs/campaigns"):
        """Analiza logs históricos para crear una lista negra de correos ya impactados."""
        contacted = set()
        if not os.path.exists(log_dir):
            return contacted
        email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
        for filename in os.listdir(log_dir):
            if filename.startswith("log_") and filename.endswith(".txt"):
                try:
                    with open(os.path.join(log_dir, filename), "r", encoding="utf-8", errors="ignore") as f:
                        found = email_pattern.findall(f.read())
                        for email in found:
                            contacted.add(email.lower().strip())
                except Exception:
                    pass
        return contacted

    @staticmethod
    def extract_by_keywords(target_keywords, output_file, spanish_countries=None, exclude_patterns=None):
        """Extrae contactos vírgenes filtrando por sector/palabras clave y países."""
        if not spanish_countries:
            spanish_countries = ['españa', 'argentina', 'chile', 'uruguay', 'paraguay', 'bolivia', 'méxico', 'colombia', 'perú', 'ecuador']
        if not exclude_patterns:
            exclude_patterns = ['sentry', 'wixpress', 'noreply', 'abuse']
            
        contacted_emails = CampaignConfigurator.get_contacted_emails_from_logs()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        where_kw = [f"sector LIKE '%{kw}%'" for kw in target_keywords] + [f"title LIKE '%{kw}%'" for kw in target_keywords]
        where_country = ["country = 'N/D'", "country IS NULL", "country = ''"] + [f"country LIKE '%{c}%'" for c in spanish_countries]
        
        query = f"SELECT primary_email, other_emails FROM main WHERE ({' OR '.join(where_kw)}) AND ({' OR '.join(where_country)}) AND (campaigns IS NULL OR campaigns = '')"
        cursor.execute(query)
        
        selected = []
        for row in cursor.fetchall():
            emails = []
            if row[0]: emails.append(row[0])
            if row[1]: emails.extend([e for e in re.split(r'[,;|\s]+', row[1]) if '@' in e])
            
            for raw_email in emails:
                email = urllib.parse.unquote(raw_email).strip(' ,;').split()[0].lower()
                if re.match(r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}", email) and not any(p in email for p in exclude_patterns) and email not in contacted_emails:
                    selected.append(email)
        
        unique = sorted(list(set(selected)))
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(unique) + "\n")
        conn.close()
        return len(unique)

    @staticmethod
    def extract_corporate_batch(input_file, output_file, batch_size=500, skip=0):
        """Filtra dominios genéricos y extrae un lote corporativo (Batching)."""
        generic = {'gmail.com', 'hotmail.com', 'yahoo.com', 'outlook.com', 'live.com', 'icloud.com', 'speedy.com.ar', 'fibertel.com.ar'}
        
        with open(input_file, 'r', encoding='utf-8') as f:
            all_emails = sorted([line.strip().lower() for line in f if line.strip()], reverse=True)
            
        corp_emails = []
        count = 0
        for email in all_emails:
            if email.split('@')[-1] not in generic:
                count += 1
                if count > skip:
                    corp_emails.append(email)
                    if len(corp_emails) >= batch_size:
                        break
                        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(corp_emails) + "\n")
        return len(corp_emails)

    @staticmethod
    def generate_identity_map(list_file, map_file, single_account=None):
        """Genera el mapa JSON para balancear carga entre cuentas o forzar una cuenta única."""
        with open(list_file, "r", encoding="utf-8") as f:
            contacts = [line.strip() for line in f if line.strip()]
            
        if single_account:
            emails = [single_account]
        else:
            accounts_json = os.getenv("EMAIL_ACCOUNTS", "[]")
            emails = [acc['email'] for acc in json.loads(accounts_json)]
            
        if not emails:
            raise ValueError("No accounts available for mapping.")
            
        identity_map = {c: emails[i % len(emails)] for i, c in enumerate(contacts)}
        
        with open(map_file, "w", encoding="utf-8") as f:
            json.dump(identity_map, f, indent=2)
        return len(identity_map)

if __name__ == "__main__":
    run_campaign()
