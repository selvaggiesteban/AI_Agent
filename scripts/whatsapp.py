import sys
from core.paths import PROJECT_ROOT
sys.path.append(str(PROJECT_ROOT / "scripts" / "social_media_manager"))

import asyncio
import os
import re
from playwright.async_api import async_playwright
from core.rpa_bot import BaseBot

PROMPT_WHATSAPP = """
Analyze the following messages from a WhatsApp chat.
Extract the First and Last Name of the person (not mine, but the interlocutor's).
Respond ONLY in pure JSON format:
{{
  "nombre": "First Name Last Name"
}}
If there is not enough information, put "UNKNOWN" in the name.

MESSAGES:
{contexto}
"""

class WhatsAppBot(BaseBot):
    def __init__(self):
        super().__init__(PROMPT_WHATSAPP)
        self.profile_path = os.path.join(os.environ['LOCALAPPDATA'], r'Google\Chrome\User Data')
        self.profile_name = "Default"

    async def run(self):
        async with async_playwright() as p:
            print(f"[*] Starting WhatsApp RPA (Profile: {self.profile_name})")
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=self.profile_path,
                headless=False,
                args=[f"--profile-directory={self.profile_name}"]
            )
            page = await browser.new_page()
            await page.goto("https://web.whatsapp.com")

            print("[!] Waiting for WhatsApp Web to load...")
            try:
                await page.wait_for_selector("div[contenteditable='true'][data-tab='3']", timeout=60000)
                print("✅ WhatsApp Web Loaded.")
            except:
                print("❌ WhatsApp load timeout.")
                await browser.close()
                return

            while True:
                try:
                    chats = await page.query_selector_all("span[title^='+'], span[title^='0'], span[title^='1']")

                    for chat in chats:
                        title = await chat.get_attribute("title")
                        if title and re.search(r'\d', title):
                            print(f"[*] Analyzing numeric prospect: {title}")

                            await chat.click()
                            await asyncio.sleep(2)

                            bubbles = await page.query_selector_all(".message-in .copyable-text")
                            messages = [await b.inner_text() for b in bubbles[-10:]]

                            if messages:
                                analysis = await self.analyze_content(messages)
                                if analysis and analysis.get('nombre') and analysis['nombre'] != "UNKNOWN":
                                    print(f"✨ AI Discovered Name: {analysis['nombre']}")
                                    self.update_lead(title, analysis, "WhatsApp")
                                else:
                                    print("🤷 AI could not determine the name.")

                    await asyncio.sleep(10)
                except Exception as e:
                    print(f"Error in WhatsApp loop: {e}")
                    await asyncio.sleep(5)

if __name__ == "__main__":
    bot = WhatsAppBot()
    asyncio.run(bot.run())
