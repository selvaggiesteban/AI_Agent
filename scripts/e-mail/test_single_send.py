import smtplib
import sys
from email.mime.text import MIMEText
from datetime import datetime

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "wwwlanuscomputacion@gmail.com"
SENDER_PASSWORD = "szbm rxyk kodl ilgn"
TO_EMAIL = "selvaggiesteban@gmail.com"
SUBJECT = "prueba"
BODY = "prueba"

def test_single_send():
    """Prueba envío de un solo email para verificar credenciales."""
    print(f"Probando envío SMTP...")
    print(f"Desde: {SENDER_EMAIL}")
    print(f"Hacia: {TO_EMAIL}")
    print(f"Asunto: {SUBJECT}")
    print(f"Servidor: {SMTP_SERVER}:{SMTP_PORT}")
    print("-" * 40)
    
    try:
        msg = MIMEText(BODY, 'plain', 'utf-8')
        msg['From'] = SENDER_EMAIL
        msg['To'] = TO_EMAIL
        msg['Subject'] = SUBJECT
        msg['Date'] = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
        
        print("Conectando a Gmail SMTP...")
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            print("Autenticando...")
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            print("Enviando mensaje...")
            server.send_message(msg)
        
        print("\n[OK] Email enviado correctamente")
        print(f"Revisa la bandeja de entrada de {TO_EMAIL}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"\n[ERROR] Autenticacion: {e}")
        print("Verifica que la contrasena de aplicacion sea correcta")
        return False
    except smtplib.SMTPException as e:
        print(f"\n[ERROR] SMTP: {e}")
        return False
    except Exception as e:
        print(f"\n[ERROR] Inesperado: {e}")
        return False

if __name__ == "__main__":
    success = test_single_send()
    sys.exit(0 if success else 1)
