"""
RPA WhatsApp Web - Envío escalonado de mensajes
Lee config.json con números, mensaje y delays.
"""

import time
import sys
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# ========================== CONFIGURACION ==========================

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

MENSAJE = config["mensaje"]
NUMEROS = config["numeros"]
DELAY_MIN = config.get("delay_min", 1)
DELAY_MAX = config.get("delay_max", 10)
START_INDEX = config.get("start_index", 0)

SELECTOR_INPUT = '[data-testid="conversation-compose-box-input"]'


# ========================== FUNCIONES ==========================

def create_driver():
    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    try:
        driver = webdriver.Chrome(options=options)
        print("[+] Conectado a Chrome.")
        return driver
    except Exception as e:
        print(f"[-] Error: {e}")
        sys.exit(1)


def close_popups(driver):
    for sel in [
        '[data-testid="confirm-popup"] [data-testid="popup-controls-close"]',
        '[data-testid="popup-controls-close"]',
    ]:
        try:
            el = driver.find_element(By.CSS_SELECTOR, sel)
            el.click()
            print("[*] Popup cerrado.")
            time.sleep(1)
            return True
        except:
            pass
    return False


def wait_for_whatsapp(driver, timeout=30):
    print("[*] Esperando WhatsApp Web...")
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="chat-list"]'))
        )
        print("[+] WhatsApp Web listo.")
        close_popups(driver)
        return True
    except TimeoutException:
        print("[-] WhatsApp Web no cargo.")
        return False


def open_chat(driver, phone_number):
    url = f"https://web.whatsapp.com/send?phone={phone_number}"
    print(f"[*] Abriendo chat: {phone_number}")
    driver.get(url)
    time.sleep(5)

    close_popups(driver)

    try:
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTOR_INPUT))
        )
        print(f"[+] Chat listo: {phone_number}")
        return True
    except TimeoutException:
        try:
            error = driver.find_element(
                By.XPATH, '//*[contains(text(), "no es v") or contains(text(), "invalid") or contains(text(), "not found")]'
            )
            print(f"[-] Numero invalido: {phone_number}")
        except NoSuchElementException:
            print(f"[-] Chat no cargo: {phone_number}")
        driver.get("https://web.whatsapp.com")
        time.sleep(3)
        return False


def send_message(driver, message):
    try:
        msg_box = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTOR_INPUT))
        )
        msg_box.click()
        time.sleep(0.3)
        msg_box.send_keys(message)
        time.sleep(0.5)
        msg_box.send_keys(Keys.ENTER)
        time.sleep(1)
        print("[+] Mensaje enviado.")
        return True
    except Exception as e:
        print(f"[-] Error al enviar: {e}")
        return False


def calculate_delays(count):
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


def run():
    print("=" * 60)
    print("  RPA WhatsApp Web - Envio Escalonado")
    print("=" * 60)
    print(f"  Contactos: {len(NUMEROS)}")
    print(f"  Delay: {DELAY_MIN}min -> {DELAY_MAX}min -> {DELAY_MIN}min")

    delays = calculate_delays(len(NUMEROS))
    total = sum(delays)
    print(f"  Tiempo estimado: {total:.1f} min ({total/60:.1f} hrs)")
    print("=" * 60)

    driver = create_driver()

    if not wait_for_whatsapp(driver):
        input("\nInicie sesion y presione Enter...")
        if not wait_for_whatsapp(driver):
            print("[-] No se pudo cargar WhatsApp.")
            return

    remaining = NUMEROS[START_INDEX:]
    delays = calculate_delays(len(remaining))
    exitosos = 0
    fallidos = 0

    for i, phone in enumerate(remaining):
        idx = START_INDEX + i
        print(f"\n--- [{idx+1}/{len(NUMEROS)}] {phone} ---")

        if open_chat(driver, phone):
            time.sleep(1)
            if send_message(driver, MENSAJE):
                exitosos += 1
                print(f"[+] Enviado: {phone}")
            else:
                fallidos += 1
                print(f"[-] Fallo envio: {phone}")
        else:
            fallidos += 1
            print(f"[-] Fallo chat: {phone}")

        if i < len(remaining) - 1:
            wait = delays[i]
            print(f"[*] Esperando {wait:.1f} min...")
            time.sleep(wait * 60)

    print("\n" + "=" * 60)
    print(f"  COMPLETADO - Enviados: {exitosos} / Fallidos: {fallidos}")
    print("=" * 60)
    input("\nPresione Enter para salir...")


if __name__ == "__main__":
    run()
