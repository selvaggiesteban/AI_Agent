import csv
import json
import os
from datetime import datetime

# Directorio de los CSVs
TRABAJO_DIR = r"C:\Users\Esteban Selvaggi\Desktop\subagent-driven_development\Trabajo"

# Archivo de salida
OUTPUT_FILE = os.path.join(TRABAJO_DIR, "trabajo_data.json")

def read_csv(filename):
    """Lee un CSV y retorna una lista de diccionarios"""
    filepath = os.path.join(TRABAJO_DIR, filename)
    if not os.path.exists(filepath):
        print(f"  [WARN] Archivo no encontrado: {filename}")
        return []
    
    rows = []
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Limpiar claves vacías
            cleaned = {k.strip(): v.strip() if v else None for k, v in row.items() if k and k.strip()}
            if cleaned:
                rows.append(cleaned)
    return rows

def safe_int(value, default=0):
    """Convierte un string a int, manejando separadores de miles"""
    if not value:
        return default
    # Remover puntos de separadores de miles y convertir
    cleaned = str(value).replace(".", "")
    try:
        return int(cleaned)
    except ValueError:
        return default

def parse_campañas(rows):
    """Parsea el CSV de campañas"""
    campanas = []
    for row in rows:
        campana = {
            "titulo": row.get("Título"),
            "cobertura_geografica": row.get("Cobertura geográfica"),
            "lista": row.get("Lista"),
            "asunto": row.get("Asunto"),
            "fecha": row.get("Fecha"),
            "mensaje": row.get("Mensaje"),
            "estado": row.get("Estado"),
            "emails_enviados": safe_int(row.get("Emails enviados")),
            "contactos_unicos": safe_int(row.get("Contactos únicos")),
            "fallos": safe_int(row.get("Fallos")),
            "duracion": row.get("Duración"),
            "cuentas_usadas": safe_int(row.get("Cuentas usadas")),
            "enriched": row.get("Enriched"),
            "log_file": row.get("Log file")
        }
        campanas.append(campana)
    return campanas

def parse_chat(rows):
    """Parsea el CSV de chat"""
    chats = []
    for row in rows:
        chat = {
            "id": row.get("ID"),
            "canal": row.get("Canal"),
            "lista": row.get("Lista"),
            "mensaje": row.get("Mensaje"),
            "remitente": row.get("Remitente"),
            "destinatario": row.get("Destinatario"),
            "respuesta": row.get("Respuesta"),
            "fecha_hora": row.get("Fecha / Hora"),
            "estado": row.get("Estado")
        }
        chats.append(chat)
    return chats

def safe_float(value, default=0.0):
    """Convierte un string a float, manejando separadores de miles"""
    if not value:
        return default
    # Remover puntos de separadores de miles y convertir
    cleaned = str(value).replace(".", "")
    try:
        return float(cleaned) / 1000 if len(cleaned) > 6 else float(cleaned)
    except ValueError:
        return default

def parse_cobertura(rows):
    """Parsea el CSV de cobertura geográfica"""
    coberturas = []
    for row in rows:
        cobertura = {
            "order": safe_int(row.get("order")),
            "id": row.get("id"),
            "desc": row.get("desc"),
            "north": safe_float(row.get("north")),
            "west": safe_float(row.get("west")),
            "south": safe_float(row.get("south")),
            "east": safe_float(row.get("east")),
            "cells": safe_int(row.get("cells")),
            "queries": row.get("queries"),
            "density": safe_int(row.get("density"))
        }
        coberturas.append(cobertura)
    return coberturas

def parse_control_horario(rows):
    """Parsea el CSV de control horario"""
    horarios = []
    for row in rows:
        horario = {
            "precio": int(row.get("Precio", 0) or 0),
            "servicio": row.get("Servicio"),
            "fecha": row.get("Fecha"),
            "horas": {}
        }
        horas_cols = ["9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]
        for h in horas_cols:
            horario["horas"][h] = row.get(h, "FALSE") == "TRUE"
        horarios.append(horario)
    return horarios

def parse_emails(rows):
    """Parsea el CSV de emails"""
    emails = []
    for row in rows:
        email = {
            "proveedor": row.get("Proveedor"),
            "usuario": row.get("Usuario"),
            "contraseña": row.get("Contraseña"),
            "contraseña_aplicacion": row.get("Contraseña de Aplicación"),
            "oauth_client_id": row.get("ID de cliente de OAuth")
        }
        emails.append(email)
    return emails

def parse_ia(rows):
    """Parsea el CSV de IA"""
    ia_data = []
    for row in rows:
        agent_full = row.get("AI_Agent", "")
        # Separar agente y email
        parts = agent_full.split(" ", 1)
        agente = parts[0] if parts else agent_full
        email = parts[1] if len(parts) > 1 else ""
        
        semanas = {}
        for k, v in row.items():
            if k and k.startswith("Semana"):
                semanas[k] = v == "TRUE"
        
        ia_entry = {
            "agente": agente,
            "email": email,
            "semanas": semanas
        }
        ia_data.append(ia_entry)
    return ia_data

def parse_keywords(rows):
    """Parsea el CSV de keywords"""
    return [row.get("keyword", list(row.values())[0] if row else "") for row in rows if row]

def parse_objetivos(rows):
    """Parsea el CSV de objetivos"""
    objetivos = []
    for row in rows:
        objetivo = {
            "mes_anio": row.get("Mes / Año"),
            "dias_habiles": int(row.get("Días Hábiles", 0) or 0),
            "ipc": row.get("IPC"),
            "precio_sesion": int(row.get("Precio por Sesión", 0) or 0),
            "sesiones_disponibles": int(row.get("Sesiones Disponibles", 0) or 0),
            "sesiones_vendidas_objetivo": int(row.get("Sesiones Vendidas (Objetivo)", 0) or 0),
            "ganancias": row.get("Ganancias")
        }
        objetivos.append(objetivo)
    return objetivos

def parse_paginas_web(rows):
    """Parsea el CSV de páginas web"""
    paginas = []
    for row in rows:
        pagina = {
            "sitio": row.get("Sitio"),
            "keyword": row.get("Keyword"),
            "cobertura_geografica": row.get("Cobertura geográfica"),
            "campana": row.get("Campaña"),
            "url_es": row.get("URL_ES"),
            "url_en": row.get("URL_EN"),
            "links_enviados": row.get("Links enviados"),
            "sesiones_vendidas_objetivo": row.get("Sesiones Vendidas (Objetivo)"),
            "fecha_hora": row.get("Fecha / Hora")
        }
        paginas.append(pagina)
    return paginas

def parse_scrap(rows):
    """Parsea el CSV de scraping"""
    scraps = []
    for row in rows:
        scrap = {
            "titulo": row.get("Título"),
            "cobertura_geografica": row.get("Cobertura geográfica"),
            "keywords": row.get("Keywords"),
            "fecha": row.get("Fecha"),
            "estado": row.get("Estado"),
            "rows": int(row.get("Rows", 0) or 0),
            "emails_unicos": int(row.get("E-mails únicos", 0) or 0),
            "ubicacion": row.get("Ubicación"),
            "duracion": row.get("Duración"),
            "log_file": row.get("Log File")
        }
        scraps.append(scrap)
    return scraps

def main():
    print("=" * 60)
    print("CONVERSOR CSV -> JSON")
    print("=" * 60)
    
    # Leer todos los CSVs
    print("\n[1/10] Leyendo TRABAJO - CAMPAÑAS.csv...")
    campanas_raw = read_csv("TRABAJO - CAMPAÑAS.csv")
    print(f"  -> {len(campanas_raw)} filas")
    
    print("[2/10] Leyendo TRABAJO - CHAT.csv...")
    chat_raw = read_csv("TRABAJO - CHAT.csv")
    print(f"  -> {len(chat_raw)} filas")
    
    print("[3/10] Leyendo TRABAJO - COBERTURA GEOGRAFICA.csv...")
    cobertura_raw = read_csv("TRABAJO - COBERTURA GEOGRÁFICA.csv")
    print(f"  -> {len(cobertura_raw)} filas")
    
    print("[4/10] Leyendo TRABAJO - CONTROL HORARIO.csv...")
    horario_raw = read_csv("TRABAJO - CONTROL HORARIO.csv")
    print(f"  -> {len(horario_raw)} filas")
    
    print("[5/10] Leyendo TRABAJO - E-MAILS.csv...")
    emails_raw = read_csv("TRABAJO - E-MAILS.csv")
    print(f"  -> {len(emails_raw)} filas")
    
    print("[6/10] Leyendo TRABAJO - IA.csv...")
    ia_raw = read_csv("TRABAJO - IA.csv")
    print(f"  -> {len(ia_raw)} filas")
    
    print("[7/10] Leyendo TRABAJO - KEYWORDS.csv...")
    keywords_raw = read_csv("TRABAJO - KEYWORDS.csv")
    print(f"  -> {len(keywords_raw)} filas")
    
    print("[8/10] Leyendo TRABAJO - OBJETIVOS.csv...")
    objetivos_raw = read_csv("TRABAJO - OBJETIVOS.csv")
    print(f"  -> {len(objetivos_raw)} filas")
    
    print("[9/10] Leyendo TRABAJO - PAGINAS WEB.csv...")
    paginas_raw = read_csv("TRABAJO - PÁGINAS WEB.csv")
    print(f"  -> {len(paginas_raw)} filas")
    
    print("[10/10] Leyendo TRABAJO - SCRAP.csv...")
    scrap_raw = read_csv("TRABAJO - SCRAP.csv")
    print(f"  -> {len(scrap_raw)} filas")
    
    # Parsear cada sección
    print("\nParseando datos...")
    data = {
        "metadata": {
            "fecha_generacion": datetime.now().isoformat(),
            "fuente": "TRABAJO - 10 CSVs",
            "total_campanas": len(campanas_raw),
            "total_chats": len(chat_raw),
            "total_coberturas": len(cobertura_raw),
            "total_horarios": len(horario_raw),
            "total_emails_cuenta": len(emails_raw),
            "total_agentes_ia": len(ia_raw),
            "total_keywords": len(keywords_raw),
            "total_objetivos": len(objetivos_raw),
            "total_paginas_web": len(paginas_raw),
            "total_scraps": len(scrap_raw)
        },
        "campanas": parse_campañas(campanas_raw),
        "chat": parse_chat(chat_raw),
        "cobertura_geografica": parse_cobertura(cobertura_raw),
        "control_horario": parse_control_horario(horario_raw),
        "emails_cuentas": parse_emails(emails_raw),
        "agentes_ia": parse_ia(ia_raw),
        "keywords": parse_keywords(keywords_raw),
        "objetivos": parse_objetivos(objetivos_raw),
        "paginas_web": parse_paginas_web(paginas_raw),
        "scraping": parse_scrap(scrap_raw)
    }
    
    # Guardar JSON
    print(f"\nGuardando JSON en: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # Resumen
    file_size = os.path.getsize(OUTPUT_FILE)
    print("\n" + "=" * 60)
    print("COMPLETADO")
    print("=" * 60)
    print(f"Archivo: {OUTPUT_FILE}")
    print(f"Tamaño: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print(f"\nSecciones:")
    print(f"  - campañas:            {len(data['campanas'])} registros")
    print(f"  - chat:                {len(data['chat'])} registros")
    print(f"  - cobertura_geografica:{len(data['cobertura_geografica'])} registros")
    print(f"  - control_horario:     {len(data['control_horario'])} registros")
    print(f"  - emails_cuentas:      {len(data['emails_cuentas'])} registros")
    print(f"  - agentes_ia:          {len(data['agentes_ia'])} registros")
    print(f"  - keywords:            {len(data['keywords'])} registros")
    print(f"  - objetivos:           {len(data['objetivos'])} registros")
    print(f"  - paginas_web:         {len(data['paginas_web'])} registros")
    print(f"  - scraping:            {len(data['scraping'])} registros")

if __name__ == "__main__":
    main()