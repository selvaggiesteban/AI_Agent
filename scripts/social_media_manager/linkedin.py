import sys
from core.paths import PROJECT_ROOT
sys.path.append(str(PROJECT_ROOT / "scripts" / "social_media_manager"))

import asyncio
import os
from playwright.async_api import async_playwright
from core.rpa_bot import BaseBot

PROMPT_LINKEDIN = """
Actuá como un analista de prospección para Esteban Selvaggi. 
Analizá los siguientes mensajes de un chat de linkedin.
Extraé el Nombre y Apellido del interlocutor y su empresa si la menciona.
Determiná el nivel de interés comercial (0-100).

MENSAJES:
{contexto}

Respondé SOLO en formato JSON puro:
{{
  "nombre": "...",
  "empresa": "...",
  "interes": 85,
  "resumen": "..."
}}
"""

class LinkedInBot(BaseBot):
    def __init__(self):
        super().__init__(PROMPT_LINKEDIN)
        self.profile_path = os.path.join(os.environ['LOCALAPPDATA'], r'Google\Chrome\User Data')
        self.profile_name = "Default"

    async def run(self):
        async with async_playwright() as p:
            print(f"[*] Iniciando LinkedIn RPA (Perfil: {self.profile_name})")
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=self.profile_path,
                headless=False,
                args=[f"--profile-directory={self.profile_name}"]
            )
            page = await browser.new_page()
            await page.goto("https://www.linkedin.com/messaging/")
            
            print("[!] Esperando carga de Mensajes...")
            try:
                await page.wait_for_selector(".msg-conversations-container", timeout=30000)
                print("✅ Bandeja de LinkedIn cargada.")
            except:
                print("❌ Timeout bandeja LinkedIn.")
                await browser.close()
                return

            threads = await page.query_selector_all(".msg-conversations-container__convo-item")
            for thread in threads[:10]:
                try:
                    await thread.click()
                    await asyncio.sleep(3)
                    
                    profile_link_elem = await page.query_selector(".msg-entity-lockup__link")
                    profile_url = await profile_link_elem.get_attribute("href") if profile_link_elem else "Unknown"

                    bubble_elements = await page.query_selector_all(".msg-s-event-listitem__body")
                    messages = [await b.inner_text() for b in bubble_elements[-15:]]
                    
                    if messages:
                        print(f"[*] Analizando chat: {profile_url}")
                        analysis = await self.analyze_content(messages)
                        if analysis and analysis.get('nombre'):
                            self.update_lead(profile_url, analysis, "LinkedIn")
                except Exception as e:
                    print(f"Error thread: {e}")

            await browser.close()
            print("--- Ciclo LinkedIn Finalizado ---")

if __name__ == "__main__":
    bot = LinkedInBot()
    asyncio.run(bot.run())
