#!/usr/bin/env python3
"""
Site Mapper - Mapea todas las páginas de un sitio web
Genera una lista completa de URLs para análisis SEO
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
        Inicializa el Site Mapper
        
        Args:
            base_url: URL base del sitio
            max_pages: Número máximo de páginas a mapear
            delay: Delay entre peticiones en segundos
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
        """Verifica si la URL pertenece al mismo dominio"""
        parsed = urlparse(url)
        return parsed.netloc == self.domain
    
    def normalize_url(self, url: str) -> str:
        """Normaliza la URL quitando fragmentos y parámetros innecesarios"""
        parsed = urlparse(url)
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.query:
            clean_url += f"?{parsed.query}"
        return clean_url
    
    def categorize_url(self, url: str) -> str:
        """Categoriza la URL según su estructura"""
        path = urlparse(url).path.strip('/')
        
        if not path:
            return 'inicio'
        elif path.startswith('blog'):
            return 'blog'
        elif path.startswith('servicios') or path.startswith('services'):
            return 'servicios'
        elif path.startswith('contact'):
            return 'contacto'
        elif path.startswith('cv'):
            return 'cv'
        elif path.startswith('presupuestos'):
            return 'presupuestos'
        elif 'cookie' in path:
            return 'legal'
        elif 'privacy' in path or 'privacidad' in path:
            return 'legal'
        elif 'terms' in path or 'terminos' in path:
            return 'legal'
        elif path.startswith('about') or path.startswith('nosotros'):
            return 'empresa'
        elif path == '404':
            return 'error'
        else:
            return 'otro'
    
    def find_links(self, url: str, soup: BeautifulSoup) -> List[str]:
        """Encuentra todos los enlaces internos en la página"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Saltar enlaces vacíos, anclas, javascript, mailto, tel
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
            
            full_url = urljoin(url, href)
            
            if self.is_valid_url(full_url):
                clean_url = self.normalize_url(full_url)
                
                if clean_url not in self.visited_urls and clean_url not in self.to_visit:
                    links.append(clean_url)
        
        return links
    
    def extract_page_info(self, url: str, soup: BeautifulSoup) -> Dict:
        """Extrae información básica de la página"""
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
        """Ejecuta el mapeo del sitio"""
        print(f"=" * 60)
        print(f"MAPEANDO SITIO: {self.base_url}")
        print(f"Dominio: {self.domain}")
        print(f"Máximo de páginas: {self.max_pages}")
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
        print(f"Mapeo completado. Total páginas: {len(self.all_urls)}")
        
        # Resumen por categoría
        categories = {}
        for page in self.all_urls:
            cat = page['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\nResumen por categoría:")
        for cat, count in sorted(categories.items()):
            print(f"  {cat}: {count}")
    
    def save_to_json(self, filename: str = 'site_map.json'):
        """Guarda los resultados en JSON"""
        if not self.all_urls:
            print("No hay resultados para guardar.")
            return
        
        output = {
            'base_url': self.base_url,
            'domain': self.domain,
            'total_pages': len(self.all_urls),
            'pages': self.all_urls
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\nMapa guardado en: {filename}")
    
    def save_to_csv(self, filename: str = 'site_map.csv'):
        """Guarda los resultados en CSV"""
        import csv
        
        if not self.all_urls:
            print("No hay resultados para guardar.")
            return
        
        fieldnames = ['url', 'category', 'title', 'meta_description', 'h1']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.all_urls)
        
        print(f"Mapa guardado en: {filename}")


def main():
    parser = argparse.ArgumentParser(
        description='Site Mapper - Mapea todas las páginas de un sitio web'
    )
    parser.add_argument('url', help='URL del sitio a mapear')
    parser.add_argument('-m', '--max-pages', type=int, default=200,
                        help='Número máximo de páginas (default: 200)')
    parser.add_argument('-d', '--delay', type=float, default=0.5,
                        help='Delay entre peticiones en segundos (default: 0.5)')
    parser.add_argument('-o', '--output', default='site_map',
                        help='Nombre base del archivo de salida (default: site_map)')
    
    args = parser.parse_args()
    
    mapper = SiteMapper(
        base_url=args.url,
        max_pages=args.max_pages,
        delay=args.delay
    )
    
    mapper.map_site()
    
    # Evitar doble extensión
    output_base = args.output
    if output_base.endswith('.json'):
        output_base = output_base[:-5]
    if output_base.endswith('.csv'):
        output_base = output_base[:-4]
    
    mapper.save_to_json(f'{output_base}.json')
    mapper.save_to_csv(f'{output_base}.csv')


if __name__ == '__main__':
    main()
