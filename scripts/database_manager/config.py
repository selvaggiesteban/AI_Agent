"""
config.py — Configuración centralizada para scripts de enriquecimiento
Rutas, reglas y constantes del sistema de contacts.db
"""

import os

# === RAÍZ DEL PROYECTO ===
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# === BASE DE DATOS ===
DB_PATH = os.path.join(PROJECT_ROOT, "data", "inputs", "contacts.db")

# === DIRECTORIOS DE FUENTES DE DATOS ===
SOURCES = {
    # Gosom output
    "gosom_general": os.path.join(PROJECT_ROOT, "data", "inputs", "gosom", "output", "general"),
    "gosom_rrhh": os.path.join(PROJECT_ROOT, "data", "inputs", "gosom", "output", "rrhh"),
    "gosom_output_root": os.path.join(PROJECT_ROOT, "data", "inputs", "gosom", "output"),
    "gosom_webdata": os.path.join(PROJECT_ROOT, "data", "inputs", "gosom", "output", "webdata"),

    # Contacts (fuentes principales)
    "contacts_root": os.path.join(PROJECT_ROOT, "data", "inputs", "contacts"),
    "contacts_google": os.path.join(PROJECT_ROOT, "data", "inputs", "contacts", "Contactos old", "contactos_google"),
    "contacts_brevo": os.path.join(PROJECT_ROOT, "data", "inputs", "contacts", "Contactos old", "contactos_brevo"),
    "contacts_mailrelay": os.path.join(PROJECT_ROOT, "data", "inputs", "contacts", "Contactos old", "contactos_mailrelay"),
    "contacts_tvmas": os.path.join(PROJECT_ROOT, "data", "inputs", "contacts", "Contactos old", "contactos_tvmas"),
    "contacts_tvmas_backup": os.path.join(PROJECT_ROOT, "data", "inputs", "contacts", "Contactos old", "contactos_tvmas", "backup_fuentes"),
    "contactos_old": os.path.join(PROJECT_ROOT, "data", "inputs", "contacts", "Contactos old"),

    # Scraping antiguo
    "scrap_bbdd": os.path.join(PROJECT_ROOT, "data", "inputs", "contacts", "Contactos old", "scrap", "bbdd"),
    "scrap_backup": os.path.join(PROJECT_ROOT, "data", "inputs", "contacts", "Contactos old", "scrap", "backup_fuentes"),

    # Nuevas carpetas (copias de trabajo)
    "nueva_carpeta": os.path.join(PROJECT_ROOT, "data", "inputs", "contacts", "Nueva carpeta"),
    "nueva_carpeta_2": os.path.join(PROJECT_ROOT, "data", "inputs", "contacts", "Nueva carpeta (2)"),

    # WhatsApp
    "whatsapp_vcards": os.path.join(PROJECT_ROOT, "data", "inputs", "whatsapp_backup", "WhatsApp", "vCards"),

    # Campaña
    "campana": os.path.join(PROJECT_ROOT, "data", "inputs", "contacts", "Contactos old", "campaña"),
}

# === LOGS ===
LOG_DIR = os.path.join(PROJECT_ROOT, "data", "inputs", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# === SCHEMA VERSION ===
SCHEMA_VERSION = 4

# === COLUMNAS POR TABLA (v4 normalizada) ===
TABLES = {
    "main": ["id", "title", "sector", "address", "city", "province", "country", "entity_type"],
    "lead": ["primary_email", "secondary_emails", "website", "google_maps", "phone",
             "facebook", "instagram", "messenger", "whatsapp", "linkedin", "telegram", "x", "youtube"],
    "contact": ["sender", "deliverability", "email_last_response", "last_validation_date",
                "last_validation_status", "last_subject_received", "smtp_processed", "form_processed", "date_added"],
    "campaign": ["contact_rowid", "title", "list_val", "subject", "sender", "date", "type", "campaign_id", "email_used"],
}

# === ARCHIVOS A IGNORAR (no son contactos) ===
IGNORE_FILES = {
    "buffer.txt",  # Credenciales
    "domains.csv",  # Lista dominios
    "results.csv",  # Verificación dominios
    "falta_total.txt",  # URLs
    "dashboard.html",  # HTML
    "calendario_editorial_2026.xlsx",  # Calendario
    "google_maps_scraper-1.10.2-windows-amd64.exe",  # Binario
    "test_ascii.csv", "test_ascii.xlsx", "test_direct.csv",  # Pruebas
    "jobs.db", "jobs.db-shm", "jobs.db-wal",  # DB interna scraper
    "powercfg.txt",  # Config
}

# === ARCHIVOS DE BLACKLIST ===
BLACKLIST_SOURCES = [
    os.path.join(PROJECT_ROOT, "data", "inputs", "contacts", "Contactos old", "CONTACTOS RECHAZADOS.docx"),
]
