import smtplib
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "wwwlanuscomputacion@gmail.com"
SENDER_PASSWORD = "szbm rxyk kodl ilgn"
TO_EMAIL = "selvaggiesteban@gmail.com"

def send_test(number):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = TO_EMAIL
    msg['Subject'] = f"Prueba #{number} - {datetime.now().strftime('%H:%M:%S')}"
    body = f"""Mensaje de prueba #{number}

Hora de envio: {datetime.now().strftime('%H:%M:%S')}
Fecha: Lunes 3 de Agosto 2026
Cuenta: {SENDER_EMAIL}

Este es un email de prueba del sistema de campañas programadas.
"""
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Email #{number} enviado OK")
        return True
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Error: {e}")
        return False

if __name__ == "__main__":
    print("Enviando 3 emails de prueba...")
    for i in range(1, 4):
        send_test(i)
        time.sleep(2)
    print("\nListo! Revisa tu bandeja de selvaggiesteban@gmail.com")
