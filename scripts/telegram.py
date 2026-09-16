import sys
from core.paths import PROJECT_ROOT
sys.path.append(str(PROJECT_ROOT / "scripts" / "social_media_manager"))

import asyncio
import os
from playwright.async_api import async_playwright
from core.rpa_bot import BaseBot

PROMPT_TELEGRAM = """
Actuá como un analista de prospección estratégica para Esteban Selvaggi. 
Analizá los siguientes mensajes de un chat de Telegram.
Extraé el Nombre y Apellido real del interlocutor y su alias si lo tiene.
Determiná su interés comercial o necesidad técnica (0-100).

MENSAJES:
{contexto}

Respondé SOLO en formato JSON puro:
{{
  "nombre": "...",
  "alias": "...",
  "interes": 75,
  "analisis_resumen": "..."
}}
"""

class TelegramBot(BaseBot):
    def __init__(self):
        super().__init__(PROMPT_TELEGRAM)
        self.profile_path = os.path.join(os.environ['LOCALAPPDATA'], r'Google\Chrome\User Data')
        self.profile_name = "Default"

    async def run(self):
        async with async_playwright() as p:
            print(f"[*] Iniciando Telegram RPA (Perfil: {self.profile_name})")
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=self.profile_path,
                headless=False,
                args=[f"--profile-directory={self.profile_name}"]
            )
            page = await browser.new_page()
            await page.goto("https://web.telegram.org/a/")
            
            print("[!] Esperando carga de Telegram Web...")
            try:
                await page.wait_for_selector(".ListItem-button", timeout=60000)
                print("✅ Telegram Web Cargado.")
            except:
                print("❌ Timeout carga Telegram.")
                await browser.close()
                return

            chats = await page.query_selector_all(".ListItem-button")
            for chat in chats[:10]:
                try:
                    name_elem = await chat.query_selector(".title > span")
                    display_name = await name_elem.inner_text() if name_elem else "Unknown"
                    
                    print(f"[*] Revisando chat: {display_name}")
                    await chat.click()
                    await asyncio.sleep(4)
                    
                    bubble_elements = await page.query_selector_all(".message-content-wrapper")
                    messages = []
                    for b in bubble_elements[-15:]:
                        text = await b.inner_text()
                        if len(text) > 3:
                            messages.append(text.strip())
                    
                    if messages:
                        print(f"    [+] Analizando contenido con IA...")
                        analysis = await self.analyze_content(messages)
                        if analysis and analysis.get('nombre'):
                            self.update_lead(display_name, analysis, "Telegram")
                except Exception as e:
                    print(f"Error chat Telegram: {e}")

            await browser.close()
            print("--- Ciclo Telegram Finalizado ---")

if __name__ == "__main__":
    bot = TelegramBot()
    asyncio.run(bot.run())
