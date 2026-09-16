import sqlite3
import imaplib
import email
import re
from config.settings import ACCOUNTS

from core.paths import INPUTS_DIR
db_path = INPUTS_DIR / "contacts.db"

def get_unknown_leads():
    # 1. Obtener todos los emails registrados en la DB (Principal y Otros)
    registered_emails = set()
    registered_domains = set()
    
    # Lista de mis propias cuentas para omitirlas
    my_emails = {acc[0].lower() for acc in ACCOUNTS}
    my_emails.add("selvaggi.esteban@gmail.com") # Asegurar tu principal

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT Email_Principal, Otros_Emails FROM main")
        for row in cursor.fetchall():
            if row[0]: 
                registered_emails.add(row[0].lower())
                domain = row[0].lower().split('@')[-1]
                registered_domains.add(domain)
            if row[1]:
                # Procesar lista de otros emails si están separados por comas
                others = [e.strip().lower() for e in row[1].split(',')]
                for e in others: 
                    registered_emails.add(e)
                    if '@' in e: registered_domains.add(e.split('@')[-1])
        conn.close()
    except Exception as e:
        print(f"Error leyendo DB: {e}")
        return

    # 2. Buscar en bandejas de entrada emails que NO estén en registered_emails y NO sean mios
    unknown_leads = {} # {email: domain}

    for email_addr, password in ACCOUNTS:
        try:
            imap_host = "imap.hostinger.com" if any(x in email_addr for x in ["lanuscomputacion", "selvaggiesteban.dev"]) else "imap.gmail.com"
            mail = imaplib.IMAP4_SSL(imap_host)
            mail.login(email_addr, password)
            mail.select("INBOX", readonly=True)
            
            status, messages = mail.search(None, 'ALL')
            if status == 'OK':
                msg_ids = messages[0].split()
                # Revisar últimos 300 para encontrar gente nueva
                for msg_id in msg_ids[-300:]:
                    try:
                        _, data = mail.fetch(msg_id, "(RFC822)")
                        msg = email.message_from_bytes(data[0][1])
                        sender_raw = msg.get("From", "").lower()
                        sender_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', sender_raw)
                        
                        if sender_match:
                            sender_email = sender_match.group(1)
                            domain = sender_email.split('@')[-1]
                            
                            # FILTROS:
                            # 1. No es mía
                            # 2. No está en la DB
                            # 3. No es Mailer Daemon / Sistema
                            if (sender_email not in my_emails and 
                                sender_email not in registered_emails and 
                                "mailer-daemon" not in sender_email and 
                                "googlemail.com" not in sender_email and
                                "noreply" not in sender_email and
                                "notifications" not in sender_email):
                                
                                # Si el dominio coincide con algo de la DB pero el mail es nuevo, es muy valioso
                                is_domain_match = domain in registered_domains
                                unknown_leads[sender_email] = "Coincidencia de Dominio" if is_domain_match else "Nuevo Externo"
                    except: continue
            mail.logout()
        except: continue

    print("\n--- LEADS DETECTADOS NO REGISTRADOS EN LA BASE DE DATOS ---")
    if not unknown_leads:
        print("No se encontraron leads externos nuevos en los mensajes recientes.")
    else:
        for email_lead, source in unknown_leads.items():
            print(f"[{source}] {email_lead}")
    print("----------------------------------------------------------\n")

if __name__ == "__main__":
    get_unknown_leads()
