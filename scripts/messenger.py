import sys
from core.paths import PROJECT_ROOT
sys.path.append(str(PROJECT_ROOT / "scripts" / "social_media_manager"))

import asyncio
import os
from playwright.async_api import async_playwright
from core.rpa_bot import BaseBot

PROMPT_MESSENGER = """
Act as a commercial prospecting expert for Esteban Selvaggi.
Analyze the following messages from a Facebook Messenger chat.
Extract the real First and Last Name of the interlocutor.
Determine their interest in professional services (0-100).

MESSAGES:
{contexto}

Respond ONLY in pure JSON format:
{{
  "nombre": "...",
  "interes": 65,
  "resumen_comercial": "..."
}}
"""

class MessengerBot(BaseBot):
    def __init__(self):
        super().__init__(PROMPT_MESSENGER)
        self.profile_path = os.path.join(os.environ['LOCALAPPDATA'], r'Google\Chrome\User Data')
        self.profile_name = "Default"

    async def run(self):
        async with async_playwright() as p:
            print(f"[*] Starting Messenger RPA (Profile: {self.profile_name})")
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=self.profile_path,
                headless=False,
                args=[f"--profile-directory={self.profile_name}"]
            )
            page = await browser.new_page()
            await page.goto("https://www.facebook.com/messages/t/")

            print("[!] Waiting for Messenger to load...")
            try:
                await page.wait_for_selector("div[role='grid']", timeout=45000)
                print("✅ Messenger inbox loaded.")
            except:
                print("❌ Messenger inbox timeout.")
                await browser.close()
                return

            chats = await page.query_selector_all("div[role='row']")
            for chat in chats[:8]:
                try:
                    await chat.click()
                    await asyncio.sleep(4)

                    name_elem = await page.query_selector("span[style*='-webkit-line-clamp: 1']")
                    fb_name = await name_elem.inner_text() if name_elem else "Unknown"

                    bubble_elements = await page.query_selector_all("div[dir='auto'][role='none']")
                    messages = []
                    for b in bubble_elements[-15:]:
                        text = await b.inner_text()
                        if len(text) > 2:
                            messages.append(text.strip())

                    if messages:
                        print(f"[*] Analyzing chat with: {fb_name}")
                        analysis = await self.analyze_content(messages)
                        if analysis and analysis.get('nombre'):
                            self.update_lead(fb_name, analysis, "Messenger")
                except Exception as e:
                    print(f"Messenger chat error: {e}")

            await browser.close()
            print("--- Messenger Cycle Finished ---")

if __name__ == "__main__":
    bot = MessengerBot()
    asyncio.run(bot.run())
