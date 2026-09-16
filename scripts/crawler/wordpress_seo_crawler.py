#!/usr/bin/env python3
"""
WordPress SEO Crawler
Rastreador de blogs WordPress para análisis SEO completo
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
        Inicializa el crawler
        
        Args:
            base_url: URL base del sitio WordPress
            max_pages: Número máximo de páginas a rastrear
            delay: Delay entre peticiones en segundos
        """
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.max_pages = max_pages
        self.delay = delay
        self.visited_urls: Set[str] = set()
        self.to_visit: List[str] = [base_url]
        self.results: List[Dict] = []
        
        # Headers para simular un navegador
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def is_valid_url(self, url: str) -> bool:
        """Verifica si la URL pertenece al mismo dominio"""
        parsed = urlparse(url)
        return parsed.netloc == self.domain
    
    def extract_keyword_from_url(self, url: str) -> str:
        """Extrae la palabra clave principal del slug de la URL"""
        path = urlparse(url).path.strip('/')
        # Obtener la última parte de la URL (slug del artículo)
        parts = path.split('/')
        if parts:
            slug = parts[-1]
            # Convertir guiones en espacios
            keyword = slug.replace('-', ' ').replace('_', ' ')
            return keyword.title()
        return ""
    
    def extract_schema(self, soup: BeautifulSoup) -> str:
        """Extrae el Schema Markup de la página"""
        schemas = []
        
        # Buscar script tags con tipo application/ld+json
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
        """Extrae información del CTA (Call To Action)"""
        # Buscar CTAs comunes en WordPress
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
        """Cuenta todos los headers (H1-H6)"""
        count = 0
        for i in range(1, 7):
            count += len(soup.find_all(f'h{i}'))
        return count
    
    def analyze_images(self, soup: BeautifulSoup) -> tuple:
        """Analiza imágenes sin ALT y sin TITLE"""
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
        """Extrae todos los datos SEO de una página"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer datos
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
            
            # Author y Publisher
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
            
            # Keyword del cluster
            keyword = self.extract_keyword_from_url(url)
            
            # Headers count
            headers_count = self.count_headers(soup)
            
            # Imágenes
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
            print(f"Error al procesar {url}: {str(e)}")
            return None
    
    def find_links(self, url: str, soup: BeautifulSoup) -> List[str]:
        """Encuentra todos los enlaces internos en la página"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(url, href)
            
            # Filtrar solo enlaces del mismo dominio
            if self.is_valid_url(full_url):
                # Limpiar la URL (quitar fragmentos y parámetros innecesarios)
                parsed = urlparse(full_url)
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                
                # Evitar duplicados y URLs ya visitadas
                if clean_url not in self.visited_urls and clean_url not in self.to_visit:
                    links.append(clean_url)
        
        return links
    
    def crawl(self):
        """Ejecuta el rastreo del sitio"""
        print(f"Iniciando rastreo de: {self.base_url}")
        print(f"Máximo de páginas: {self.max_pages}")
        print("-" * 60)
        
        while self.to_visit and len(self.visited_urls) < self.max_pages:
            url = self.to_visit.pop(0)
            
            if url in self.visited_urls:
                continue
            
            print(f"Rastreando ({len(self.visited_urls) + 1}/{self.max_pages}): {url}")
            
            try:
                # Obtener y analizar la página
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extraer datos de la página
                page_data = self.extract_page_data(url)
                if page_data:
                    self.results.append(page_data)
                
                # Marcar como visitada
                self.visited_urls.add(url)
                
                # Encontrar nuevos enlaces
                new_links = self.find_links(url, soup)
                self.to_visit.extend(new_links)
                
                # Delay para no sobrecargar el servidor
                time.sleep(self.delay)
                
            except Exception as e:
                print(f"Error al rastrear {url}: {str(e)}")
                self.visited_urls.add(url)
        
        print("-" * 60)
        print(f"Rastreo completado. Páginas analizadas: {len(self.results)}")
    
    def save_to_csv(self, filename: str = 'wordpress_seo_analysis.csv'):
        """Guarda los resultados en un archivo CSV"""
        if not self.results:
            print("No hay resultados para guardar.")
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
        
        print(f"\nResultados guardados en: {filename}")


def main():
    parser = argparse.ArgumentParser(
        description='WordPress SEO Crawler - Analiza blogs de WordPress'
    )
    parser.add_argument('url', help='URL del sitio WordPress a rastrear')
    parser.add_argument('-m', '--max-pages', type=int, default=100,
                        help='Número máximo de páginas a rastrear (default: 100)')
    parser.add_argument('-d', '--delay', type=float, default=1.0,
                        help='Delay entre peticiones en segundos (default: 1.0)')
    parser.add_argument('-o', '--output', default='wordpress_seo_analysis.csv',
                        help='Nombre del archivo CSV de salida')
    
    args = parser.parse_args()
    
    # Crear y ejecutar el crawler
    crawler = WordPressSEOCrawler(
        base_url=args.url,
        max_pages=args.max_pages,
        delay=args.delay
    )
    
    crawler.crawl()
    crawler.save_to_csv(args.output)


if __name__ == '__main__':
    main()
