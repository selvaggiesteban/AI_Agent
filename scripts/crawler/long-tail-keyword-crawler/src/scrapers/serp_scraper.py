import yaml
from bs4 import BeautifulSoup

class SerpScraper:
    def __init__(self, engine, settings_path='config/settings.yaml'):
        with open(settings_path, 'r') as f:
            self.settings = yaml.safe_load(f)
        self.selectors = self.settings['search_engines'][engine]['selectors']

    def scrape(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []

        for result_div in soup.select(self.selectors['results']):
            title_tag = result_div.select_one(self.selectors['title'])
            url_tag = result_div.select_one(self.selectors['url'])
            description_tag = result_div.select_one(self.selectors['description'])

            title = title_tag.get_text(strip=True) if title_tag else None
            url = url_tag['href'] if url_tag and 'href' in url_tag.attrs else None
            description = description_tag.get_text(strip=True) if description_tag else None

            if title and url:
                results.append({
                    'title': title,
                    'url': url,
                    'description': description
                })
        return results
