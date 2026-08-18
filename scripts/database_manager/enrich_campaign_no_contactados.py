import sqlite3
import re
from datetime import datetime

DB_PATH = 'C:\\Users\\Esteban Selvaggi\\Desktop\\subagent-driven_development\\data\\inputs\\contacts.db'
LOG_PATH = 'C:\\Users\\Esteban Selvaggi\\Desktop\\subagent-driven_development\\logs\\campaigns\\log_no_contactados_20260810_102646.txt'

# Extraer emails del log
with open(LOG_PATH, 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

pattern = r'\[OK\]\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
emails = re.findall(pattern, content)
emails = list(set(e.lower().strip() for e in emails))
print(f'Emails únicos: {len(emails)}')

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

CAMPAIGN_ID = 'no_contactados_20260810'
CAMPAIGN_TITLE = 'No Contactados - Servicio Tecnico'
SUBJECT = 'Servicio Tecnico de Computadoras y Productos de Tecnologia'
SENDER_ACCOUNTS = [
    'wwwlanuscomputacion@gmail.com',
    'adrianaavila131969@gmail.com',
    'fernando1141967@gmail.com',
    'selvaggiesteban9@gmail.com',
    'selvaggiesteban4@gmail.com',
    'selvaggiesteban11@gmail.com',
    'marketing1a1oficial@gmail.com',
    'selvaggiconsultores@gmail.com',
    'estebanmfwd@gmail.com',
    'selvaggiesteban1@gmail.com',
    'selvaggiesteban2@gmail.com',
    'marcelagomez7799@gmail.com',
]

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
updated = 0
inserted = 0

for email in emails:
    # Buscar ROWID en lead
    c.execute('SELECT ROWID FROM lead WHERE primary_email = ?', (email,))
    row = c.fetchone()
    if row:
        rowid = row[0]
        # Actualizar contact: smtp_processed='1', sender=cuenta rotativa
        sender = SENDER_ACCOUNTS[updated % len(SENDER_ACCOUNTS)]
        c.execute('UPDATE contact SET smtp_processed = \"1\", sender = ? WHERE ROWID = ?', (sender, rowid))
        if c.rowcount > 0:
            updated += 1
        
        # Insertar en campaign
        c.execute('''
            INSERT INTO campaign (contact_rowid, title, list_val, subject, sender, date, type, campaign_id, email_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (rowid, CAMPAIGN_TITLE, 'no_contactados_valid', SUBJECT, sender, now, 'email', CAMPAIGN_ID, sender))
        inserted += 1

conn.commit()
conn.close()
print(f'Contactos actualizados: {updated}')
print(f'Registros campaign insertados: {inserted}')