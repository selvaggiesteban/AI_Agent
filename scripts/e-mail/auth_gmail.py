import os
import json
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CLIENT_SECRETS_FILE = os.path.join(SCRIPT_DIR, 'credentials.json')
TOKEN_FILE = os.path.join(SCRIPT_DIR, 'token.pickle')

def authenticate():
    """Autentica con Gmail API y guarda el token."""
    if not os.path.exists(CLIENT_SECRETS_FILE):
        print(f"Error: No se encontro {CLIENT_SECRETS_FILE}")
        print("Guarda tu archivo JSON de credenciales como 'credentials.json' en esta carpeta:")
        print(SCRIPT_DIR)
        return False

    print("Iniciando flujo de autenticacion OAuth2...")
    print()

    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, SCOPES)
    
    # Usar run_console para obtener URL manualmente
    creds = flow.run_console()
    
    with open(TOKEN_FILE, 'wb') as token:
        pickle.dump(creds, token)
    
    print()
    print("Autenticacion exitosa!")
    print(f"Token guardado en: {TOKEN_FILE}")
    return True

if __name__ == "__main__":
    authenticate()
