---
title: "Guide to Optimizing Photos for Websites"
description: "Learn the best techniques and tools for optimizing web images: modern formats, compression, responsive images, lazy loading, and CDN to boost speed and SEO."
pubDate: 2026-06-26
heroImage: "/assets/blog/covers/guide-to-optimizing-photos-for-websites.svg"
seoTitle: "Guide to Optimizing Photos for Websites | Formats, compression & SEO"
seoDescription: "Master web image optimization: WebP, AVIF, lossless compression, srcset, lazy loading and CDN. Improve your Core Web Vitals and SEO rankings."
permalink: "/blog/guia-optimizar-fotos-sitios-web"
altTexts: ["Web image format comparison chart", "Image compression tool interface", "Srcset code for responsive images", "CDN image delivery architecture"]
---
*   Images are the heaviest resource on most websites; proper optimization can reduce total page weight by up to 80%.
*   Modern formats WebP and AVIF offer far superior compression compared to JPEG and PNG at the same visual quality.
*   Combining modern formats, compression, `srcset`, lazy loading, and an image CDN is the ultimate strategy for maximizing speed and SEO.

## Why image optimization is critical

Images account for 50% to 80% of a web page's total weight. The average visitor consumes over 1 MB just from images when loading a page. Without optimization, the site becomes slow, user experience degrades, and SEO suffers directly in metrics like LCP (Largest Contentful Paint).

Google measures LCP as part of Core Web Vitals, and images are the #1 factor affecting it. A slow LCP (greater than 2.5 seconds) penalizes ranking. Optimizing images is not a luxury — it is a non-negotiable technical requirement.

## 1. Choose the right format

| Format | Compression | Transparency | Animation | Recommended Use |
|---|---|---|---|---|
| JPEG | Lossy | No | No | Photographs and complex scenes |
| PNG | Lossless | Yes | No | Graphics, logos, screenshots |
| WebP | Lossy and lossless | Yes | Yes | Modern replacement for JPEG and PNG |
| AVIF | Lossy and lossless | Yes | Yes | Maximum compression, newest format |
| SVG | Vector | Yes | Yes | Icons, logos, illustrations |

**Recommendation:** Use WebP as the primary format with fallback to JPEG/PNG based on compatibility. AVIF for browsers that support it (Chrome, Firefox, Edge).

## 2. Compress images without losing quality

### Recommended free tools

- **Squoosh** (squoosh.app) — Compress and convert to WebP/AVIF from the browser
- **TinyPNG / TinyJPG** — Smart compression with minimal loss
- **ImageOptim** (macOS) — Lossless compression without quality loss
- **sharp** (Node.js) — Programmatic library for automating compression in build pipelines

### Example with sharp (Node.js)

```js
import sharp from 'sharp';

await sharp('original-photo.jpg')
  .resize(1200)
  .webp({ quality: 80 })
  .toFile('optimized-photo.webp');
```

## 3. Use responsive images with srcset and sizes

The `srcset` attribute lets the browser choose the appropriate image size based on screen resolution. Never serve a 2000 px image to a mobile phone.

```html
<img
  src="photo-800.webp"
  srcset="
    photo-400.webp 400w,
    photo-800.webp 800w,
    photo-1200.webp 1200w
  "
  sizes="(max-width: 600px) 100vw, (max-width: 1024px) 50vw, 800px"
  alt="Photo description"
  loading="lazy"
  decoding="async"
/>
```

**Explanation:**
- `400w`, `800w`, `1200w` are the actual widths in pixels of each image
- `sizes` tells the browser how wide the image will be depending on the viewport
- The browser only downloads the most appropriate image

## 4. Lazy loading and modern attributes

Native lazy loading with `loading="lazy"` prevents off-screen images from downloading until the user scrolls near them.

```html
<img src="photo.webp" loading="lazy" decoding="async" alt="...">
```

- `loading="lazy"` — defer loading until the image is close to the viewport
- `decoding="async"` — decode the image asynchronously without blocking rendering
- `fetchpriority="high"` — prioritize loading for the LCP image (use only on the main image)

## 5. Serve images from a CDN

An image CDN (such as Cloudflare Images, Imgix, Cloudinary, or ImageKit) provides:

- **Reduced latency** — servers in multiple geographic locations
- **Real-time transformation** — resize and compress via URL parameters
- **Automatic format negotiation** — serve WebP or AVIF based on the visitor's browser
- **Persistent cache** — optimized images are stored at the edge

### Example with Cloudflare Images

```html
<img
  src="https://images.yourdomain.com/cdn-cgi/image/width=800,format=auto/photo.jpg"
  srcset="
    https://images.yourdomain.com/cdn-cgi/image/width=400,format=auto/photo.jpg 400w,
    https://images.yourdomain.com/cdn-cgi/image/width=800,format=auto/photo.jpg 800w,
    https://images.yourdomain.com/cdn-cgi/image/width=1200,format=auto/photo.jpg 1200w
  "
  sizes="(max-width: 600px) 100vw, 800px"
  alt="..."
  loading="lazy"
/>
```

The `format=auto` parameter makes Cloudflare automatically serve AVIF if the browser supports it, or WebP as a fallback.

## 6. Additional best practices

- **Explicit dimensions:** Always declare `width` and `height` in HTML to prevent Cumulative Layout Shift (CLS)
- **Preload the LCP image:** Use `<link rel="preload">` for the main hero image
- **SVG for icons:** SVGs are lightweight, scalable, and editable with CSS
- **Audit with Lighthouse:** Run the Chrome DevTools performance audit and review image optimization opportunities
- **Automate in the build:** Integrate sharp or a Vite/Webpack plugin so images are automatically compressed on deploy
