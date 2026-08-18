# WordPress SEO Crawler

Script Python para rastrear blogs de WordPress y extraer información SEO completa para análisis de clusters y optimización.

## 📋 Características

El script extrae los siguientes datos de cada página:

- **URL**: Dirección completa de la página
- **Keyword (Cluster)**: Palabra clave principal extraída del slug de la URL
- **H1**: Encabezado principal de la página
- **CTA URL**: URL del Call-to-Action
- **CTA Anchor Text**: Texto del enlace del CTA
- **Schema**: Tipos de Schema Markup implementados
- **Meta Description**: Descripción meta de la página
- **SEO Title**: Título SEO (tag `<title>`)
- **Alt Texts**: Textos alternativos de todas las imágenes
- **Robots Tag**: Directivas para robots de búsqueda
- **Author**: Autor del contenido
- **Publisher**: Editor del contenido
- **Lang**: Idioma de la página
- **Headers (quantity)**: Cantidad total de encabezados (H1-H6)
- **Images without ALT**: Número de imágenes sin atributo ALT
- **Images without TITLE**: Número de imágenes sin atributo TITLE

## 🚀 Instalación

### 1. Requisitos previos
- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

O instalar manualmente:

```bash
pip install requests beautifulsoup4 lxml
```

## 💻 Uso

### Uso básico

```bash
python wordpress_seo_crawler.py https://ejemplo.com
```

### Opciones avanzadas

```bash
# Limitar a 50 páginas
python wordpress_seo_crawler.py https://ejemplo.com -m 50

# Aumentar el delay entre peticiones a 2 segundos
python wordpress_seo_crawler.py https://ejemplo.com -d 2.0

# Especificar nombre del archivo de salida
python wordpress_seo_crawler.py https://ejemplo.com -o mi_analisis.csv

# Combinar opciones
python wordpress_seo_crawler.py https://ejemplo.com -m 200 -d 1.5 -o analisis_seo.csv
```

### Parámetros disponibles

- `url` (requerido): URL del sitio WordPress a rastrear
- `-m, --max-pages`: Número máximo de páginas a rastrear (default: 100)
- `-d, --delay`: Delay entre peticiones en segundos (default: 1.0)
- `-o, --output`: Nombre del archivo CSV de salida (default: wordpress_seo_analysis.csv)

### Ver ayuda

```bash
python wordpress_seo_crawler.py --help
```

## 📊 Formato de salida

El script genera un archivo CSV con todas las métricas SEO. Ejemplo:

| URL | Keyword (Cluster) | H1 | CTA URL | Schema | Meta Description | ... |
|-----|-------------------|----|---------| -------|------------------|-----|
| https://ejemplo.com/post-1 | Post 1 | Título del Post | /contact | Article | Descripción... | ... |

## 🎯 Casos de uso

### 1. Análisis de cluster de contenido
Identifica automáticamente palabras clave principales de cada artículo basándose en la URL.

### 2. Auditoría SEO
Detecta páginas sin:
- Meta descriptions
- H1 tags
- Alt texts en imágenes
- Schema markup

### 3. Análisis de CTAs
Revisa la presencia y consistencia de llamadas a la acción en todo el sitio.

### 4. Optimización de imágenes
Identifica imágenes sin atributos ALT o TITLE para mejorar accesibilidad y SEO.

## ⚙️ Funcionamiento interno

1. **Rastreo**: Comienza desde la URL base y sigue enlaces internos
2. **Extracción**: Para cada página, extrae todos los elementos SEO
3. **Filtrado**: Solo rastrea URLs del mismo dominio
4. **Exportación**: Guarda todos los datos en formato CSV

## 🔒 Buenas prácticas

- **Respeta los robots.txt**: El script no verifica robots.txt, asegúrate de tener permiso para rastrear
- **Usa delays apropiados**: El default es 1 segundo, aumenta si el servidor es lento
- **Limita el alcance**: Para sitios grandes, usa `-m` para limitar páginas
- **Horarios de bajo tráfico**: Ejecuta durante horarios de poco tráfico

## 🐛 Solución de problemas

### Error de conexión
```bash
# Aumenta el delay entre peticiones
python wordpress_seo_crawler.py https://ejemplo.com -d 2.0
```

### Timeout
```bash
# El script tiene un timeout de 10 segundos por página
# Si falla, verifica tu conexión o el estado del sitio
```

### Memoria insuficiente para sitios grandes
```bash
# Reduce el número máximo de páginas
python wordpress_seo_crawler.py https://ejemplo.com -m 50
```

## 📝 Ejemplos de análisis

### Ejemplo 1: Auditoría rápida (20 páginas)
```bash
python wordpress_seo_crawler.py https://miblog.com -m 20 -o auditoria_rapida.csv
```

### Ejemplo 2: Análisis completo con delay conservador
```bash
python wordpress_seo_crawler.py https://miblog.com -m 500 -d 2.0 -o analisis_completo.csv
```

### Ejemplo 3: Test de un subdirectorio específico
```bash
python wordpress_seo_crawler.py https://miblog.com/categoria/ -m 30 -o categoria_analisis.csv
```

## 📚 Dependencias

- **requests**: Realiza peticiones HTTP
- **beautifulsoup4**: Analiza HTML
- **lxml**: Parser rápido para BeautifulSoup

## 🤝 Contribuciones

El script es extensible. Puedes agregar nuevos extractores de datos modificando el método `extract_page_data()`.

## ⚠️ Limitaciones

- Solo rastrea el mismo dominio (no sigue enlaces externos)
- No ejecuta JavaScript (sitios SPA pueden no funcionar completamente)
- No procesa contenido detrás de login
- El análisis de CTA busca patrones comunes, puede no detectar todos los CTAs personalizados

## 📄 Licencia

Script de uso libre para análisis SEO.
