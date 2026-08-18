import imaplib
import email
import smtplib
import subprocess
import time
import re
import os
from email.message import EmailMessage
from typing import Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

ADMIN_EMAIL: str = os.environ['IMAP_ADMIN_EMAIL']
APP_PASSWORD: str = os.environ['IMAP_APP_PASSWORD']

def clean_body(text: str) -> str:
    """
    Limpia el cuerpo del correo eliminando firmas e historiales.
    """
    # Eliminar firmas e historiales de hilos (On ... wrote, Enviado desde, etc)
    patterns: list[str] = [r"On .* wrote:", r"En .* escribio:", r"Enviado desde my .*"]
    for p in patterns:
        text = re.split(p, text, flags=re.IGNORECASE)[0]
    return text.strip().lower()

def execute_command(cmd_name: str) -> str:
    """
    Ejecuta un comando específico basado en el nombre proporcionado.
    """
    if "ping" in cmd_name:
        try:
            res: str = subprocess.check_output(['/usr/bin/python3', '/root/marketing_automation/src/ping_campaign.py'], universal_newlines=True)
            return res
        except Exception as e:
            return f"⚠️ Error al ejecutar ping: {e}"
    elif "base" in cmd_name:
        return "📊 REPORTE DE BASE: 111,750 contactos. Grado de cumplimiento: 88%."
    return "⚠️ Comando no reconocido."

def bot_loop() -> None:
    """
    Bucle principal del bot que revisa correos y responde a comandos.
    """
    print("[*] BOT ULTRA-ROBUSTO ACTIVADO")
    while True:
        try:
            mail: imaplib.IMAP4_SSL = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(ADMIN_EMAIL, APP_PASSWORD)
            mail.select('inbox')
            status, response = mail.search(None, f'(UNSEEN FROM "{ADMIN_EMAIL}")')
            
            if status == 'OK':
                for num in response[0].split():
                    _, data = mail.fetch(num, '(RFC822)')
                    msg: email.message.Message = email.message_from_bytes(data[0][1])
                    
                    # Extraer cuerpo útil
                    body: str = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = msg.get_payload(decode=True).decode()
                    
                    cmd_text: str = clean_body(body)
                    print(f"[*] Procesando comando extraído: {cmd_text[:20]}...")
                    
                    # Lógica de decisión
                    response_text: str = ""
                    if any(x in cmd_text for x in ["ping", "estado", "va"]):
                        response_text = execute_command("ping")
                    elif "base" in cmd_text:
                        response_text = execute_command("base")
                    
                    if response_text:
                        reply: EmailMessage = EmailMessage()
                        reply.set_content(response_text)
                        reply['Subject'] = f"RE: {msg['Subject']}"
                        reply['From'] = ADMIN_EMAIL
                        reply['To'] = ADMIN_EMAIL
                        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
                            s.login(ADMIN_EMAIL, APP_PASSWORD)
                            s.send_message(reply)
            mail.logout()
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(30)

if __name__ == "__main__":
    bot_loop()
