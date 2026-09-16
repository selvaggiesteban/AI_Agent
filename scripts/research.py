import sys
import os
import re
import json
import time
import random
import argparse
import requests
import asyncio
import html
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from markdownify import markdownify as md
from duckduckgo_search import DDGS
from fpdf import FPDF
from fpdf.enums import XPos, YPos

# Conditional imports for heavy dependencies
try:
    from sumy.parsers.plaintext import PlaintextParser
    from sumy.nlp.tokenizers import Tokenizer
    from sumy.summarizers.lsa import LsaSummarizer
    from sumy.utils import get_stop_words
    import nltk
except ImportError:
    pass

try:
    from pypdf import PdfReader
    from docx import Document
    import openpyxl
    from pptx import Presentation
    import pytesseract
    from PIL import Image
    import speech_recognition as sr
    from pydub import AudioSegment
    from moviepy import VideoFileClip
except ImportError:
    pass

# Add root to sys.path
from core.paths import PROJECT_ROOT, OUTPUTS_DIR as DATA_OUTPUTS_DIR
sys.path.append(str(PROJECT_ROOT / "scripts" / "web_scraper"))

# =============================================================================
# 1. SCRAPER & SEARCH
# =============================================================================

class SearchEngine:
    def __init__(self, max_results=10):
        self.max_results = max_results

    def search(self, query):
        logger.info(f"Searching for: '{query}'...")
        try:
            ddgs = DDGS()
            return list(ddgs.text(query, max_results=self.max_results))
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

class Scraper:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    def fetch_content(self, url):
        try:
            r = requests.get(url, headers=self.headers, timeout=10)
            r.raise_for_status()
            soup = BeautifulSoup(r.content, 'html.parser')
            for tag in soup(["script", "style", "nav", "footer", "header"]): tag.decompose()
            return {"title": soup.title.string.strip() if soup.title else "No Title", "text": soup.get_text(separator=' ', strip=True), "url": url}
        except: return None

# =============================================================================
# 2. ANALYSIS & SUMMARIZATION
# =============================================================================

class Analyzer:
    def __init__(self, language="spanish"):
        self.language = language
        try:
            nltk.data.find('tokenizers/punkt')
        except:
            nltk.download('punkt')
            nltk.download('punkt_tab')

    def get_narrative_block(self, text, sentence_count=15):
        if not text: return ""
        try:
            parser = PlaintextParser.from_string(text, Tokenizer(self.language))
            summarizer = LsaSummarizer()
            summarizer.stop_words = get_stop_words(self.language)
            sentences = summarizer(parser.document, sentence_count)
            return " ".join([str(s) for s in sentences])
        except: return text[:500] + "..."

# =============================================================================
# 3. GENERATORS (HTML & PDF)
# =============================================================================

class HTMLGenerator:
    def __init__(self, keyword):
        self.keyword = keyword
        self.content = []

    def add_section(self, title, body):
        self.content.append(f"<h2>{html.escape(title)}</h2><p>{html.escape(body)}</p>")

    def save(self, path):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"<html><body><h1>{self.keyword}</h1>" + "\n".join(self.content) + "</body></html>")

class PDFReport(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10, 'SADD Smart Research Report', border=False, ln=True, align='C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

# =============================================================================
# CLI ORCHESTRATOR
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="SADD Smart Research Assistant")
    parser.add_argument("--query", required=True, help="Topic to research")
    parser.add_argument("--output", help="Output filename")
    
    args = parser.parse_args()
    
    print(f"[*] Starting research on: {args.query}")
    
    # 1. Search
    searcher = SearchEngine()
    results = searcher.search(args.query)
    
    # 2. Scrape & Analyze
    scraper = Scraper()
    analyzer = Analyzer()
    full_text = ""
    for res in results[:3]:
        data = scraper.fetch_content(res['href'])
        if data: full_text += data['text'] + " "
    
    summary = analyzer.get_narrative_block(full_text)
    
    # 3. Generate
    out_dir = DATA_OUTPUTS_DIR / "research"
    out_dir.mkdir(parents=True, exist_ok=True)
    
    html_gen = HTMLGenerator(args.query)
    html_gen.add_section("Executive Summary", summary)
    
    filename = args.output or args.query.replace(' ', '_')
    html_gen.save(out_dir / f"{filename}.html")
    
    print(f"✅ Research completed. Results saved in {out_dir}")

if __name__ == "__main__":
    main()
