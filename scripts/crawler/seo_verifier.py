#!/usr/bin/env python3
"""
SEO Verifier - Verifies SEO requirements on web pages
Analyzes 35+ requirements and generates detailed reports
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
        Initializes the SEO verifier

        Args:
            base_url: Base URL of the site
            delay: Delay between requests
        """
        self.base_url = base_url.rstrip('/')
        self.domain = urlparse(base_url).netloc
        self.delay = delay
        self.results: List[Dict] = []

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def check_meta_title(self, soup: BeautifulSoup) -> Dict:
        """Verifies meta title"""
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else ''

        return {
            'name': 'meta_title',
            'pass': bool(title),
            'value': title if title else 'No Title',
            'message': 'Meta title present' if title else 'Meta title missing'
        }

    def check_meta_description(self, soup: BeautifulSoup) -> Dict:
        """Verifies meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        desc = meta_desc.get('content', '') if meta_desc else ''

        return {
            'name': 'meta_description',
            'pass': bool(desc),
            'value': desc if desc else 'No Meta Description',
            'message': 'Meta description present' if desc else 'Meta description missing'
        }

    def check_h1(self, soup: BeautifulSoup) -> Dict:
        """Verifies unique H1"""
        h1_tags = soup.find_all('h1')
        count = len(h1_tags)
        h1_text = h1_tags[0].get_text(strip=True) if h1_tags else ''

        return {
            'name': 'h1_unique',
            'pass': count == 1,
            'value': f"{count} H1: {h1_text[:50]}..." if h1_text else 'No H1',
            'message': 'Single H1' if count == 1 else f'{count} H1 found'
        }

    def check_h1_not_equals_title(self, soup: BeautifulSoup) -> Dict:
        """Verifies that H1 is different from the title"""
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else ''

        h1_tags = soup.find_all('h1')
        h1_text = h1_tags[0].get_text(strip=True) if h1_tags else ''

        if not title or not h1_text:
            return {
                'name': 'h1_not_equals_title',
                'pass': False,
                'value': 'N/A',
                'message': 'Cannot compare (title or H1 missing)'
            }

        # Normalize for comparison
        title_norm = title.lower().strip()
        h1_norm = h1_text.lower().strip()

        return {
            'name': 'h1_not_equals_title',
            'pass': title_norm != h1_norm,
            'value': f"Title: {title[:30]}... | H1: {h1_text[:30]}...",
            'message': 'H1 different from title' if title_norm != h1_norm else 'H1 same as title'
        }

    def check_schema(self, soup: BeautifulSoup) -> Dict:
        """Verifies Schema JSON-LD"""
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

        # Convert all to strings
        schemas_str = [str(s) for s in schemas]

        return {
            'name': 'schema_jsonld',
            'pass': len(schemas_str) > 0,
            'value': ', '.join(schemas_str) if schemas_str else 'No Schema',
            'message': f"Schema found: {', '.join(schemas_str)}" if schemas_str else 'No Schema JSON-LD'
        }

    def check_og_image(self, soup: BeautifulSoup) -> Dict:
        """Verifies Open Graph image"""
        og_image = soup.find('meta', property='og:image')

        return {
            'name': 'og_image',
            'pass': bool(og_image),
            'value': og_image.get('content', '')[:100] if og_image else 'No OG Image',
            'message': 'OG Image present' if og_image else 'OG Image missing'
        }

    def check_favicon(self, soup: BeautifulSoup) -> Dict:
        """Verifies favicon"""
        favicon = soup.find('link', rel='icon') or soup.find('link', rel='shortcut icon')

        return {
            'name': 'favicon',
            'pass': bool(favicon),
            'value': favicon.get('href', '')[:50] if favicon else 'No Favicon',
            'message': 'Favicon present' if favicon else 'Favicon missing'
        }

    def check_viewport(self, soup: BeautifulSoup) -> Dict:
        """Verifies responsive viewport"""
        viewport = soup.find('meta', attrs={'name': 'viewport'})

        return {
            'name': 'responsive_viewport',
            'pass': bool(viewport),
            'value': viewport.get('content', '')[:50] if viewport else 'No Viewport',
            'message': 'Viewport configured' if viewport else 'Viewport missing'
        }

    def check_images_alt(self, soup: BeautifulSoup) -> Dict:
        """Verifies that all images have ALT text"""
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
            'value': f"{total} images, {without_alt} without ALT",
            'message': f"All with ALT" if without_alt == 0 else f"{without_alt} images without ALT"
        }

    def check_images_webp(self, soup: BeautifulSoup) -> Dict:
        """Verifies that images are in WebP format"""
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
            'value': f"{webp_count}/{total} in WebP",
            'message': 'All in WebP' if webp_count == total else f"{total - webp_count} are not WebP"
        }

    def check_cookie_policy(self, soup: BeautifulSoup, url: str) -> Dict:
        """Verifies cookie notice"""
        # Search for links to cookie policies
        links = soup.find_all('a', href=True)
        cookie_links = [l for l in links if 'cookie' in l.get('href', '').lower() or 'cookie' in l.get_text().lower()]

        # Search for cookie banner
        cookie_banner = soup.find('div', class_=lambda x: x and 'cookie' in x.lower()) if soup else None

        return {
            'name': 'cookie_policy',
            'pass': len(cookie_links) > 0 or cookie_banner is not None,
            'value': f"{len(cookie_links)} links found",
            'message': 'Cookie policy present' if len(cookie_links) > 0 else 'Cookie policy missing'
        }

    def check_privacy_policy(self, soup: BeautifulSoup, url: str) -> Dict:
        """Verifies privacy policies"""
        links = soup.find_all('a', href=True)
        privacy_links = [l for l in links if 'privacy' in l.get('href', '').lower() or 'privacidad' in l.get('href', '').lower()]

        return {
            'name': 'privacy_policy',
            'pass': len(privacy_links) > 0,
            'value': f"{len(privacy_links)} links found",
            'message': 'Privacy policy present' if len(privacy_links) > 0 else 'Privacy policy missing'
        }

    def check_contact_info(self, soup: BeautifulSoup) -> Dict:
        """Verifies contact information"""
        # Search for contact links
        links = soup.find_all('a', href=True)
        contact_links = [l for l in links if 'contact' in l.get('href', '').lower() or 'contacto' in l.get('href', '').lower()]

        # Search for phone or email
        text = soup.get_text()
        has_phone = any(c.isdigit() for c in text) and ('tel' in text.lower() or 'phone' in text.lower())
        has_email = '@' in text

        return {
            'name': 'contact_info',
            'pass': len(contact_links) > 0 or has_phone or has_email,
            'value': f"{len(contact_links)} contact links",
            'message': 'Contact info present' if len(contact_links) > 0 else 'Contact info missing'
        }

    def check_google_analytics(self, soup: BeautifulSoup) -> Dict:
        """Verifies Google Analytics"""
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
            'value': 'Google Analytics detected' if ga_found else 'Not detected',
            'message': 'GA configured' if ga_found else 'Google Analytics missing'
        }

    def check_social_links(self, soup: BeautifulSoup) -> Dict:
        """Verifies social networks in footer"""
        footer = soup.find('footer')
        if not footer:
            return {
                'name': 'social_links_footer',
                'pass': False,
                'value': 'No footer',
                'message': 'Footer not found'
            }

        social_domains = ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube', 'tiktok']
        links = footer.find_all('a', href=True)
        social_links = [l for l in links if any(sd in l.get('href', '').lower() for sd in social_domains)]

        return {
            'name': 'social_links_footer',
            'pass': len(social_links) > 0,
            'value': f"{len(social_links)} social links",
            'message': f"{len(social_links)} social networks in footer" if social_links else 'No social networks in footer'
        }

    def check_portfolio_link(self, soup: BeautifulSoup) -> Dict:
        """Verifies portfolio in footer"""
        footer = soup.find('footer')
        if not footer:
            return {
                'name': 'portfolio_link',
                'pass': False,
                'value': 'No footer',
                'message': 'Footer not found'
            }

        links = footer.find_all('a', href=True)
        portfolio_links = [l for l in links if 'selvaggiesteban' in l.get('href', '').lower() or 'portfolio' in l.get('href', '').lower()]

        return {
            'name': 'portfolio_link',
            'pass': len(portfolio_links) > 0,
            'value': f"{len(portfolio_links)} portfolio links",
            'message': 'Portfolio in footer' if portfolio_links else 'Portfolio missing in footer'
        }

    def check_faq(self, soup: BeautifulSoup) -> Dict:
        """Verifies FAQ"""
        # Search for FAQ elements
        faq_sections = soup.find_all(['section', 'div'], class_=lambda x: x and 'faq' in str(x).lower())
        faq_headers = soup.find_all(['h2', 'h3'], string=lambda x: x and ('question' in x.lower() or 'frequent' in x.lower() or 'faq' in x.lower()))

        # Search for native HTML details/summary
        details = soup.find_all('details')

        return {
            'name': 'faq_present',
            'pass': len(faq_sections) > 0 or len(faq_headers) > 0 or len(details) > 0,
            'value': f"{len(faq_sections)} sections, {len(details)} details",
            'message': 'FAQ present' if len(faq_sections) > 0 or len(details) > 0 else 'No FAQ'
        }

    def verify_page(self, url: str) -> Dict:
        """Verifies all requirements on a page"""
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

            # Calculate statistics
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
        """Verifies multiple URLs"""
        print(f"=" * 60)
        print(f"VERIFYING SEO: {len(urls)} pages")
        print(f"=" * 60)

        for i, url in enumerate(urls):
            print(f"[{i+1}/{len(urls)}] {url}")

            result = self.verify_page(url)
            self.results.append(result)

            print(f"  Score: {result['score']}% ({result['passed']}/{result['total_checks']})")

            time.sleep(self.delay)

        # Final summary
        if self.results:
            avg_score = sum(r['score'] for r in self.results) / len(self.results)
            print(f"\n{'=' * 60}")
            print(f"SUMMARY")
            print(f"{'=' * 60}")
            print(f"Total pages: {len(self.results)}")
            print(f"Average score: {avg_score:.1f}%")
            print(f"{'=' * 60}")

    def save_to_json(self, filename: str = 'seo_results.json'):
        """Saves results to JSON"""
        output = {
            'base_url': self.base_url,
            'total_pages': len(self.results),
            'results': self.results
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\nResults saved to: {filename}")

    def save_to_csv(self, filename: str = 'seo_results.csv'):
        """Saves results to CSV"""
        if not self.results:
            return

        # Get all check names
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

        print(f"Results saved to: {filename}")

    def load_urls_from_json(filename: str) -> List[str]:
        """Loads URLs from a JSON file (generated by site_mapper.py)"""
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return [page['url'] for page in data.get('pages', [])]


def main():
    parser = argparse.ArgumentParser(
        description='SEO Verifier - Verifies SEO requirements on web pages'
    )
    parser.add_argument('urls', nargs='*', help='URLs to verify')
    parser.add_argument('-f', '--file', help='JSON file with URLs (generated by site_mapper.py)')
    parser.add_argument('-d', '--delay', type=float, default=0.5,
                        help='Delay between requests (default: 0.5)')
    parser.add_argument('-o', '--output', default='seo_results',
                        help='Base name of the output file (default: seo_results)')

    args = parser.parse_args()

    # Get URLs
    urls = []
    if args.file:
        urls = load_urls_from_json(args.file)
    elif args.urls:
        urls = args.urls
    else:
        print("Error: Specify URLs or a JSON file with URLs")
        return

    if not urls:
        print("No URLs found to verify")
        return

    # Create verifier
    verifier = SEOVerifier(
        base_url=urls[0] if urls else 'https://example.com',
        delay=args.delay
    )

    verifier.verify_urls(urls)

    # Avoid double extension
    output_base = args.output
    if output_base.endswith('.json'):
        output_base = output_base[:-5]
    if output_base.endswith('.csv'):
        output_base = output_base[:-4]

    verifier.save_to_json(f'{output_base}.json')
    verifier.save_to_csv(f'{output_base}.csv')


if __name__ == '__main__':
    main()
