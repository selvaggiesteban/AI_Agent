from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

class SeleniumDriver:
    def __init__(self, webdriver_path=None, headless=True):
        self.webdriver_path = webdriver_path
        self.headless = headless
        self.driver = self._start_driver()

    def _start_driver(self):
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920x1080")
        chrome_options.add_argument("--log-level=3") # Suppress unnecessary logs
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36")

        try:
            if self.webdriver_path:
                service = Service(executable_path=self.webdriver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
            else:
                # Try to use the webdriver if it's in the system PATH
                driver = webdriver.Chrome(options=chrome_options)
            
            print("Selenium WebDriver started successfully.")
            return driver
        except Exception as e:
            print(f"Error starting Selenium WebDriver: {e}")
            print("Please ensure ChromeDriver is installed and the path in 'config/settings.yaml' is correct.")
            return None

    def get_page_source(self, url):
        if not self.driver:
            return None
        try:
            self.driver.get(url)
            # We could add smart waits here if necessary
            time.sleep(2) # Simple wait for the page to load
            return self.driver.page_source
        except Exception as e:
            print(f"Error getting content for URL {url} with Selenium: {e}")
            return None

    def close(self):
        if self.driver:
            self.driver.quit()
            print("Selenium WebDriver closed.")