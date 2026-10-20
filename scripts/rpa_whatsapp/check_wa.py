from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

o = Options()
o.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
d = webdriver.Chrome(options=o)
print("URL:", d.current_url)
print("Title:", d.title)
try:
    el = d.find_element(By.CSS_SELECTOR, 'div[contenteditable="true"][data-tab="10"]')
    print("WhatsApp Web LISTO - sesion activa")
except:
    try:
        qr = d.find_element(By.CSS_SELECTOR, "canvas")
        print("QR detectado - escanealo")
    except:
        print("Cargando...")
