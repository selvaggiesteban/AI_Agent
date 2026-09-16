import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

class Scraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def fetch_content(self, url):
        """
        Fetches the URL content and returns a dictionary with 'text', 'markdown', and 'title'.
        Returns None if fetching fails.
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Handle encoding
            if response.encoding is None:
                response.encoding = 'utf-8'

            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove clutter
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
                tag.decompose()

            title = soup.title.string.strip() if soup.title else "No Title"
            text_content = soup.get_text(separator=' ', strip=True)
            markdown_content = md(str(soup.body)) if soup.body else text_content

            return {
                "title": title,
                "text": text_content,
                "markdown": markdown_content,
                "url": url
            }
        except Exception as e:
            print(f"[!] Failed to scrape {url}: {e}")
            return None
