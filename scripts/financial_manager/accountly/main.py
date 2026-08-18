import os
import sys

# Agregar path local para imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src import extractors, processors, generator

# Configuración de rutas (Ajustar a tus carpetas reales)
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # contabilidad_dashboard
ROOT_DIR = os.path.dirname(BASE_DIR) # contabilidad

DIRS = {
    'arca': os.path.join(ROOT_DIR, "facturas emitidas de ARCA", "Punto de venta 00004"),
    'santander': os.path.join(ROOT_DIR, "resúmenes de cuenta Banco Santander Argentina"),
    'mercadopago': os.path.join(ROOT_DIR, "resúmenes de cuenta Mercado Pago"),
    'credicoop': os.path.join(ROOT_DIR, "resúmenes de cuenta Banco Credicoop")
}

TEMPLATE_PATH = os.path.join(BASE_DIR, 'templates', 'index.html')
OUTPUT_PATH = os.path.join(BASE_DIR, 'index.html')

def main():
    print("Iniciando generación del Dashboard Contable...")
    
    # 1. Extracción
    print("--- Fase 1: Extracción de Datos ---")
    arca_data = extractors.process_arca_files(DIRS['arca'])
    
    # Bancos (Se pueden agregar más extractores aquí)
    santander_data = extractors.process_santander(DIRS['santander'])
    mp_data = extractors.process_mercadopago(DIRS['mercadopago'])
    credicoop_data = extractors.process_credicoop(DIRS['credicoop'])
    
    # Western Union
    wu_file = os.path.join(ROOT_DIR, "resúmen de recibos Western Union.pdf")
    wu_data = extractors.process_western_union(wu_file)
    
    all_bank_data = santander_data + mp_data + credicoop_data
    
    print(f"Registros extraídos: ARCA={len(arca_data)}, Bancos={len(all_bank_data)}, WU={len(wu_data)}")
    
    # DEBUG: Verificar montos
    if arca_data:
        print(f"Muestra ARCA: {arca_data[0]}")
    if all_bank_data:
        print(f"Muestra Banco: {all_bank_data[0]}")
    if wu_data:
        print(f"Muestra WU: {wu_data[0]}")

    # 2. Procesamiento
    print("--- Fase 2: Procesamiento y Unificación ---")
    processed_data = processors.aggregate_data(arca_data, all_bank_data, wu_data)
    
    # 3. Generación
    print("--- Fase 3: Generación de Reporte HTML ---")
    generator.generate_html_report(processed_data, TEMPLATE_PATH, OUTPUT_PATH)
    
    print("\n¡Proceso completado!")
    print(f"Abre el siguiente archivo en tu navegador: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
