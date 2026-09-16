# SEO Crawler Suite

Suite de herramientas Python para rastrear sitios web y generar reportes SEO completos.

## 📋 Herramientas Incluidas

### 1. WordPress SEO Crawler (`wordpress_seo_crawler.py`)
Rastreador de blogs WordPress para análisis SEO completo.

### 2. Site Mapper (`site_mapper.py`)
Mapea todas las páginas de un sitio web generando una lista completa de URLs.

### 3. SEO Verifier (`seo_verifier.py`)
Verifica 17+ requisitos SEO en cada página del sitio.

### 4. HTML Report Generator (`html_report_generator.py`)
Genera reportes HTML interactivos con resultados visuales.

## 🚀 Instalación

### 1. Requisitos previos
- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 💻 Uso Rápido

### Paso 1: Mapear el sitio
```bash
python site_mapper.py https://lanuscomputacion.com -o lanus_map.json
```

### Paso 2: Verificar SEO
```bash
python seo_verifier.py -f lanus_map.json -o lanus_seo.json
```

### Paso 3: Generar reporte HTML
```bash
python html_report_generator.py lanus_seo.json -o reportes/lanuscomputacion/
```

## 📊 Flujo de Trabajo Completo

```bash
# 1. Mapear los 3 sitios
python site_mapper.py https://lanuscomputacion.com -o data/lanus_map.json
python site_mapper.py https://selvaggiconsultores.com -o data/selvaggiconsultores_map.json
python site_mapper.py https://selvaggiesteban.dev -o data/selvaggiesteban_map.json

# 2. Verificar SEO en cada sitio
python seo_verifier.py -f data/lanus_map.json -o data/lanus_seo.json
python seo_verifier.py -f data/selvaggiconsultores_map.json -o data/selvaggiconsultores_seo.json
python seo_verifier.py -f data/selvaggiesteban_map.json -o data/selvaggiesteban_seo.json

# 3. Generar reportes HTML
python html_report_generator.py data/lanus_seo.json -o reportes/lanuscomputacion/
python html_report_generator.py data/selvaggiconsultores_seo.json -o reportes/selvaggiconsultores/
python html_report_generator.py data/selvaggiesteban_seo.json -o reportes/selvaggiesteban/

# 4. Generar reporte comparativo
python html_report_generator.py data/lanus_seo.json -o reportes/ --compare data/selvaggiconsultores_seo.json data/selvaggiesteban_seo.json
```

## 🔍 Verificaciones SEO

El script `seo_verifier.py` verifica los siguientes requisitos:

### SEO Técnico
- ✅ Meta título único por página
- ✅ Meta descripción única
- ✅ H1 único por página
- ✅ H1 diferente al meta-título
- ✅ Schema JSON-LD presente
- ✅ Open Graph image
- ✅ Favicon

### Diseño Responsive
- ✅ Viewport meta tag configurado
- ✅ Imágenes en formato WebP
- ✅ Alt text en todas las imágenes

### Legal y Contacto
- ✅ Aviso de Cookies
- ✅ Políticas de Privacidad
- ✅ Información de contacto real

### Analytics y Redes
- ✅ Google Analytics configurado
- ✅ Redes sociales en footer
- ✅ Portfolio en footer

### Contenido
- ✅ FAQ presente

## 📁 Estructura de Archivos

```
crawler/
├── wordpress_seo_crawler.py    # Crawler original WordPress
├── site_mapper.py              # Mapeador de sitios
├── seo_verifier.py             # Verificador SEO
├── html_report_generator.py    # Generador de reportes HTML
├── requirements.txt            # Dependencias
├── README.md                   # Esta documentación
├── data/                       # Datos generados (JSON, CSV)
│   ├── *_map.json              # Mapas de sitios
│   └── *_seo.json              # Resultados SEO
└── reportes/                   # Reportes HTML generados
    ├── lanuscomputacion/
    ├── selvaggiconsultores/
    └── selvaggiesteban/
```

## 📊 Formato de Salida

### JSON (para procesamiento programático)
```json
{
  "base_url": "https://lanuscomputacion.com",
  "total_pages": 50,
  "results": [
    {
      "url": "https://lanuscomputacion.com/servicios/seo",
      "score": 85.7,
      "passed": 15,
      "failed": 2,
      "checks": [...]
    }
  ]
}
```

### HTML (para visualización)
Reportes interactivos con:
- Resumen general con estadísticas
- Detalle por página con colores
- Filtros por verificación
- Diseño responsive

## ⚙️ Opciones de los Scripts

### site_mapper.py
```bash
python site_mapper.py <url> [-m MAX_PAGES] [-d DELAY] [-o OUTPUT]
```
- `url`: URL base del sitio
- `-m, --max-pages`: Máximo de páginas (default: 200)
- `-d, --delay`: Delay entre peticiones (default: 0.5s)
- `-o, --output`: Nombre base del archivo de salida

### seo_verifier.py
```bash
python seo_verifier.py [urls...] [-f FILE] [-d DELAY] [-o OUTPUT]
```
- `urls`: URLs a verificar
- `-f, --file`: Archivo JSON con URLs (generado por site_mapper.py)
- `-d, --delay`: Delay entre peticiones (default: 0.5s)
- `-o, --output`: Nombre base del archivo de salida

### html_report_generator.py
```bash
python html_report_generator.py <input> [-o OUTPUT_DIR] [-n NAME] [--compare FILES...]
```
- `input`: Archivo JSON con resultados
- `-o, --output-dir`: Directorio de salida (default: reportes)
- `-n, --name`: Nombre del archivo HTML (default: reporte_seo.html)
- `--compare`: Archivos JSON adicionales para comparar

## 🎯 Casos de Uso

### 1. Auditoría SEO completa
```bash
python site_mapper.py https://misitio.com -o data/map.json
python seo_verifier.py -f data/map.json -o data/seo.json
python html_report_generator.py data/seo.json -o reportes/misitio/
```

### 2. Comparar 2 sitios competidores
```bash
python html_report_generator.py data/mi_sitio.json -o reportes/ --compare data/competidor.json
```

### 3. Monitoreo periódico
```bash
# Ejecutar semanalmente y guardar con fecha
python seo_verifier.py -f data/map.json -o "data/seo_$(date +%Y%m%d).json"
```

## 🐛 Solución de Problemas

### Error de conexión
```bash
# Aumentar delay
python site_mapper.py https://ejemplo.com -d 2.0
```

### Timeout
```bash
# Reducir páginas máximas
python site_mapper.py https://ejemplo.com -m 50
```

### Memoria insuficiente
```bash
# Procesar por lotes
python site_mapper.py https://ejemplo.com -m 100 -o batch1.json
```

## 📚 Dependencias

- **requests**: Peticiones HTTP
- **beautifulsoup4**: Análisis HTML
- **lxml**: Parser rápido para BeautifulSoup

## 📄 Licencia

Script de uso libre para análisis SEO.
