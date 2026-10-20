from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

o = Options()
o.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
d = webdriver.Chrome(options=o)

phone = "34607257334"

print(f"Title: {d.title}")

# Find search input
search = d.find_element(By.CSS_SELECTOR, '[data-testid="chat-list-search-container"] input[type="text"]')
print(f"Search placeholder: {search.get_attribute('placeholder')}")

search.click()
time.sleep(0.3)
search.clear()
search.send_keys(phone)
time.sleep(3)

print(f"\nAfter typing '{phone}':")

# Check for "no results"
page_text = d.find_element(By.CSS_SELECTOR, '[data-testid="chat-list"]').text
print(f"Chat list text: {page_text[:200]}")

# Check all list items
items = d.find_elements(By.CSS_SELECTOR, '[data-testid="chat-list"] div[role="listitem"]')
print(f"List items: {len(items)}")

# Check all spans in chat list with the phone number
spans = d.find_elements(By.XPATH, f'//span[contains(text(), "{phone[-6:]}")]')
print(f"Spans with last 6 digits ({phone[-6:]}): {len(spans)}")

# Check all testids in chat list
testids = d.find_elements(By.CSS_SELECTOR, '[data-testid]')
search_tids = [e.get_attribute("data-testid") for e in testids if "search" in e.get_attribute("data-testid").lower() or "result" in e.get_attribute("data-testid").lower()]
print(f"Search/result testids: {search_tids}")

# Check if search input has text
val = search.get_attribute("value")
print(f"Search value: '{val}'")
