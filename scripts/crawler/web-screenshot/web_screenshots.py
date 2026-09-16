from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'screenshot_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'),
        logging.StreamHandler()
    ]
)

# Función para tomar la captura de pantalla
def take_screenshot(url, viewport, file_name, timeout=30):
    driver = None
    try:
        # Configurar las opciones del navegador
        options = Options()
        options.headless = True  # Ejecutar sin abrir la ventana del navegador

        # Suprimir errores y advertencias de Chrome
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-logging')
        options.add_argument('--log-level=3')
        options.add_argument('--silent')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        # Iniciar el navegador
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.set_page_load_timeout(timeout)

        # Configurar las dimensiones para cada vista ANTES de cargar la página
        if viewport == 'desktop':
            driver.set_window_size(1920, 1080)
        elif viewport == 'tablet':
            driver.set_window_size(1024, 1366)
        elif viewport == 'mobile':
            driver.set_window_size(430, 932)

        # Cargar la URL
        logging.info(f"Accediendo a {url} [{viewport}]...")
        driver.get(url)

        # Esperar a que la página se cargue completamente
        time.sleep(5)

        # Tomar la captura de pantalla
        driver.save_screenshot(file_name)
        logging.info(f"✓ Captura guardada: {file_name}")

        return True

    except TimeoutException:
        logging.error(f"✗ Timeout al acceder a {url} [{viewport}] - La página tardó más de {timeout}s en cargar")
        return False

    except WebDriverException as e:
        error_msg = str(e)
        if "ERR_NAME_NOT_RESOLVED" in error_msg:
            logging.error(f"✗ DNS no resuelto para {url} [{viewport}] - Verifica que el dominio existe")
        elif "ERR_CONNECTION_REFUSED" in error_msg:
            logging.error(f"✗ Conexión rechazada para {url} [{viewport}] - El servidor no responde")
        elif "ERR_CONNECTION_TIMED_OUT" in error_msg:
            logging.error(f"✗ Timeout de conexión para {url} [{viewport}]")
        else:
            logging.error(f"✗ Error de WebDriver para {url} [{viewport}]: {error_msg[:200]}")
        return False

    except Exception as e:
        logging.error(f"✗ Error inesperado para {url} [{viewport}]: {str(e)[:200]}")
        return False

    finally:
        # Cerrar el navegador siempre
        if driver:
            try:
                driver.quit()
            except:
                pass

# Función principal para procesar múltiples sitios web
def process_websites(websites):
    # Crear carpeta para screenshots si no existe
    if not os.path.exists('screenshots'):
        os.makedirs('screenshots')

    # Estadísticas
    total_sites = len(websites)
    successful_sites = []
    failed_sites = []
    total_screenshots = 0
    failed_screenshots = 0

    logging.info(f"Iniciando procesamiento de {total_sites} sitios web...")
    logging.info("=" * 70)

    for idx, url in enumerate(websites, 1):
        try:
            # Extraer el nombre del sitio web (dominio)
            site_name = url.split("//")[-1].split("/")[0]

            logging.info(f"\n[{idx}/{total_sites}] Procesando: {site_name}")
            logging.info("-" * 70)

            # Contadores para este sitio
            site_success_count = 0
            viewports = ['desktop', 'tablet', 'mobile']

            # Tomar capturas en diferentes vistas
            for viewport in viewports:
                file_name = f'screenshots/{site_name}_{viewport}.png'
                success = take_screenshot(url, viewport, file_name)

                if success:
                    site_success_count += 1
                    total_screenshots += 1
                else:
                    failed_screenshots += 1

            # Registrar resultado del sitio
            if site_success_count == 3:
                successful_sites.append(site_name)
                logging.info(f"✓ Sitio completado: {site_name} ({site_success_count}/3 capturas)")
            elif site_success_count > 0:
                successful_sites.append(f"{site_name} (parcial: {site_success_count}/3)")
                logging.warning(f"⚠ Sitio parcialmente completado: {site_name} ({site_success_count}/3 capturas)")
            else:
                failed_sites.append(site_name)
                logging.error(f"✗ Sitio fallido: {site_name} (0/3 capturas)")

        except Exception as e:
            failed_sites.append(site_name if 'site_name' in locals() else url)
            logging.error(f"✗ Error crítico procesando {url}: {str(e)[:200]}")

    # Reporte final
    logging.info("\n" + "=" * 70)
    logging.info("REPORTE FINAL")
    logging.info("=" * 70)
    logging.info(f"Total de sitios procesados: {total_sites}")
    logging.info(f"Sitios exitosos: {len([s for s in successful_sites if 'parcial' not in s])}")
    logging.info(f"Sitios parciales: {len([s for s in successful_sites if 'parcial' in s])}")
    logging.info(f"Sitios fallidos: {len(failed_sites)}")
    logging.info(f"Screenshots totales: {total_screenshots}/{total_sites * 3}")
    logging.info(f"Screenshots fallidas: {failed_screenshots}")

    if failed_sites:
        logging.info("\nSitios con errores:")
        for site in failed_sites:
            logging.info(f"  - {site}")

    logging.info("=" * 70)

if __name__ == "__main__":
    # Lista de sitios web que deseas capturar
    websites = [
        "https://acuatika25.com.ar/",
        "https://aidbones.com/",
        "https://alquiriasolutions.com/",
        "https://amarantus.esloogan.online/",
        "https://aptofisico.com/",
        "https://asistencia365.com.ar/",
        "https://abogario.com.ar/", 
        "https://academiacopo.com/",
        "https://grupoalquilaga.com/",
        "https://bercatti.com/",
        "https://banplast.com.ar/",
        "https://behshadarjomandi.com/",
        "https://consulting-21.com/",
        "https://centraldeturbos.com/",
        "https://citipix.eu/",
        "https://cvela2017.com/",
        "https://cosechanatural.com.ar/",
        "https://ciclorural.com/",
        "https://dermaklinic.cl/",
        "https://depaoli.com.ar/",
        "https://diaadianet.com.ar/",
        "https://draandreamamani.com/",
        "https://decotay.com.ar/",
        "https://sosamirandaabogados.com.ar/",
        "https://todosalud.co",
        "https://ingenieriaproyectos.com.ar",
        "https://smartalk.cl/",
        "https://semikon.com.ar/",
        "https://semikongarden.com.ar/",
        "https://seararefrigeracion.com.ar/",
        "https://watervan.com.ar/",
        "https://muebles-cavah.com.ar/",
        "https://globaloltenia.es/",
        "https://reformaplus.com/",
        "https://ekilib.es/",
        "https://ecoalimentaria.es/",
        "https://8mejor.top/",
        "https://healthybodychamp.com/",
        "https://inksomniumtattoo.com/",
        "https://guiadepredadoresorellana.com/"
    ]
    
    # Procesar todos los sitios web
    process_websites(websites)
