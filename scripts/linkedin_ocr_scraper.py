import os
import time
import asyncio
import re
import pandas as pd
import easyocr
import cv2
from datetime import datetime
from playwright.async_api import async_playwright

# Configuraciones
PROFILE_PATH = os.path.join(os.environ.get('LOCALAPPDATA', ''), r'Google\Chrome\User Data')
PROFILE_NAME = "Default"
OUTPUT_DIR = "data/outputs/linkedin"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class LinkedInOCRScraper:
    def __init__(self, keyword, location="Argentina", limit=10):
        self.keyword = keyword
        self.location = location
        self.limit = limit
        self.reader = easyocr.Reader(['es', 'en'], gpu=False) # Inicializar OCR
        self.results = []
        
    async def run(self):
        print(f"[*] Iniciando LinkedIn OCR Scraper para: {self.keyword} en {self.location}")
        
        async with async_playwright() as p:
            # Usar perfil persistente para evitar logins manuales
            try:
                browser = await p.chromium.launch_persistent_context(
                    user_data_dir=PROFILE_PATH,
                    headless=False,
                    args=[f"--profile-directory={self.profile_name}"] if hasattr(self, 'profile_name') else [f"--profile-directory=Default"]
                )
            except Exception as e:
                print(f"❌ Error crítico al lanzar Chrome. Asegúrate de que todas las ventanas de Chrome estén cerradas. Error: {e}")
                return
                
            page = await browser.new_page()
            
            # Construir URL de busqueda
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={urllib.parse.quote(self.keyword)}&location={urllib.parse.quote(self.location)}"
            await page.goto(search_url)
            print("[!] Esperando carga de la página de empleos...")
            
            # Esperar a que cargue la lista izquierda
            try:
                await page.wait_for_selector(".jobs-search-results-list", timeout=15000)
            except Exception as e:
                print(f"❌ Error al cargar empleos: {e}")
                await browser.close()
                return

            jobs_processed = 0
            
            while jobs_processed < self.limit:
                # Obtener las tarjetas de trabajo visibles
                job_cards = await page.query_selector_all(".job-card-container")
                
                if not job_cards or jobs_processed >= len(job_cards):
                    # Intentar hacer scroll para cargar mas
                    print("[*] Haciendo scroll para cargar más empleos...")
                    await page.evaluate("document.querySelector('.jobs-search-results-list').scrollBy(0, 1000)")
                    await asyncio.sleep(2)
                    job_cards = await page.query_selector_all(".job-card-container")
                    if jobs_processed >= len(job_cards):
                        print("[!] No hay más empleos disponibles en esta página.")
                        break

                card = job_cards[jobs_processed]
                try:
                    await card.click()
                    await asyncio.sleep(2) # Esperar a que renderice el panel derecho
                    
                    # 1. Extracción híbrida (DOM para lo fácil)
                    title_elem = await page.query_selector(".jobs-details-top-card__job-title")
                    title = await title_elem.inner_text() if title_elem else "N/A"
                    
                    company_elem = await page.query_selector(".jobs-details-top-card__company-url")
                    company = await company_elem.inner_text() if company_elem else "N/A"
                    
                    # 2. Extracción profunda (OCR en la descripción)
                    desc_container = await page.query_selector(".jobs-description__content")
                    extracted_text = ""
                    emails = []
                    links = []
                    
                    if desc_container:
                        # Tomar screenshot del area de descripcion
                        screenshot_path = f"temp_job_{jobs_processed}.png"
                        await desc_container.screenshot(path=screenshot_path)
                        
                        # Pasar OCR
                        print(f"[*] Escaneando visualmente oferta: {title} ({company})")
                        ocr_result = self.reader.readtext(screenshot_path, detail=0, paragraph=True)
                        extracted_text = " ".join(ocr_result)
                        
                        # Buscar correos y webs
                        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', extracted_text)
                        links = re.findall(r'(https?://\S+)', extracted_text)
                        
                        os.remove(screenshot_path) # Limpiar temp
                        
                    job_data = {
                        "Puesto": title.strip(),
                        "Empresa": company.strip(),
                        "Ubicacion": self.location,
                        "Emails_Extraidos": ", ".join(list(set(emails))),
                        "Links_Extraidos": ", ".join(list(set(links))),
                        "Descripcion_OCR": extracted_text,
                        "Fecha_Extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    
                    self.results.append(job_data)
                    jobs_processed += 1
                    print(f"✅ Procesado: {jobs_processed}/{self.limit}")
                    
                except Exception as e:
                    print(f"⚠️ Error al procesar tarjeta: {e}")
                    jobs_processed += 1
            
            await browser.close()
            self.export_results()

    def export_results(self):
        if not self.results:
            print("No hay resultados para exportar.")
            return
            
        df = pd.DataFrame(self.results)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_kw = self.keyword.replace(" ", "_")
        
        csv_path = os.path.join(OUTPUT_DIR, f"linkedin_{safe_kw}_{timestamp}.csv")
        excel_path = os.path.join(OUTPUT_DIR, f"linkedin_{safe_kw}_{timestamp}.xlsx")
        json_path = os.path.join(OUTPUT_DIR, f"linkedin_{safe_kw}_{timestamp}.json")
        
        df.to_csv(csv_path, index=False, encoding='utf-8')
        df.to_excel(excel_path, index=False)
        df.to_json(json_path, orient='records', force_ascii=False, indent=4)
        
        print(f"\n=== EXPORTACIÓN EXITOSA ===")
        print(f"Exportado a CSV: {csv_path}")
        print(f"Exportado a Excel: {excel_path}")
        print(f"Exportado a JSON: {json_path}")

if __name__ == "__main__":
    import urllib.parse
    # Configuración de prueba
    KEYWORD = "Diseñador Web"
    LOCATION = "Argentina"
    LIMIT = 5 # Extraer 5 de prueba
    
    scraper = LinkedInOCRScraper(KEYWORD, LOCATION, LIMIT)
    asyncio.run(scraper.run())
