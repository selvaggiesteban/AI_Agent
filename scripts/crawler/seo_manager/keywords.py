import sys
import os
import re
import json
import time
import random
import asyncio
import argparse
import requests
import httpx
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from concurrent.futures import ThreadPoolExecutor

# Add root to sys.path
from core.paths import PROJECT_ROOT, INPUTS_DIR, OUTPUTS_DIR
sys.path.append(str(PROJECT_ROOT / "scripts" / "seo_manager"))

# =============================================================================
# 1. KEYWORD GENERATOR (CONCATENATION)
# =============================================================================

class KeywordGenerator:
    @staticmethod
    def generate(val1_str: str, val2_str: str) -> List[str]:
        list1 = [item.strip() for item in val1_str.split(',') if item.strip()]
        list2 = [item.strip() for item in val2_str.split(',') if item.strip()]
        results = [f"{item1} {item2}" for item1 in list1 for item2 in list2]
        return results

# =============================================================================
# 2. COMPETITOR FINDER (EXCEL PARSING)
# =============================================================================

class CompetitorFinder:
    NON_LOCAL_DOMAINS = [
        "facebook.com", "youtube.com", "instagram.com", "linkedin.com", "twitter.com",
        "pinterest.com", "google.com", "amazon.com", "ebay.com", "aliexpress.com"
    ]

    @staticmethod
    def find_local(xlsx_path: str, exclude_list: List[str] = None) -> List[Dict[str, str]]:
        import openpyxl
        exclude = exclude_list or CompetitorFinder.NON_LOCAL_DOMAINS
        try:
            wb = openpyxl.load_workbook(xlsx_path)
            sheet = wb.active
            results = []
            for row in sheet.iter_rows(min_row=2, max_row=100, values_only=True):
                if row and row[0]:
                    domain = str(row[0]).lower()
                    if domain not in exclude:
                        url = next((c for c in row[1:] if isinstance(c, str) and c.startswith('http')), f"https://{domain}")
                        results.append({"domain": domain, "url": url})
            return results
        except Exception as e:
            print(f"Error parsing Excel: {e}")
            return []

# =============================================================================
# 3. SCRAPER ENGINE (GOOGLE & BING)
# =============================================================================

class KeywordScraper:
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
    ]

    def __init__(self):
        self.session = requests.Session()

    def get_suggestions(self, keyword: str, engine: str = 'google') -> List[str]:
        headers = {"User-Agent": random.choice(self.USER_AGENTS)}
        if engine == 'google':
            url = "http://suggestqueries.google.com/complete/search"
            params = {"client": "chrome", "q": keyword, "hl": "es"}
            try:
                r = self.session.get(url, params=params, headers=headers, timeout=10)
                if r.status_code == 200:
                    return [item for item in r.json()[1]]
            except: pass
        elif engine == 'bing':
            url = "https://www.bing.com/AS/Suggestions"
            params = {"q": keyword}
            try:
                r = self.session.get(url, params=params, headers=headers, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    return [item['Txt'] for item in data.get('AS', {}).get('Results', [{}])[0].get('Suggests', [])]
            except: pass
        return []

    def scrape_serp(self, keyword: str, engine: str = 'google') -> List[Dict]:
        headers = {"User-Agent": random.choice(self.USER_AGENTS)}
        url = f"https://www.{engine}.com/search?q={keyword.replace(' ', '+')}"
        try:
            r = self.session.get(url, headers=headers, timeout=15)
            if r.status_code != 200: return []
            
            soup = BeautifulSoup(r.text, 'html.parser')
            results = []
            
            # Simple selector logic for demonstration
            if engine == 'google':
                items = soup.select('div.g')
                for item in items:
                    t = item.select_one('h3')
                    l = item.select_one('a')
                    if t and l: results.append({"title": t.text, "url": l['href']})
            
            return results
        except: return []

# =============================================================================
# CLI ORCHESTRATOR
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Unified Keyword & Competitor Tool")
    parser.add_argument("--mode", choices=["generate", "find-competitors", "scrape"], required=True)
    parser.add_argument("--v1", help="Concatenation group 1")
    parser.add_argument("--v2", help="Concatenation group 2")
    parser.add_argument("--xlsx", help="Excel path for competitor finding")
    parser.add_argument("--keywords", nargs="+", help="Keywords to scrape")
    
    args = parser.parse_args()

    if args.mode == "generate":
        if not args.v1 or not args.v2:
            print("Error: --v1 and --v2 are required.")
            return
        res = KeywordGenerator.generate(args.v1, args.v2)
        print("\n".join(res))

    elif args.mode == "find-competitors":
        if not args.xlsx:
            print("Error: --xlsx is required.")
            return
        res = CompetitorFinder.find_local(args.xlsx)
        for c in res: print(f"{c['domain']} -> {c['url']}")

    elif args.mode == "scrape":
        if not args.keywords:
            print("Error: --keywords is required.")
            return
        scraper = KeywordScraper()
        for kw in args.keywords:
            print(f"[*] Suggestions for {kw}: {scraper.get_suggestions(kw)}")

if __name__ == "__main__":
    main()
