"""
Test RPA - send?phone= con 3 numeros nuevos
"""

import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

MENSAJE = config["mensaje"]
NUMEROS_TEST = config["numeros"][6:9]  # next 3 uncontacted

SELECTOR_INPUT = '[data-testid="conversation-compose-box-input"]'


def close_popups(driver):
    try:
        el = driver.find_element(By.CSS_SELECTOR, '[data-testid="popup-controls-close"]')
        el.click()
        print("  Popup cerrado.")
        time.sleep(1)
    except:
        pass


def open_chat(driver, phone):
    url = f"https://web.whatsapp.com/send?phone={phone}"
    print(f"  Abriendo chat: {phone}")
    driver.get(url)
    time.sleep(5)
    close_popups(driver)

    try:
        WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, SELECTOR_INPUT))
        )
        print(f"  Chat OK: {phone}")
        return True
    except TimeoutException:
        try:
            driver.find_element(
                By.XPATH, '//*[contains(text(), "no es v") or contains(text(), "invalid") or contains(text(), "not found")]'
            )
            print(f"  Numero invalido: {phone}")
        except NoSuchElementException:
            print(f"  Chat no cargo: {phone}")
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
        print("  Mensaje ENVIADO.")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False


def main():
    print("=" * 50)
    print("  TEST send?phone= - 3 numeros")
    print("=" * 50)
    print(f"  Numeros: {NUMEROS_TEST}")
    print("=" * 50)

    options = Options()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(options=options)

    exitosos = 0

    for i, phone in enumerate(NUMEROS_TEST):
        print(f"\n[{i+1}/3] {phone}")

        if open_chat(driver, phone):
            time.sleep(1)
            if send_message(driver, MENSAJE):
                exitosos += 1

        if i < len(NUMEROS_TEST) - 1:
            print("  Esperando 5s...")
            time.sleep(5)

    print("\n" + "=" * 50)
    print(f"  TEST COMPLETADO - Enviados: {exitosos}/3")
    print("=" * 50)


if __name__ == "__main__":
    main()
