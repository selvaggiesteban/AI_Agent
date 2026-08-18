import requests
from bs4 import BeautifulSoup
import csv
import time
import random
from fake_useragent import UserAgent
import concurrent.futures
from typing import List, Dict, Any

def get_session() -> requests.Session:
    """Configura y retorna una sesión de requests con cabeceras aleatorias"""
    session = requests.Session()
    ua = UserAgent()
    session.headers.update({
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3',
        'Referer': 'https://es.kompass.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    })
    return session

def extract_page_data(url: str, session: requests.Session) -> List[Dict[str, str]]:
    """Extrae datos de empresas de una URL específica de Kompass"""
    print(f"Accediendo a la URL: {url}")
    try:
        response = session.get(url, timeout=30)
        if response.status_code != 200:
            print(f"Error al acceder a la página. Código de estado: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error en la petición: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    company_containers = soup.find_all('div', class_='prod_list')
    results = []

    for container in company_containers:
        name = container.find('h2').text.strip() if container.find('h2') else ''
        location = container.find('span', class_='placeText')
        location = location.text.strip() if location else ''
        summary = container.find('p', class_='product-summary')
        summary = summary.find('span', class_='text').text.strip() if summary else ''
        products = container.find('ul')
        products_list = [li.text.strip() for li in products.find_all('li')] if products else []
        phone = container.find('input', id=lambda x: x and x.startswith('freePhone--'))
        phone_val = phone['value'] if phone else ''
        website = container.find('div', class_='companyWeb')
        website_url = website.find('a')['href'] if website and website.find('a') else ''
        
        results.append({
            'Nombre': name,
            'Ubicación': location,
            'Resumen': summary,
            'Productos': ', '.join(products_list),
            'phone': phone_val,
            'Sitio Web': website_url
        })
    
    return results

def extract_kompass_data(sector: str, sector_id: str, num_pages: int) -> List[Dict[str, str]]:
    """Coordina el raspado multihilo de múltiples páginas de Kompass"""
    base_url = f"https://es.kompass.com/s/{sector}/{sector_id}/page-"
    session = get_session()
    
    all_results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for page in range(1, num_pages + 1):
            url = f"{base_url}{page}/"
            futures.append(executor.submit(extract_page_data, url, session))
            time.sleep(random.uniform(2, 5))  # Pausa entre solicitudes
        
        for future in concurrent.futures.as_completed(futures):
            try:
                all_results.extend(future.result())
            except Exception as e:
                print(f"Error procesando hilo: {e}")
    
    return all_results

def save_to_csv(data: List[Dict[str, str]], filename: str) -> None:
    """Guarda los datos extraídos en un archivo CSV"""
    if not data:
        print("No hay datos para guardar.")
        return
    with open(filename, 'w', newline='', encoding='utf-8') as csv_file:
        fields = ['Nombre', 'Ubicación', 'Resumen', 'Productos', 'phone', 'Sitio Web']
        writer = csv.DictWriter(csv_file, fieldnames=fields)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

if __name__ == "__main__":
    # Uso del script
    target_sector = "construccion"
    target_sector_id = "09"
    total_pages = 2

    results = extract_kompass_data(target_sector, target_sector_id, total_pages)
    save_to_csv(results, 'empresas_construccion_kompass.csv')
    print(f"Se han extraído {len(results)} empresas y guardado en 'empresas_construccion_kompass.csv'")
