#!/usr/bin/env python3
"""
WordPress SEO Crawler
Crawler for WordPress blogs for comprehensive SEO analysis
"""

import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time
from collections import defaultdict
import re
from typing import Dict, List, Set
import argparse


class WordPressSEOCrawler:
    def __init__(self, base_url: str, max_pages: int = 100, delay: float = 1.0):
        """
        Initializes the crawler

        Args:
            base_url: Base URL of the WordPress site
            max_pages: Maximum number of pages to crawl
            delay: Delay between requests in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.max_pages = max_pages
        self.delay = delay
        self.visited_urls: Set[str] = set()
        self.to_visit: List[str] = [base_url]
        self.results: List[Dict] = []

        # Headers to simulate a browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def is_valid_url(self, url: str) -> bool:
        """Verifies if the URL belongs to the same domain"""
        parsed = urlparse(url)
        return parsed.netloc == self.domain

    def extract_keyword_from_url(self, url: str) -> str:
        """Extracts the main keyword from the URL slug"""
        path = urlparse(url).path.strip('/')
        # Get the last part of the URL (article slug)
        parts = path.split('/')
        if parts:
            slug = parts[-1]
            # Convert dashes to spaces
            keyword = slug.replace('-', ' ').replace('_', ' ')
            return keyword.title()
        return ""

    def extract_schema(self, soup: BeautifulSoup) -> str:
        """Extracts the Schema Markup from the page"""
        schemas = []

        # Look for script tags with type application/ld+json
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                schema_data = json.loads(script.string)
                if isinstance(schema_data, dict):
                    schema_type = schema_data.get('@type', 'Unknown')
                    schemas.append(schema_type)
                elif isinstance(schema_data, list):
                    for item in schema_data:
                        if isinstance(item, dict):
                            schema_type = item.get('@type', 'Unknown')
                            schemas.append(schema_type)
            except:
                continue

        return ', '.join(schemas) if schemas else 'No Schema'

    def extract_cta_info(self, soup: BeautifulSoup) -> tuple:
        """Extracts information from the CTA (Call To Action)"""
        # Search for common CTAs in WordPress
        cta_selectors = [
            'a.cta', 'a.btn', 'a.button',
            'a[href*="contact"]', 'a[href*="subscribe"]',
            '.cta a', '.call-to-action a', '.wp-block-button a'
        ]

        for selector in cta_selectors:
            cta = soup.select_one(selector)
            if cta and cta.get('href'):
                return cta.get('href', ''), cta.get_text(strip=True)

        return '', ''

    def count_headers(self, soup: BeautifulSoup) -> int:
        """Counts all headers (H1-H6)"""
        count = 0
        for i in range(1, 7):
            count += len(soup.find_all(f'h{i}'))
        return count

    def analyze_images(self, soup: BeautifulSoup) -> tuple:
        """Analyzes images without ALT and without TITLE"""
        images = soup.find_all('img')
        without_alt = 0
        without_title = 0
        all_alts = []

        for img in images:
            alt = img.get('alt', '').strip()
            title = img.get('title', '').strip()

            if not alt:
                without_alt += 1
            else:
                all_alts.append(alt)

            if not title:
                without_title += 1

        return without_alt, without_title, ' | '.join(all_alts) if all_alts else 'No ALT'

    def extract_page_data(self, url: str) -> Dict:
        """Extracts all SEO data from a page"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract data
            h1 = soup.find('h1')
            h1_text = h1.get_text(strip=True) if h1 else 'No H1'

            # Meta tags
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            meta_description = meta_desc.get('content', 'No Meta Description') if meta_desc else 'No Meta Description'

            # SEO Title
            title_tag = soup.find('title')
            seo_title = title_tag.get_text(strip=True) if title_tag else 'No Title'

            # Robots
            robots_tag = soup.find('meta', attrs={'name': 'robots'})
            robots = robots_tag.get('content', 'index, follow') if robots_tag else 'index, follow'

            # Author and Publisher
            author_meta = soup.find('meta', attrs={'name': 'author'}) or soup.find('meta', property='article:author')
            author = author_meta.get('content', 'No Author') if author_meta else 'No Author'

            publisher_meta = soup.find('meta', property='article:publisher')
            publisher = publisher_meta.get('content', 'No Publisher') if publisher_meta else 'No Publisher'

            # Lang
            html_tag = soup.find('html')
            lang = html_tag.get('lang', 'No Lang') if html_tag else 'No Lang'

            # CTA
            cta_url, cta_anchor = self.extract_cta_info(soup)

            # Schema
            schema = self.extract_schema(soup)

            # Keyword of the cluster
            keyword = self.extract_keyword_from_url(url)

            # Headers count
            headers_count = self.count_headers(soup)

            # Images
            imgs_without_alt, imgs_without_title, alt_texts = self.analyze_images(soup)

            return {
                'URL': url,
                'Keyword (Cluster)': keyword,
                'H1': h1_text,
                'CTA URL': cta_url,
                'CTA Anchor Text': cta_anchor,
                'Schema': schema,
                'Meta Description': meta_description,
                'SEO Title': seo_title,
                'Alt Texts': alt_texts,
                'Robots Tag': robots,
                'Author': author,
                'Publisher': publisher,
                'Lang': lang,
                'Headers (quantity)': headers_count,
                'Images without ALT': imgs_without_alt,
                'Images without TITLE': imgs_without_title
            }

        except Exception as e:
            print(f"Error processing {url}: {str(e)}")
            return None

    def find_links(self, url: str, soup: BeautifulSoup) -> List[str]:
        """Finds all internal links on the page"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)

            # Filter only links from the same domain
            if self.is_valid_url(full_url):
                # Clean the URL (remove fragments and unnecessary parameters)
                parsed = urlparse(full_url)
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

                # Avoid duplicates and already visited URLs
                if clean_url not in self.visited_urls and clean_url not in self.to_visit:
                    links.append(clean_url)

        return links

    def crawl(self):
        """Executes the site crawl"""
        print(f"Starting crawl of: {self.base_url}")
        print(f"Maximum pages: {self.max_pages}")
        print("-" * 60)

        while self.to_visit and len(self.visited_urls) < self.max_pages:
            url = self.to_visit.pop(0)

            if url in self.visited_urls:
                continue

            print(f"Crawling ({len(self.visited_urls) + 1}/{self.max_pages}): {url}")

            try:
                # Get and analyze the page
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract page data
                page_data = self.extract_page_data(url)
                if page_data:
                    self.results.append(page_data)

                # Mark as visited
                self.visited_urls.add(url)

                # Find new links
                new_links = self.find_links(url, soup)
                self.to_visit.extend(new_links)

                # Delay to avoid overloading the server
                time.sleep(self.delay)

            except Exception as e:
                print(f"Error crawling {url}: {str(e)}")
                self.visited_urls.add(url)

        print("-" * 60)
        print(f"Crawl completed. Pages analyzed: {len(self.results)}")

    def save_to_csv(self, filename: str = 'wordpress_seo_analysis.csv'):
        """Saves results to a CSV file"""
        if not self.results:
            print("No results to save.")
            return

        fieldnames = [
            'URL', 'Keyword (Cluster)', 'H1', 'CTA URL', 'CTA Anchor Text',
            'Schema', 'Meta Description', 'SEO Title', 'Alt Texts',
            'Robots Tag', 'Author', 'Publisher', 'Lang', 'Headers (quantity)',
            'Images without ALT', 'Images without TITLE'
        ]

        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)

        print(f"\nResults saved to: {filename}")


def main():
    parser = argparse.ArgumentParser(
        description='WordPress SEO Crawler - Analyzes WordPress blogs'
    )
    parser.add_argument('url', help='URL of the WordPress site to crawl')
    parser.add_argument('-m', '--max-pages', type=int, default=100,
                        help='Maximum number of pages to crawl (default: 100)')
    parser.add_argument('-d', '--delay', type=float, default=1.0,
                        help='Delay between requests in seconds (default: 1.0)')
    parser.add_argument('-o', '--output', default='wordpress_seo_analysis.csv',
                        help='Name of the output CSV file')

    args = parser.parse_args()

    # Create and run the crawler
    crawler = WordPressSEOCrawler(
        base_url=args.url,
        max_pages=args.max_pages,
        delay=args.delay
    )

    crawler.crawl()
    crawler.save_to_csv(args.output)


if __name__ == '__main__':
    main()
