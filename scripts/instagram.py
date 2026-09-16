import sys
from core.paths import PROJECT_ROOT
sys.path.append(str(PROJECT_ROOT / "scripts" / "social_media_manager"))

import asyncio
import os
from playwright.async_api import async_playwright
from core.rpa_bot import BaseBot

PROMPT_INSTAGRAM = """
Actuá como un experto en Social Selling para Esteban Selvaggi. 
Analizá los siguientes mensajes de un chat de Instagram Direct.
Extraé el Nombre y Apellido real del interlocutor (el usuario de IG suele ser un alias).
Respondé SOLO en formato JSON puro:
{{
  "nombre": "...",
  "interes": 70,
  "contexto_resumen": "..."
}}

MENSAJES:
{contexto}
"""

class InstagramBot(BaseBot):
    def __init__(self):
        super().__init__(PROMPT_INSTAGRAM)
        self.profile_path = os.path.join(os.environ['LOCALAPPDATA'], r'Google\Chrome\User Data')
        self.profile_name = "Default"

    async def run(self):
        async with async_playwright() as p:
            print(f"[*] Iniciando Instagram RPA (Perfil: {self.profile_name})")
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=self.profile_path,
                headless=False,
                args=[f"--profile-directory={self.profile_name}"]
            )
            page = await browser.new_page()
            await page.goto("https://www.instagram.com/direct/inbox/")
            
            try:
                await page.wait_for_selector("div[role='listitem']", timeout=15000)
            except:
                print("❌ Timeout bandeja IG.")
                await browser.close()
                return

            chats = await page.query_selector_all("div[role='listitem']")
            for chat in chats[:5]:
                try:
                    await chat.click()
                    await asyncio.sleep(3)
                    user_header = await page.query_selector("header h1, header span")
                    username = (await user_header.inner_text()).strip().split('\n')[0] if user_header else "unknown"
                    
                    bubble_elements = await page.query_selector_all("div[dir='auto'] span")
                    messages = [await b.inner_text() for b in bubble_elements[-15:]]
                    
                    if messages:
                        analysis = await self.analyze_content(messages)
                        if analysis:
                            self.update_lead(username, analysis, "Instagram")
                except Exception as e:
                    print(f"Error chat: {e}")

            await browser.close()

if __name__ == "__main__":
    bot = InstagramBot()
    asyncio.run(bot.run())
