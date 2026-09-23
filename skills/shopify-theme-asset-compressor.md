---
name: Shopify Theme Asset Compressor
description: Optimizes and compresses all theme assets (images, CSS, JS) to achieve maximum PageSpeed scores.
---

# Shopify Theme Asset Compressor

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **Asset Audit**: Identify large images, unminified CSS, and bloated JS files using Chrome DevTools and PageSpeed Insights.
- **Format Analysis**: Check for outdated image formats (e.g., JPG/PNG) that could be replaced with WebP or AVIF.
- **Render-Blocking Check**: Identify CSS and JS files that are blocking the initial page render.

### 2. Analysis (Plan)
- **Compression Strategy**: Plan the conversion of all static assets to modern formats (WebP for images, minified Gzip/Brotli for text).
- **Loading Strategy**: Design a "Critical CSS" implementation to load essential styles first and defer the rest.
- **Asset Pipeline**: Plan a process for automatically optimizing images upon upload to Shopify.

### 3. Programming (Act)
- **Image Optimization**: Use Shopify's image filters (e.g., `image_url: width: ...`) to serve responsive images in WebP format.
- **CSS Refactoring**: Convert bloated CSS to Tailwind CSS utility classes to drastically reduce the final CSS bundle size.
- **JS Minification**: Minify and bundle custom JS scripts, removing unused libraries and redundant polyfills.
- **Lazy Loading**: Implement native `loading="lazy"` and `decoding="async"` for all non-critical images.

### 4. Verification (Evaluate)
- **Core Web Vitals Audit**: Measure the improvement in LCP (Largest Contentful Paint) and CLS (Cumulative Layout Shift).
- **Payload Comparison**: Compare the total page weight (in MB) before and after asset compression.
- **Visual Integrity Check**: Ensure that compressed images and minified CSS do not cause visual degradation on any device.
