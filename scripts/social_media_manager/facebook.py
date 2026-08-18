# Copyright (C) 2025 Esteban Selvaggi
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys
from pathlib import Path
import os
import asyncio
import random
import time
from datetime import datetime
from playwright.async_api import async_playwright

# Add root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

try:
    from core.rpa_bot import BaseBot
except ImportError:
    class BaseBot:
        def __init__(self, prompt): pass
        def update_lead(self, id, data, channel): print(f"Update: {id} {channel}")
from core.config import DB_PATH, LOG_CAMPAIGN_DIR, FACEBOOK_POST_MESSAGE, FACEBOOK_GROUPS

MESSAGE = FACEBOOK_POST_MESSAGE

class FacebookGroupBot(BaseBot):
    def __init__(self):
        super().__init__("")
        self.profile_path = os.path.join(os.environ['LOCALAPPDATA'], r'Google\Chrome\User Data')
        self.profile_name = "Default" # Match LinkedIn/Messenger
        self.groups = [g for g in FACEBOOK_GROUPS if g.strip()]
        self.log_file = LOG_CAMPAIGN_DIR / "facebook_posting_log.txt"

    def get_delays(self):
        cycle = list(range(1, 11)) + list(range(9, 1, -1))
        while True:
            for d in cycle:
                yield d

    async def post_to_group(self, page, group_url):
        print(f"[*] Navegando a: {group_url}")
        try:
            # Forzamos la URL para ir directamente a la zona de creación si es posible
            await page.goto(group_url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(random.uniform(6, 9))

            # 1. Identificar si es un grupo de Compra/Venta (Marketplace)
            # Los grupos de venta tienen botones como "¿Qué vendes?" o "Vender algo"
            sell_selectors = [
                'span:has-text("¿Qué vendes?")',
                'span:has-text("Vender algo")',
                'span:has-text("Vender")'
            ]
            
            is_sell_group = False
            for s in sell_selectors:
                if await page.query_selector(s):
                    is_sell_group = True
                    break

            # 2. Si es grupo de venta, preferimos ir a la pestaña "Conversación" para un post normal
            if is_sell_group:
                print("[*] Detectado grupo de venta, buscando pestaña Conversación...")
                conv_found = False
                tabs = await page.query_selector_all('a[role="tab"]')
                for tab in tabs:
                    text = await tab.inner_text()
                    if "Conversación" in text or "Discusión" in text:
                        await tab.click()
                        await asyncio.sleep(5)
                        conv_found = True
                        break
                if not conv_found:
                    # A veces no es un tab, sino un link
                    links = await page.query_selector_all('a')
                    for link in links:
                        text = await link.inner_text()
                        if "Conversación" in text or "Discusión" in text:
                            await link.click()
                            await asyncio.sleep(5)
                            break

            # 3. Buscar el botón de "Escribe algo..." pero filtrando para que sea el principal
            # Evitamos los que están dentro de comentarios buscando roles de botón fuera de listas de noticias
            main_post_selectors = [
                'div[role="button"]:has-text("Escribe algo...")',
                'div[role="button"]:has-text("Crear publicación pública...")',
                'div[aria-label*="Escribe algo"]',
                'div[role="button"]:has-text("¿Qué estás pensando?")'
            ]

            found = False
            for selector in main_post_selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        if await element.is_visible():
                            await element.click(force=True) # Usamos force para saltar overlays
                            found = True
                            break
                    if found: break
                except: continue

            if not found:
                print(f"[-] No se encontró área de post principal en {group_url}")
                return False

            print("[*] Botón de post clickeado, esperando modal...")
            await asyncio.sleep(5)
            
            # 4. Escribir el mensaje en el modal (Surgical Targeting)
            try:
                # Buscamos el modal que específicamente sea para crear publicaciones
                modal_selectors = [
                    'div[role="dialog"][aria-label="Crear publicación"]',
                    'div[role="dialog"][aria-label="Create post"]',
                    'div[role="dialog"]:has-text("Crear publicación")',
                    'div[role="dialog"]' # Fallback
                ]
                
                modal = None
                for ms in modal_selectors:
                    elements = await page.query_selector_all(ms)
                    for el in elements:
                        if await el.is_visible():
                            # Verificamos que contenga un textbox para estar seguros
                            if await el.query_selector('div[role="textbox"]'):
                                modal = el
                                print(f"[*] Modal correcto detectado: {ms}")
                                break
                    if modal: break

                if modal:
                    textbox = await modal.query_selector('div[role="textbox"]')
                    if textbox:
                        await textbox.click(force=True)
                        await asyncio.sleep(3)
                        # Limpiamos y escribimos
                        await textbox.fill(MESSAGE)
                        await asyncio.sleep(random.uniform(4, 6))
                        
                        # 5. Botón Publicar dentro del modal
                        post_btn_selectors = [
                            'div[aria-label="Publicar"][role="button"]',
                            'div[aria-label="Post"][role="button"]',
                            'div[role="button"]:has-text("Publicar")',
                            'div[role="button"]:has-text("Post")'
                        ]
                        
                        btn_found = False
                        for btn_selector in post_btn_selectors:
                            btn = await modal.query_selector(btn_selector)
                            if btn and await btn.is_visible():
                                # Verificamos que esté habilitado (FB a veces lo deshabilita mientras procesa)
                                await btn.click(force=True)
                                btn_found = True
                                break
                        
                        if btn_found:
                            print(f"[+] Publicando... esperando confirmación final")
                            # Esperar a que el modal desaparezca
                            try:
                                await asyncio.sleep(10)
                                print("[+] Publicación enviada.")
                                return True
                            except: return True
                    else:
                        print("[-] No se encontró textbox en el modal.")
                else:
                    print("[-] No se detectó el modal de publicación.")
            except Exception as e:
                print(f"[-] Error procesando modal: {e}")
            
            return False
        except Exception as e:
            print(f"[-] Error en {group_url}: {e}")
            return False

    async def run(self):
        if not self.groups:
            print("❌ No se encontraron grupos en el .env (FACEBOOK_GROUPS)")
            return

        # Check log for already processed groups TODAY
        processed_today = set()
        today_str = datetime.now().strftime("%Y-%m-%d")
        if self.log_file.exists():
            with open(self.log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if today_str in line and "EXITO" in line:
                        parts = line.split(" | ")
                        if len(parts) >= 3: processed_today.add(parts[2].strip())

        groups_to_process = [g for g in self.groups if g not in processed_today]
        if not groups_to_process:
            print("✅ Todo procesado por hoy.")
            return

        print(f"[*] Grupos pendientes: {len(groups_to_process)}")
        delay_gen = self.get_delays()

        async with async_playwright() as p:
            print(f"[*] Iniciando Chrome (Perfil: {self.profile_name})")
            browser = await p.chromium.launch_persistent_context(
                user_data_dir=self.profile_path,
                headless=False,
                args=[f"--profile-directory={self.profile_name}"]
            )
            
            page = browser.pages[0] if browser.pages else await browser.new_page()
            
            print("[*] Validando sesión en Facebook...")
            await page.goto("https://www.facebook.com/", wait_until="domcontentloaded")
            await asyncio.sleep(5)
            
            if "login" in page.url or await page.query_selector('input[name="email"]'):
                print("⚠️ No detecto sesión. Por favor logueate manualmente en la ventana abierta.")
                # Wait for user to login
                while "login" in page.url or await page.query_selector('input[name="email"]'):
                    await asyncio.sleep(5)
                print("✅ Sesión detectada.")

            for i, group in enumerate(groups_to_process):
                success = await self.post_to_group(page, group)
                
                with open(self.log_file, "a", encoding="utf-8") as f:
                    status = "EXITO" if success else "FALLO"
                    f.write(f"{datetime.now().isoformat()} | {status} | {group} | MSG: {MESSAGE[:30]}...\n")

                if i < len(groups_to_process) - 1:
                    delay = next(delay_gen)
                    print(f"[*] Espera de {delay} min...")
                    for _ in range(delay * 60): await asyncio.sleep(1)

            await browser.close()

if __name__ == "__main__":
    bot = FacebookGroupBot()
    asyncio.run(bot.run())
