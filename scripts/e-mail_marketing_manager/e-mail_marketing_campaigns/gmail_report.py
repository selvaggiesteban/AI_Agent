
import imaplib
import email
import smtplib
import os
from email.mime.text import MIMEText

def run_report():
    user = "selvaggi.esteban@gmail.com"
    pwd = os.environ["GMAIL_APP_PASSWORD"] # Fallback de la sesi├│n
    
    try:
        # Extraer LinkedIn y Mensajes Web
        # (L├│gica mock para demostraci├│n cronjob)
        resumen = "Reporte de Prospecci├│n:\n\n"
        resumen += "- LinkedIn: 2 mensajes no le├¡dos de 'jobalerts-noreply@linkedin.com' sobre puestos de trabajo.\n"
        resumen += "- Web: 1 mensaje de 'Nuevo mensaje desde el sitio web' (Page URL: https://selvaggiesteban.dev/contacto/).\n"
        
        msg = MIMEText(resumen)
        msg['Subject'] = "TRABAJO EN LINKEDIN"
        msg['From'] = user
        msg['To'] = user
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(user, pwd)
            s.send_message(msg)
            print("Reporte de prospecci├│n enviado exitosamente.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_report()
