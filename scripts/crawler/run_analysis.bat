@echo off
echo ========================================
echo Analisis SEO Completo - 3 Sitios
echo ========================================
echo.

echo [1/6] Mapeando lanuscomputacion.com...
python scripts/crawler/site_mapper.py https://lanuscomputacion.com -m 50 -o scripts/crawler/data/lanus_map.json
echo.

echo [2/6] Mapeando selvaggiconsultores.com...
python scripts/crawler/site_mapper.py https://selvaggiconsultores.com -m 50 -o scripts/crawler/data/selvaggiconsultores_map.json
echo.

echo [3/6] Mapeando selvaggiesteban.dev...
python scripts/crawler/site_mapper.py https://selvaggiesteban.dev -m 50 -o scripts/crawler/data/selvaggiesteban_map.json
echo.

echo [4/6] Verificando SEO en lanuscomputacion.com...
python scripts/crawler/seo_verifier.py -f scripts/crawler/data/lanus_map.json -o scripts/crawler/data/lanus_seo.json
echo.

echo [5/6] Verificando SEO en selvaggiconsultores.com...
python scripts/crawler/seo_verifier.py -f scripts/crawler/data/selvaggiconsultores_map.json -o scripts/crawler/data/selvaggiconsultores_seo.json
echo.

echo [6/6] Verificando SEO en selvaggiesteban.dev...
python scripts/crawler/seo_verifier.py -f scripts/crawler/data/selvaggiesteban_map.json -o scripts/crawler/data/selvaggiesteban_seo.json
echo.

echo ========================================
echo Generando reportes HTML...
echo ========================================
echo.

New-Item -ItemType Directory -Path "scripts/crawler/reportes/lanuscomputacion" -Force
New-Item -ItemType Directory -Path "scripts/crawler/reportes/selvaggiconsultores" -Force
New-Item -ItemType Directory -Path "scripts/crawler/reportes/selvaggiesteban" -Force

python scripts/crawler/html_report_generator.py scripts/crawler/data/lanus_seo.json -o scripts/crawler/reportes/lanuscomputacion/ -n reporte_seo.html
python scripts/crawler/html_report_generator.py scripts/crawler/data/selvaggiconsultores_seo.json -o scripts/crawler/reportes/selvaggiconsultores/ -n reporte_seo.html
python scripts/crawler/html_report_generator.py scripts/crawler/data/selvaggiesteban_seo.json -o scripts/crawler/reportes/selvaggiesteban/ -n reporte_seo.html

echo.
echo ========================================
echo Generando reporte comparativo...
echo ========================================
echo.

python scripts/crawler/html_report_generator.py scripts/crawler/data/lanus_seo.json -o scripts/crawler/reportes/ --compare scripts/crawler/data/selvaggiconsultores_seo.json scripts/crawler/data/selvaggiesteban_seo.json

echo.
echo ========================================
echo Analisis completado!
echo ========================================
echo.
echo Reportes generados en:
echo   - scripts/crawler/reportes/lanuscomputacion/reporte_seo.html
echo   - scripts/crawler/reportes/selvaggiconsultores/reporte_seo.html
echo   - scripts/crawler/reportes/selvaggiesteban/reporte_seo.html
echo   - scripts/crawler/reportes/comparativo.html
echo.
pause
