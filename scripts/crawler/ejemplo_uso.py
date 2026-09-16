#!/usr/bin/env python3
"""
Ejemplo de uso del WordPress SEO Crawler
Este script muestra cómo usar el crawler programáticamente
"""

from wordpress_seo_crawler import WordPressSEOCrawler

# Ejemplo 1: Uso básico
print("=" * 60)
print("EJEMPLO 1: Uso básico")
print("=" * 60)

crawler1 = WordPressSEOCrawler(
    base_url='https://ejemplo.com',
    max_pages=10,
    delay=1.0
)

# Nota: Descomenta las siguientes líneas para ejecutar
# crawler1.crawl()
# crawler1.save_to_csv('ejemplo_basico.csv')


# Ejemplo 2: Análisis más profundo con delay mayor
print("\n" + "=" * 60)
print("EJEMPLO 2: Análisis profundo")
print("=" * 60)

crawler2 = WordPressSEOCrawler(
    base_url='https://miblog.com',
    max_pages=50,
    delay=2.0
)

# Nota: Descomenta las siguientes líneas para ejecutar
# crawler2.crawl()
# crawler2.save_to_csv('analisis_profundo.csv')


# Ejemplo 3: Analizar resultados después del rastreo
print("\n" + "=" * 60)
print("EJEMPLO 3: Análisis de resultados")
print("=" * 60)

crawler3 = WordPressSEOCrawler(
    base_url='https://otroblog.com',
    max_pages=20,
    delay=1.5
)

# Nota: Descomenta las siguientes líneas para ejecutar
# crawler3.crawl()

# Analizar resultados
# print(f"\nTotal de páginas rastreadas: {len(crawler3.results)}")

# Páginas sin H1
# sin_h1 = [r for r in crawler3.results if r['H1'] == 'No H1']
# print(f"Páginas sin H1: {len(sin_h1)}")

# Páginas sin meta description
# sin_meta = [r for r in crawler3.results if r['Meta Description'] == 'No Meta Description']
# print(f"Páginas sin Meta Description: {len(sin_meta)}")

# Páginas sin Schema
# sin_schema = [r for r in crawler3.results if r['Schema'] == 'No Schema']
# print(f"Páginas sin Schema: {len(sin_schema)}")

# Total de imágenes sin ALT
# total_imgs_sin_alt = sum(r['Images without ALT'] for r in crawler3.results)
# print(f"Total de imágenes sin ALT: {total_imgs_sin_alt}")

# crawler3.save_to_csv('analisis_con_estadisticas.csv')


print("\n" + "=" * 60)
print("INSTRUCCIONES")
print("=" * 60)
print("""
Para usar estos ejemplos:

1. Edita las URLs en los ejemplos arriba
2. Descomenta las líneas que quieras ejecutar
3. Ejecuta: python ejemplo_uso.py

O usa directamente desde la línea de comandos:
python wordpress_seo_crawler.py https://tu-blog.com -m 50 -o resultado.csv
""")
