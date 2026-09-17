#!/usr/bin/env python3
"""
Site Mapper - Maps all pages of a website
Generates a complete list of URLs for SEO analysis
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time
from typing import Dict, List, Set
import argparse


class SiteMapper:
    def __init__(self, base_url: str, max_pages: int = 200, delay: float = 0.5):
        """
        Initializes the Site Mapper

        Args:
            base_url: Base URL of the site
            max_pages: Maximum number of pages to map
            delay: Delay between requests in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.max_pages = max_pages
        self.delay = delay
        self.visited_urls: Set[str] = set()
        self.to_visit: List[str] = [base_url]
        self.all_urls: List[Dict] = []

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def is_valid_url(self, url: str) -> bool:
        """Verifies if the URL belongs to the same domain"""
        parsed = urlparse(url)
        return parsed.netloc == self.domain

    def normalize_url(self, url: str) -> str:
        """Normalizes the URL by removing fragments and unnecessary parameters"""
        parsed = urlparse(url)
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.query:
            clean_url += f"?{parsed.query}"
        return clean_url

    def categorize_url(self, url: str) -> str:
        """Categorizes the URL based on its structure"""
        path = urlparse(url).path.strip('/')

        if not path:
            return 'home'
        elif path.startswith('blog'):
            return 'blog'
        elif path.startswith('servicios') or path.startswith('services'):
            return 'services'
        elif path.startswith('contact'):
            return 'contact'
        elif path.startswith('cv'):
            return 'cv'
        elif path.startswith('presupuestos') or path.startswith('quotes'):
            return 'quotes'
        elif 'cookie' in path:
            return 'legal'
        elif 'privacy' in path or 'privacidad' in path:
            return 'legal'
        elif 'terms' in path or 'terminos' in path:
            return 'legal'
        elif path.startswith('about') or path.startswith('nosotros'):
            return 'company'
        elif path == '404':
            return 'error'
        else:
            return 'other'

    def find_links(self, url: str, soup: BeautifulSoup) -> List[str]:
        """Finds all internal links on the page"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']

            # Skip empty links, anchors, javascript, mailto, tel
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue

            full_url = urljoin(url, href)

            if self.is_valid_url(full_url):
                clean_url = self.normalize_url(full_url)

                if clean_url not in self.visited_urls and clean_url not in self.to_visit:
                    links.append(clean_url)

        return links

    def extract_page_info(self, url: str, soup: BeautifulSoup) -> Dict:
        """Extracts basic information from the page"""
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else ''

        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ''

        h1 = soup.find('h1')
        h1_text = h1.get_text(strip=True) if h1 else ''

        return {
            'url': url,
            'category': self.categorize_url(url),
            'title': title,
            'meta_description': description,
            'h1': h1_text
        }

    def map_site(self):
        """Executes the site mapping"""
        print(f"=" * 60)
        print(f"MAPPING SITE: {self.base_url}")
        print(f"Domain: {self.domain}")
        print(f"Maximum pages: {self.max_pages}")
        print(f"=" * 60)

        while self.to_visit and len(self.visited_urls) < self.max_pages:
            url = self.to_visit.pop(0)

            if url in self.visited_urls:
                continue

            print(f"[{len(self.visited_urls) + 1}/{self.max_pages}] {url}")

            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                page_info = self.extract_page_info(url, soup)
                self.all_urls.append(page_info)

                self.visited_urls.add(url)

                new_links = self.find_links(url, soup)
                self.to_visit.extend(new_links)

                time.sleep(self.delay)

            except Exception as e:
                print(f"  Error: {str(e)}")
                self.visited_urls.add(url)

        print(f"=" * 60)
        print(f"Mapping completed. Total pages: {len(self.all_urls)}")

        # Summary by category
        categories = {}
        for page in self.all_urls:
            cat = page['category']
            categories[cat] = categories.get(cat, 0) + 1

        print("\nSummary by category:")
        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count}")

    def save_to_json(self, filename: str = 'site_map.json'):
        """Saves results to JSON"""
        if not self.all_urls:
            print("No results to save.")
            return

        output = {
            'base_url': self.base_url,
            'domain': self.domain,
            'total_pages': len(self.all_urls),
            'pages': self.all_urls
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\nMap saved to: {filename}")

    def save_to_csv(self, filename: str = 'site_map.csv'):
        """Saves results to CSV"""
        import csv

        if not self.all_urls:
            print("No results to save.")
            return

        fieldnames = ['url', 'category', 'title', 'meta_description', 'h1']

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.all_urls)

        print(f"Map saved to: {filename}")


def main():
    parser = argparse.ArgumentParser(
        description='Site Mapper - Maps all pages of a website'
    )
    parser.add_argument('url', help='URL of the site to map')
    parser.add_argument('-m', '--max-pages', type=int, default=200,
                        help='Maximum number of pages (default: 200)')
    parser.add_argument('-d', '--delay', type=float, default=0.5,
                        help='Delay between requests in seconds (default: 0.5)')
    parser.add_argument('-o', '--output', default='site_map',
                        help='Base name of the output file (default: site_map)')

    args = parser.parse_args()

    mapper = SiteMapper(
        base_url=args.url,
        max_pages=args.max_pages,
        delay=args.delay
    )

    mapper.map_site()

    # Avoid double extension
    output_base = args.output
    if output_base.endswith('.json'):
        output_base = output_base[:-5]
    if output_base.endswith('.csv'):
        output_base = output_base[:-4]

    mapper.save_to_json(f'{output_base}.json')
    mapper.save_to_csv(f'{output_base}.csv')


if __name__ == '__main__':
    main()
