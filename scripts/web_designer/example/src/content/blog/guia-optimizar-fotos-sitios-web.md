---
title: "Guía para optimizar fotos en sitios web"
description: "Aprende las mejores técnicas y herramientas para optimizar imágenes web: formatos modernos, compresión, responsive images, lazy loading y CDN para mejorar velocidad y SEO."
pubDate: 2026-06-26
heroImage: "/assets/blog/covers/guia-optimizar-fotos-sitios-web.svg"
seoTitle: "Guía para optimizar fotos en sitios web | Formatos, compresión y SEO"
seoDescription: "Domina la optimización de imágenes web: WebP, AVIF, compresión sin pérdida, srcset, lazy loading y CDN. Mejora tu Core Web Vitals y posicionamiento SEO."
permalink: "/blog/guia-optimizar-fotos-sitios-web"
altTexts: ["Comparativa de formatos de imagen web", "Herramienta de compresión de imágenes", "Código srcset para responsive images", "Arquitectura CDN para imágenes"]
---
*   Las imágenes son el recurso más pesado en la mayoría de los sitios web; optimizarlas correctamente puede reducir el peso total de la página hasta un 80%.
*   Los formatos modernos WebP y AVIF ofrecen una compresión muy superior a JPEG y PNG con la misma calidad visual.
*   La combinación de formatos modernos, compresión, `srcset`, lazy loading y un CDN de imágenes es la estrategia definitiva para maximizar la velocidad y el SEO.

## Por qué es crítico optimizar las imágenes

Las imágenes representan entre el 50% y el 80% del peso total de una página web. Un visitante promedio consume más de 1 MB solo en imágenes al cargar una página. Si no están optimizadas, el sitio se vuelve lento, la experiencia de usuario se degrada y el SEO se resiente directamente en métricas como LCP (Largest Contentful Paint).

Google mide el LCP como parte de Core Web Vitals, y las imágenes son el factor #1 que lo afecta. Un LCP lento (mayor a 2.5 segundos) penaliza el ranking. Optimizar imágenes no es un lujo — es un requisito técnico innegociable.

## 1. Elegir el formato correcto

| Formato | Compresión | Transparencia | Animación | Uso recomendado |
|---|---|---|---|---|
| JPEG | Con pérdida (lossy) | No | No | Fotografías y escenas complejas |
| PNG | Sin pérdida (lossless) | Sí | No | Gráficos, logotipos, capturas de pantalla |
| WebP | Lossy y lossless | Sí | Sí | Reemplazo moderno de JPEG y PNG |
| AVIF | Lossy y lossless | Sí | Sí | Máxima compresión, formato más moderno |
| SVG | Vectorial | Sí | Sí | Iconos, logotipos, ilustraciones |

**Recomendación:** Usá WebP como formato principal con fallback a JPEG/PNG según compatibilidad. AVIF para navegadores que lo soporten (Chrome, Firefox, Edge).

## 2. Comprimir imágenes sin perder calidad

### Herramientas gratuitas recomendadas

- **Squoosh** (squoosh.app) — Comprime y convierte a WebP/AVIF desde el navegador
- **TinyPNG / TinyJPG** — Compresión inteligente con pérdida mínima
- **ImageOptim** (macOS) — Compresión lossless sin perder calidad
- **sharp** (Node.js) — Biblioteca programática para automatizar la compresión en pipelines de build

### Ejemplo con sharp (Node.js)

```js
import sharp from 'sharp';

await sharp('foto-original.jpg')
  .resize(1200)
  .webp({ quality: 80 })
  .toFile('foto-optimizada.webp');
```

## 3. Usar imágenes responsive con srcset y sizes

El atributo `srcset` permite al navegador elegir el tamaño de imagen adecuado según la resolución de la pantalla. Nunca sirvas una imagen de 2000 px a un teléfono móvil.

```html
<img
  src="foto-800.webp"
  srcset="
    foto-400.webp 400w,
    foto-800.webp 800w,
    foto-1200.webp 1200w
  "
  sizes="(max-width: 600px) 100vw, (max-width: 1024px) 50vw, 800px"
  alt="Descripción de la foto"
  loading="lazy"
  decoding="async"
/>
```

**Explicación:**
- `400w`, `800w`, `1200w` son los anchos reales en píxeles de cada imagen
- `sizes` le dice al navegador qué ancho ocupará la imagen según el viewport
- El navegador descarga solo la imagen más apropiada

## 4. Lazy loading y atributos modernos

El lazy loading nativo con `loading="lazy"` evita que las imágenes fuera de la pantalla se descarguen hasta que el usuario se desplace hacia ellas.

```html
<img src="foto.webp" loading="lazy" decoding="async" alt="...">
```

- `loading="lazy"` — diferir la carga hasta que la imagen esté cerca del viewport
- `decoding="async"` — decodificar la imagen de forma asíncrona sin bloquear el renderizado
- `fetchpriority="high"` — priorizar la carga de la imagen LCP (usar solo en la imagen principal)

## 5. Servir imágenes desde un CDN

Un CDN de imágenes (como Cloudflare Images, Imgix, Cloudinary o ImageKit) ofrece:

- **Reducción de latencia** — servidores en múltiples ubicaciones geográficas
- **Transformación en tiempo real** — redimensionar y comprimir según parámetros en la URL
- **Formato automático** — servir WebP o AVIF según el navegador del visitante
- **Caché persistente** — las imágenes optimizadas se almacenan en edge

### Ejemplo con Cloudflare Images

```html
<img
  src="https://imagenes.tudominio.com/cdn-cgi/image/width=800,format=auto/foto.jpg"
  srcset="
    https://imagenes.tudominio.com/cdn-cgi/image/width=400,format=auto/foto.jpg 400w,
    https://imagenes.tudominio.com/cdn-cgi/image/width=800,format=auto/foto.jpg 800w,
    https://imagenes.tudominio.com/cdn-cgi/image/width=1200,format=auto/foto.jpg 1200w
  "
  sizes="(max-width: 600px) 100vw, 800px"
  alt="..."
  loading="lazy"
/>
```

El parámetro `format=auto` hace que Cloudflare sirva automáticamente AVIF si el navegador lo soporta, o WebP como fallback.

## 6. Buenas prácticas adicionales

- **Dimensiones explícitas:** Siempre declará `width` y `height` en el HTML para evitar Cumulative Layout Shift (CLS)
- **Precargá la imagen LCP:** Usá `<link rel="preload">` para la imagen principal del hero
- **SVG para iconos:** Los SVG son livianos, escalables y editables con CSS
- **Auditá con Lighthouse:** Pasá la auditoría de rendimiento de Chrome DevTools y revisá las oportunidades de optimización de imágenes
- **Automatizá en el build:** Integrá sharp o un plugin de Vite/Webpack para que las imágenes se compriman automáticamente al hacer deploy
