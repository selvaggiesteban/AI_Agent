import os
import json
import base64
import pickle
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText

# === CONFIGURACION ===
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data', 'credentials', 'google', 'client_secret_997721949653-lb4ofpob473p7bsh0kluohgukls4rbd3.apps.googleusercontent.com.json')
TOKEN_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'token.pickle')
SENDER_EMAIL = "wwwlanuscomputacion@gmail.com"
TO_EMAIL = "selvaggiesteban@gmail.com"
SUBJECT = "prueba"
BODY = "prueba"

def get_gmail_service():
    """Obtiene el servicio de Gmail API con OAuth2."""
    creds = None
    
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                print(f"Error: No se encontro {CLIENT_SECRETS_FILE}")
                print("Descarga las credenciales de Google Cloud Console:")
                print("1. Ve a https://console.cloud.google.com")
                print("2. Crea un proyecto o selecciona uno existente")
                print("3. Habilita la Gmail API")
                print("4. Crea credenciales OAuth 2.0 (Tipo: Aplicacion de escritorio)")
                print("5. Descarga el JSON como 'credentials.json' en esta carpeta")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)

def schedule_send(service, send_time):
    """Programa un envio para la hora especificada."""
    message = MIMEText(BODY, 'plain', 'utf-8')
    message['To'] = TO_EMAIL
    message['From'] = SENDER_EMAIL
    message['Subject'] = f"{SUBJECT} - Programado {send_time.strftime('%H:%M')}"
    
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    
    body = {
        'raw': raw,
        'sendAt': send_time.isoformat() + 'Z'
    }
    
    result = service.users().messages().send(
        userId='me',
        body=body
    ).execute()
    
    return result

def main():
    print("=" * 60)
    print("GMAIL SCHEDULER - Programar envios")
    print("=" * 60)
    print()
    
    service = get_gmail_service()
    if not service:
        return
    
    print("Servicio de Gmail API conectado.")
    print()
    
    # Programar envios para Lunes 3/Agosto de 7:00 a 13:00
    target_date = datetime(2026, 8, 3)  # Lunes 3 de agosto
    
    print(f"Programando envios para: {target_date.strftime('%A %d/%m/%Y')}")
    print(f"Horario: 7:00 - 13:00")
    print()
    
    scheduled = []
    for hour in range(7, 14):
        send_time = target_date.replace(hour=hour, minute=0, second=0)
        
        try:
            result = schedule_send(service, send_time)
            print(f"[OK] Programado: {send_time.strftime('%H:%M')} - ID: {result.get('id', 'N/A')}")
            scheduled.append((send_time, result))
        except Exception as e:
            print(f"[ERROR] {send_time.strftime('%H:%M')}: {e}")
    
    print()
    print(f"Total programados: {len(scheduled)}")
    print("Revisa la seccion 'Programados' en Gmail")

if __name__ == "__main__":
    main()
