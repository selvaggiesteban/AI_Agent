import json
import yaml
from .base_crawler import BaseCrawler

class BingCrawler(BaseCrawler):
    def __init__(self, network_manager, selenium_driver=None, settings_path='config/settings.yaml'):
        super().__init__(network_manager)
        self.selenium_driver = selenium_driver
        with open(settings_path, 'r') as f:
            self.settings = yaml.safe_load(f)
        self.suggest_url = self.settings['search_engines']['bing']['suggest_url']
        self.search_url = self.settings['search_engines']['bing']['search_url']

    def get_suggestions(self, keyword):
        # Suggestions are still obtained via HTTP for efficiency
        params = {
            'q': keyword
        }
        response = self.network_manager.fetch(self.suggest_url, params=params)
        if response and response.status_code == 200:
            try:
                data = response.json()
                if 'AS' in data and 'Results' in data['AS'] and data['AS']['Results']:
                    suggestions = [item['Txt'] for item in data['AS']['Results'][0]['Suggests']]
                    return suggestions
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error parsing Bing suggestions JSON: {e}")
                print(f"Response: {response.text}")
                return []
        return []

    def search_serp(self, keyword):
        # SERP search now uses Selenium if available
        if self.selenium_driver:
            url = self.search_url.format(keyword=keyword)
            return self.selenium_driver.get_page_source(url)
        else:
            # Fallback to HTTP method if no Selenium driver
            url = self.search_url.format(keyword=keyword)
            response = self.network_manager.fetch(url)
            if response and response.status_code == 200:
                return response.text
            return None