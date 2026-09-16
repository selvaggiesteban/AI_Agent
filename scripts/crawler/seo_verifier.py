#!/usr/bin/env python3
"""
SEO Verifier - Verifica requisitos SEO en páginas web
Analiza 35+ requisitos y genera reportes detallados
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import json
import csv
import time
from typing import Dict, List
import argparse
import os


class SEOVerifier:
    def __init__(self, base_url: str, delay: float = 0.5):
        """
        Inicializa el verificador SEO
        
        Args:
            base_url: URL base del sitio
            delay: Delay entre peticiones
        """
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.delay = delay
        self.results: List[Dict] = []
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def check_meta_title(self, soup: BeautifulSoup) -> Dict:
        """Verifica meta título"""
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else ''
        
        return {
            'name': 'meta_title',
            'pass': bool(title),
            'value': title if title else 'No Title',
            'message': 'Meta título presente' if title else 'Falta meta título'
        }
    
    def check_meta_description(self, soup: BeautifulSoup) -> Dict:
        """Verifica meta descripción"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        desc = meta_desc.get('content', '') if meta_desc else ''
        
        return {
            'name': 'meta_description',
            'pass': bool(desc),
            'value': desc if desc else 'No Meta Description',
            'message': 'Meta descripción presente' if desc else 'Falta meta descripción'
        }
    
    def check_h1(self, soup: BeautifulSoup) -> Dict:
        """Verifica H1 único"""
        h1_tags = soup.find_all('h1')
        count = len(h1_tags)
        h1_text = h1_tags[0].get_text(strip=True) if h1_tags else ''
        
        return {
            'name': 'h1_unique',
            'pass': count == 1,
            'value': f"{count} H1: {h1_text[:50]}..." if h1_text else 'No H1',
            'message': 'Un solo H1' if count == 1 else f'{count} H1 encontrados'
        }
    
    def check_h1_not_equals_title(self, soup: BeautifulSoup) -> Dict:
        """Verifica que H1 sea diferente al título"""
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else ''
        
        h1_tags = soup.find_all('h1')
        h1_text = h1_tags[0].get_text(strip=True) if h1_tags else ''
        
        if not title or not h1_text:
            return {
                'name': 'h1_not_equals_title',
                'pass': False,
                'value': 'N/A',
                'message': 'No se puede comparar (falta título o H1)'
            }
        
        # Normalizar para comparación
        title_norm = title.lower().strip()
        h1_norm = h1_text.lower().strip()
        
        return {
            'name': 'h1_not_equals_title',
            'pass': title_norm != h1_norm,
            'value': f"Título: {title[:30]}... | H1: {h1_text[:30]}...",
            'message': 'H1 diferente al título' if title_norm != h1_norm else 'H1 igual al título'
        }
    
    def check_schema(self, soup: BeautifulSoup) -> Dict:
        """Verifica Schema JSON-LD"""
        schemas = []
        
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                schema_data = json.loads(script.string)
                if isinstance(schema_data, dict):
                    schema_type = schema_data.get('@type', 'Unknown')
                    if isinstance(schema_type, list):
                        schemas.extend(schema_type)
                    else:
                        schemas.append(str(schema_type))
                elif isinstance(schema_data, list):
                    for item in schema_data:
                        if isinstance(item, dict):
                            schema_type = item.get('@type', 'Unknown')
                            if isinstance(schema_type, list):
                                schemas.extend(schema_type)
                            else:
                                schemas.append(str(schema_type))
            except:
                continue
        
        # Convertir todos a strings
        schemas_str = [str(s) for s in schemas]
        
        return {
            'name': 'schema_jsonld',
            'pass': len(schemas_str) > 0,
            'value': ', '.join(schemas_str) if schemas_str else 'No Schema',
            'message': f"Schema encontrado: {', '.join(schemas_str)}" if schemas_str else 'Sin Schema JSON-LD'
        }
    
    def check_og_image(self, soup: BeautifulSoup) -> Dict:
        """Verifica Open Graph image"""
        og_image = soup.find('meta', property='og:image')
        
        return {
            'name': 'og_image',
            'pass': bool(og_image),
            'value': og_image.get('content', '')[:100] if og_image else 'No OG Image',
            'message': 'OG Image presente' if og_image else 'Falta OG Image'
        }
    
    def check_favicon(self, soup: BeautifulSoup) -> Dict:
        """Verifica favicon"""
        favicon = soup.find('link', rel='icon') or soup.find('link', rel='shortcut icon')
        
        return {
            'name': 'favicon',
            'pass': bool(favicon),
            'value': favicon.get('href', '')[:50] if favicon else 'No Favicon',
            'message': 'Favicon presente' if favicon else 'Falta favicon'
        }
    
    def check_viewport(self, soup: BeautifulSoup) -> Dict:
        """Verifica viewport responsive"""
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        
        return {
            'name': 'responsive_viewport',
            'pass': bool(viewport),
            'value': viewport.get('content', '')[:50] if viewport else 'No Viewport',
            'message': 'Viewport configurado' if viewport else 'Falta viewport'
        }
    
    def check_images_alt(self, soup: BeautifulSoup) -> Dict:
        """Verifica que todas las imágenes tengan ALT"""
        images = soup.find_all('img')
        total = len(images)
        without_alt = 0
        
        for img in images:
            alt = img.get('alt', '').strip()
            if not alt:
                without_alt += 1
        
        return {
            'name': 'image_alt_text',
            'pass': without_alt == 0,
            'value': f"{total} imágenes, {without_alt} sin ALT",
            'message': f"Todos con ALT" if without_alt == 0 else f"{without_alt} imágenes sin ALT"
        }
    
    def check_images_webp(self, soup: BeautifulSoup) -> Dict:
        """Verifica que las imágenes estén en WebP"""
        images = soup.find_all('img')
        total = len(images)
        webp_count = 0
        
        for img in images:
            src = img.get('src', '')
            if src.lower().endswith('.webp'):
                webp_count += 1
        
        return {
            'name': 'image_webp',
            'pass': webp_count == total if total > 0 else True,
            'value': f"{webp_count}/{total} en WebP",
            'message': 'Todas en WebP' if webp_count == total else f"{total - webp_count} no son WebP"
        }
    
    def check_cookie_policy(self, soup: BeautifulSoup, url: str) -> Dict:
        """Verifica aviso de cookies"""
        # Buscar enlaces a políticas de cookies
        links = soup.find_all('a', href=True)
        cookie_links = [l for l in links if 'cookie' in l.get('href', '').lower() or 'cookie' in l.get_text().lower()]
        
        # Buscar banner de cookies
        cookie_banner = soup.find('div', class_=lambda x: x and 'cookie' in x.lower()) if soup else None
        
        return {
            'name': 'cookie_policy',
            'pass': len(cookie_links) > 0 or cookie_banner is not None,
            'value': f"{len(cookie_links)} enlaces encontrados",
            'message': 'Política de cookies presente' if len(cookie_links) > 0 else 'Falta política de cookies'
        }
    
    def check_privacy_policy(self, soup: BeautifulSoup, url: str) -> Dict:
        """Verifica políticas de privacidad"""
        links = soup.find_all('a', href=True)
        privacy_links = [l for l in links if 'privacy' in l.get('href', '').lower() or 'privacidad' in l.get('href', '').lower()]
        
        return {
            'name': 'privacy_policy',
            'pass': len(privacy_links) > 0,
            'value': f"{len(privacy_links)} enlaces encontrados",
            'message': 'Política de privacidad presente' if len(privacy_links) > 0 else 'Falta política de privacidad'
        }
    
    def check_contact_info(self, soup: BeautifulSoup) -> Dict:
        """Verifica información de contacto"""
        # Buscar enlaces de contacto
        links = soup.find_all('a', href=True)
        contact_links = [l for l in links if 'contact' in l.get('href', '').lower() or 'contacto' in l.get('href', '').lower()]
        
        # Buscar teléfono o email
        text = soup.get_text()
        has_phone = any(c.isdigit() for c in text) and ('tel' in text.lower() or 'phone' in text.lower())
        has_email = '@' in text
        
        return {
            'name': 'contact_info',
            'pass': len(contact_links) > 0 or has_phone or has_email,
            'value': f"{len(contact_links)} enlaces de contacto",
            'message': 'Contacto presente' if len(contact_links) > 0 else 'Falta información de contacto'
        }
    
    def check_google_analytics(self, soup: BeautifulSoup) -> Dict:
        """Verifica Google Analytics"""
        scripts = soup.find_all('script')
        ga_found = False
        
        for script in scripts:
            src = script.get('src', '')
            content = script.string or ''
            
            if 'google-analytics' in src or 'googletagmanager' in src or 'gtag' in content or 'ga(' in content:
                ga_found = True
                break
        
        return {
            'name': 'google_analytics',
            'pass': ga_found,
            'value': 'Google Analytics detectado' if ga_found else 'No detectado',
            'message': 'GA configurado' if ga_found else 'Falta Google Analytics'
        }
    
    def check_social_links(self, soup: BeautifulSoup) -> Dict:
        """Verifica redes sociales en footer"""
        footer = soup.find('footer')
        if not footer:
            return {
                'name': 'social_links_footer',
                'pass': False,
                'value': 'Sin footer',
                'message': 'No se encontró footer'
            }
        
        social_domains = ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'tiktok']
        links = footer.find_all('a', href=True)
        social_links = [l for l in links if any(sd in l.get('href', '').lower() for sd in social_domains)]
        
        return {
            'name': 'social_links_footer',
            'pass': len(social_links) > 0,
            'value': f"{len(social_links)} enlaces sociales",
            'message': f"{len(social_links)} redes sociales en footer" if social_links else 'Sin redes sociales en footer'
        }
    
    def check_portfolio_link(self, soup: BeautifulSoup) -> Dict:
        """Verifica portfolio en footer"""
        footer = soup.find('footer')
        if not footer:
            return {
                'name': 'portfolio_link',
                'pass': False,
                'value': 'Sin footer',
                'message': 'No se encontró footer'
            }
        
        links = footer.find_all('a', href=True)
        portfolio_links = [l for l in links if 'selvaggiesteban' in l.get('href', '').lower() or 'portfolio' in l.get('href', '').lower()]
        
        return {
            'name': 'portfolio_link',
            'pass': len(portfolio_links) > 0,
            'value': f"{len(portfolio_links)} enlaces de portfolio",
            'message': 'Portfolio en footer' if portfolio_links else 'Falta portfolio en footer'
        }
    
    def check_faq(self, soup: BeautifulSoup) -> Dict:
        """Verifica FAQ"""
        # Buscar elementos de FAQ
        faq_sections = soup.find_all(['section', 'div'], class_=lambda x: x and 'faq' in str(x).lower())
        faq_headers = soup.find_all(['h2', 'h3'], string=lambda x: x and ('pregunta' in x.lower() or 'frecuente' in x.lower() or 'faq' in x.lower()))
        
        # Buscar elementos details/summary (FAQ HTML nativo)
        details = soup.find_all('details')
        
        return {
            'name': 'faq_present',
            'pass': len(faq_sections) > 0 or len(faq_headers) > 0 or len(details) > 0,
            'value': f"{len(faq_sections)} secciones, {len(details)} details",
            'message': 'FAQ presente' if len(faq_sections) > 0 or len(details) > 0 else 'Sin FAQ'
        }
    
    def verify_page(self, url: str) -> Dict:
        """Verifica todos los requisitos en una página"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            checks = [
                self.check_meta_title(soup),
                self.check_meta_description(soup),
                self.check_h1(soup),
                self.check_h1_not_equals_title(soup),
                self.check_schema(soup),
                self.check_og_image(soup),
                self.check_favicon(soup),
                self.check_viewport(soup),
                self.check_images_alt(soup),
                self.check_images_webp(soup),
                self.check_cookie_policy(soup, url),
                self.check_privacy_policy(soup, url),
                self.check_contact_info(soup),
                self.check_google_analytics(soup),
                self.check_social_links(soup),
                self.check_portfolio_link(soup),
                self.check_faq(soup),
            ]
            
            # Calcular estadísticas
            total = len(checks)
            passed = sum(1 for c in checks if c['pass'])
            failed = total - passed
            
            return {
                'url': url,
                'total_checks': total,
                'passed': passed,
                'failed': failed,
                'score': round((passed / total) * 100, 1) if total > 0 else 0,
                'checks': checks
            }
            
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'total_checks': 0,
                'passed': 0,
                'failed': 0,
                'score': 0,
                'checks': []
            }
    
    def verify_urls(self, urls: List[str]):
        """Verifica múltiples URLs"""
        print(f"=" * 60)
        print(f"VERIFICANDO SEO: {len(urls)} páginas")
        print(f"=" * 60)
        
        for i, url in enumerate(urls):
            print(f"[{i+1}/{len(urls)}] {url}")
            
            result = self.verify_page(url)
            self.results.append(result)
            
            print(f"  Score: {result['score']}% ({result['passed']}/{result['total_checks']})")
            
            time.sleep(self.delay)
        
        # Resumen final
        if self.results:
            avg_score = sum(r['score'] for r in self.results) / len(self.results)
            print(f"\n{'=' * 60}")
            print(f"RESUMEN")
            print(f"{'=' * 60}")
            print(f"Total páginas: {len(self.results)}")
            print(f"Score promedio: {avg_score:.1f}%")
            print(f"{'=' * 60}")
    
    def save_to_json(self, filename: str = 'seo_results.json'):
        """Guarda resultados en JSON"""
        output = {
            'base_url': self.base_url,
            'total_pages': len(self.results),
            'results': self.results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\nResultados guardados en: {filename}")
    
    def save_to_csv(self, filename: str = 'seo_results.csv'):
        """Guarda resultados en CSV"""
        if not self.results:
            return
        
        # Obtener todos los check names
        all_checks = set()
        for r in self.results:
            for c in r.get('checks', []):
                all_checks.add(c['name'])
        
        fieldnames = ['url', 'score', 'passed', 'failed'] + sorted(all_checks)
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for r in self.results:
                row = {
                    'url': r['url'],
                    'score': r['score'],
                    'passed': r['passed'],
                    'failed': r['failed']
                }
                
                for c in r.get('checks', []):
                    row[c['name']] = '✅' if c['pass'] else '❌'
                
                writer.writerow(row)
        
        print(f"Resultados guardados en: {filename}")


def load_urls_from_json(filename: str) -> List[str]:
    """Carga URLs desde un archivo JSON (generado por site_mapper.py)"""
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return [page['url'] for page in data.get('pages', [])]


def main():
    parser = argparse.ArgumentParser(
        description='SEO Verifier - Verifica requisitos SEO en páginas web'
    )
    parser.add_argument('urls', nargs='*', help='URLs a verificar')
    parser.add_argument('-f', '--file', help='Archivo JSON con URLs (generado por site_mapper.py)')
    parser.add_argument('-d', '--delay', type=float, default=0.5,
                        help='Delay entre peticiones (default: 0.5)')
    parser.add_argument('-o', '--output', default='seo_results',
                        help='Nombre base del archivo de salida (default: seo_results)')
    
    args = parser.parse_args()
    
    # Obtener URLs
    urls = []
    if args.file:
        urls = load_urls_from_json(args.file)
    elif args.urls:
        urls = args.urls
    else:
        print("Error: Especifica URLs o un archivo JSON con URLs")
        return
    
    if not urls:
        print("No se encontraron URLs para verificar")
        return
    
    # Crear verificador
    verifier = SEOVerifier(
        base_url=urls[0] if urls else 'https://example.com',
        delay=args.delay
    )
    
    verifier.verify_urls(urls)
    
    # Evitar doble extensión
    output_base = args.output
    if output_base.endswith('.json'):
        output_base = output_base[:-5]
    if output_base.endswith('.csv'):
        output_base = output_base[:-4]
    
    verifier.save_to_json(f'{output_base}.json')
    verifier.save_to_csv(f'{output_base}.csv')


if __name__ == '__main__':
    main()
