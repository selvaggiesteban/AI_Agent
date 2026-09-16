import sys
from core.paths import PROJECT_ROOT
sys.path.append(str(PROJECT_ROOT / "scripts" / "social_media_manager"))

import asyncio
import os
import re
from playwright.async_api import async_playwright
from core.rpa_bot import BaseBot

PROMPT_WHATSAPP = """
Analizá los siguientes mensajes de un chat de WhatsApp. 
Extraé el Nombre y Apellido de la persona (no el mío, sino el del interlocutor).
Respondé SOLO en formato JSON puro:
{{
  "nombre": "Nombre Apellido"
}}
Si no hay suficiente información, poné "DESCONOCIDO" en el nombre.

MENSAJES:
{contexto}
"""

class WhatsAppBot(BaseBot):
    def __init__(self):
        super().__init__(PROMPT_WHATSAPP)
        self.profile_path = os.path.join(os.environ['LOCALAPPDATA'], r'Google\Chrome\User Data')
        self.profile_name = "Default"

    async def run(self):
        async with async_playwright() as p:
            print(f"[*] Iniciando WhatsApp RPA (Perfil: {self.profile_name})")
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=self.profile_path,
                headless=False,
                args=[f"--profile-directory={self.profile_name}"]
            )
            page = await browser.new_page()
            await page.goto("https://web.whatsapp.com")
            
            print("[!] Esperando carga de WhatsApp Web...")
            try:
                await page.wait_for_selector("div[contenteditable='true'][data-tab='3']", timeout=60000)
                print("✅ WhatsApp Web Cargado.")
            except:
                print("❌ Timeout carga WhatsApp.")
                await browser.close()
                return

            while True:
                try:
                    chats = await page.query_selector_all("span[title^='+'], span[title^='0'], span[title^='1']")
                    
                    for chat in chats:
                        title = await chat.get_attribute("title")
                        if title and re.search(r'\d', title):
                            print(f"[*] Analizando prospecto numérico: {title}")
                            
                            await chat.click()
                            await asyncio.sleep(2)

                            bubbles = await page.query_selector_all(".message-in .copyable-text")
                            messages = [await b.inner_text() for b in bubbles[-10:]]
                            
                            if messages:
                                analysis = await self.analyze_content(messages)
                                if analysis and analysis.get('nombre') and analysis['nombre'] != "DESCONOCIDO":
                                    print(f"✨ IA Descubrió Nombre: {analysis['nombre']}")
                                    self.update_lead(title, analysis, "WhatsApp")
                                else:
                                    print("🤷 IA no pudo determinar el nombre.")
                            
                    await asyncio.sleep(10)
                except Exception as e:
                    print(f"Error en loop WhatsApp: {e}")
                    await asyncio.sleep(5)

if __name__ == "__main__":
    bot = WhatsAppBot()
    asyncio.run(bot.run())
