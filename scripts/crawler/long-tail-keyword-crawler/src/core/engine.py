import yaml
from src.utils.network import NetworkManager
from src.utils.selenium_driver import SeleniumDriver
from src.crawlers.google_crawler import GoogleCrawler
from src.crawlers.bing_crawler import BingCrawler
from src.scrapers.serp_scraper import SerpScraper

class ScraperEngine:
    def __init__(self, settings_path='config/settings.yaml'):
        with open(settings_path, 'r') as f:
            self.settings = yaml.safe_load(f)
        
        self.scraping_mode = self.settings.get('scraping_mode', 'http')
        self.webdriver_path = self.settings.get('webdriver_path', None)
        
        self.network_manager = NetworkManager(settings_path)
        self.selenium_driver = None
        
        if self.scraping_mode == 'selenium':
            self.selenium_driver = SeleniumDriver(webdriver_path=self.webdriver_path)
        
        self.crawlers = {
            'google': GoogleCrawler(self.network_manager, self.selenium_driver, settings_path),
            'bing': BingCrawler(self.network_manager, self.selenium_driver, settings_path)
        }

    def run(self, initial_keywords, search_engines=['google']):
        if self.scraping_mode == 'selenium' and not self.selenium_driver.driver:
            print("Selenium mode is enabled but WebDriver could not start. Aborting.")
            return []
            
        all_results = []
        try:
            for keyword in initial_keywords:
                print(f"Processing keyword: {keyword}")
                for engine_name in search_engines:
                    if engine_name in self.crawlers:
                        crawler = self.crawlers[engine_name]
                        scraper = SerpScraper(engine_name)

                        suggestions = crawler.get_suggestions(keyword)
                        print(f"  Suggestions from {engine_name} for '{keyword}': {suggestions}")
                        
                        keywords_to_search = list(set([keyword] + suggestions))

                        for kw_to_search in keywords_to_search:
                            print(f"    Searching {engine_name} SERP for '{kw_to_search}'")
                            html_content = crawler.search_serp(kw_to_search)
                            
                            if html_content:
                                if kw_to_search == keyword:
                                    debug_filepath = f"data/debug_html/{engine_name}_{kw_to_search.replace(' ', '_')}.html"
                                    with open(debug_filepath, 'w', encoding='utf-8') as f:
                                        f.write(html_content)
                                    print(f"      Debug HTML saved to {debug_filepath}")
                                
                                serp_results = scraper.scrape(html_content)
                                all_results.append({
                                    'keyword': kw_to_search,
                                    'engine': engine_name,
                                    'results': serp_results
                                })
                            else:
                                print(f"      Could not retrieve SERP content for '{kw_to_search}' on {engine_name}")
                    else:
                        print(f"Search engine '{engine_name}' not supported.")
        finally:
            if self.selenium_driver:
                self.selenium_driver.close()
        
        return all_results