"""
RPA WhatsApp Web - Envío escalonado de mensajes
Lee config.json con números, mensaje y delays.
"""

import time
import random
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException,
)


# ========================== CONFIGURACIÓN ==========================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

MENSAJE = config["mensaje"]
NUMEROS = config["numeros"]
DELAY_MIN = config.get("delay_min", 1)
DELAY_MAX = config.get("delay_max", 10)
PATTERN = "ascending_descending"

WHATSAPP_URL = "https://web.whatsapp.com"


# ========================== FUNCIONES ==========================

def create_driver():
    """Crea el driver de Chrome con la sesión existente."""
    options = Options()
    # Permite reutilizar la sesión de Chrome existente
    options.add_argument("--user-data-dir=C:\\Users\\Esteban Selvaggi\\AppData\\Local\\Google\\Chrome\\User Data")
    options.add_argument("--profile-directory=Default")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    # Suprimir mensajes de automatización
    options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"},
    )
    return driver


def wait_for_whatsapp(driver, timeout=60):
    """Espera a que WhatsApp Web cargue completamente."""
    print("[*] Esperando que WhatsApp Web cargue...")
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[contenteditable="true"][data-tab="10"]'))
        )
        print("[+] WhatsApp Web listo.")
        return True
    except TimeoutException:
        print("[-] Timeout: WhatsApp Web no cargó a tiempo.")
        return False


def search_contact(driver, phone_number):
    """Busca un contacto por número en el buscador de WhatsApp Web."""
    print(f"[*] Buscando contacto: {phone_number}")

    try:
        # Click en el buscador de chats
        search_box = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'div[contenteditable="true"][data-tab="10"]')
            )
        )
        search_box.click()
        time.sleep(0.5)

        # Limpiar campo y escribir número
        search_box.clear()
        time.sleep(0.3)
        search_box.send_keys(phone_number)
        time.sleep(2)  # Esperar resultados de búsqueda

        # Verificar si apareció el contacto
        try:
            # Buscar el primer resultado en el panel de chats
            result = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, f'//span[@title="{phone_number}"]/ancestor::div[@role="listitem"]')
                )
            )
            result.click()
            print(f"[+] Contacto encontrado: {phone_number}")
            time.sleep(1)
            return True

        except TimeoutException:
            # Intentar buscar con formato alternativo
            try:
                result = driver.find_element(
                    By.XPATH,
                    f'//div[contains(@class, "_ak1r")]//span[contains(text(), "{phone_number}")]'
                )
                result.click()
                print(f"[+] Contacto encontrado (formato alternativo): {phone_number}")
                time.sleep(1)
                return True
            except NoSuchElementException:
                print(f"[-] No se encontró el contacto: {phone_number}")
                return False

    except Exception as e:
        print(f"[-] Error al buscar contacto: {e}")
        return False


def open_chat_by_url(driver, phone_number):
    """Abre chat directamente por URL (alternativa más confiable)."""
    url = f"https://web.whatsapp.com/send?phone={phone_number}"
    print(f"[*] Abriendo chat por URL: {url}")
    driver.get(url)
    time.sleep(3)

    # Verificar si se cargó el chat
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div[contenteditable="true"][data-tab="10"]')
            )
        )
        print(f"[+] Chat abierto para {phone_number}")
        return True
    except TimeoutException:
        print(f"[-] No se pudo abrir chat para {phone_number}")
        return False


def send_message(driver, message):
    """Escribe y envía un mensaje en el chat activo."""
    print(f"[*] Enviando mensaje: {message[:50]}...")

    try:
        # Localizar el campo de mensaje
        msg_box = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, 'div[contenteditable="true"][data-tab="10"]')
            )
        )
        msg_box.click()
        time.sleep(0.5)

        # Escribir mensaje
        msg_box.send_keys(message)
        time.sleep(0.5)

        # Enviar con Enter
        msg_box.send_keys(Keys.ENTER)
        time.sleep(1)

        print("[+] Mensaje enviado correctamente.")
        return True

    except (TimeoutException, NoSuchElementException) as e:
        print(f"[-] Error al enviar mensaje: {e}")
        return False


def calculate_delays(count):
    """
    Patrón: 1,2,3,4,5,6,7,8,9,10,9,8,7,6,5,4,3,2,1,2,3...
    Sube de 1 a 10, baja a 1, vuelve a subir, repite.
    """
    if count <= 1:
        return [0]

    delays = []
    step = 1
    direction = 1

    for i in range(count):
        delays.append(float(step))

        if step >= DELAY_MAX:
            direction = -1
        elif step <= DELAY_MIN:
            direction = 1

        step += direction

    return delays


def run_rpa():
    """Función principal del RPA."""
    print("=" * 60)
    print("  RPA WhatsApp Web - Envío Escalonado de Mensajes")
    print("=" * 60)
    print(f"  Números a contactar: {len(NUMEROS)}")
    print(f"  Mensaje: {MENSAJE[:60]}...")
    print(f"  Delay: {DELAY_MIN}min → {DELAY_MAX}min → {DELAY_MIN}min")
    print("=" * 60)

    # Calcular delays
    delays = calculate_delays(len(NUMEROS))
    total_time = sum(delays)

    print(f"\n[*] Patrón de delays (minutos): {delays}")
    print(f"[*] Tiempo total estimado: {total_time:.1f} min ({total_time/60:.1f} hrs)")
    print()

    driver = None

    try:
        # Crear driver
        driver = create_driver()
        driver.get(WHATSAPP_URL)

        # Esperar carga
        if not wait_for_whatsapp(driver):
            print("\n[!] ASEGÚRATE de tener WhatsApp Web abierto en Chrome.")
            print("[!] O ejecuta Chrome con: chrome.exe --remote-debugging-port=9222")
            input("\nPresiona Enter para reintentar...")
            driver.quit()
            return

        print(f"\n[*] Iniciando envíos a {len(NUMEROS)} contactos...\n")

        for i, phone in enumerate(NUMEROS):
            print(f"\n{'─' * 50}")
            print(f"  [{i+1}/{len(NUMEROS)}] Contacto: {phone}")
            print(f"{'─' * 50}")

            # Buscar y abrir chat (por URL es más confiable)
            if open_chat_by_url(driver, phone):
                time.sleep(2)

                # Enviar mensaje
                send_message(driver, MENSAJE)
                print(f"[+] ✓ Enviado a {phone}")
            else:
                print(f"[-] ✗ No se pudo enviar a {phone}")

            # Esperar delay (excepto después del último)
            if i < len(NUMEROS) - 1:
                wait_minutes = delays[i]
                wait_seconds = wait_minutes * 60
                print(f"\n[*] Esperando {wait_minutes:.1f} min antes del siguiente envío...")
                time.sleep(wait_seconds)

        print("\n" + "=" * 60)
        print("  ✓ TODOS LOS MENSAJES ENVIADOS EXITOSAMENTE")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\n[!] RPA detenido por el usuario.")
    except Exception as e:
        print(f"\n[!] Error inesperado: {e}")
    finally:
        if driver:
            input("\nPresiona Enter para cerrar el navegador...")
            driver.quit()


# ========================== PUNTO DE ENTRADA ==========================

if __name__ == "__main__":
    run_rpa()
