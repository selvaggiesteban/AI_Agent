from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

o = Options()
o.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
d = webdriver.Chrome(options=o)

# Click first chat
chat = d.find_element(By.CSS_SELECTOR, '[data-testid="list-item-0"]')
chat.click()
print("Clicked first chat")
time.sleep(3)

print(f"URL: {d.current_url}")
print(f"Title: {d.title}")

# Find ALL contenteditable
els = d.find_elements(By.CSS_SELECTOR, '[contenteditable="true"]')
print(f"contenteditable: {len(els)}")
for i, e in enumerate(els):
    print(f"  [{i}] title='{e.get_attribute('title')}' data-tab='{e.get_attribute('data-tab')}' role='{e.get_attribute('role')}'")

# Find compose box
for sel in [
    '[data-testid="conversation-compose-box-input"]',
    '[data-testid="send"]',
    '#main [contenteditable="true"]',
    '#main footer [contenteditable="true"]',
    '#footer [contenteditable="true"]',
]:
    try:
        el = d.find_element(By.CSS_SELECTOR, sel)
        print(f"FOUND: {sel}")
    except:
        pass
