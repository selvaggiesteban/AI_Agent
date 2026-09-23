---
name: Web Vitals Performance Tuner
description: Optimizes Core Web Vitals (LCP, FID, CLS) using advanced Astro, Tailwind, and Cloudflare techniques.
---

# Web Vitals Performance Tuner

This skill focuses on the technical optimization of a website to achieve perfect Core Web Vitals scores, directly impacting SEO and user experience.

## Workflow

### 1. Diagnosis (Perceive)
- Run PageSpeed Insights, Lighthouse, and Web Vitals extension to identify failing metrics.
- Analyze the "Waterfall" chart in Chrome DevTools to find render-blocking resources.
- Identify causes of Layout Shift (CLS) (e.g., images without dimensions, dynamic content injection).
- Measure Largest Contentful Paint (LCP) and find the critical path asset.

### 2. Analysis (Plan)
- **LCP Strategy**: Plan for critical CSS inlining, image priority (`fetchpriority="high"`), and CDN caching.
- **CLS Strategy**: Design placeholders/skeletons for dynamic content and enforce aspect ratios for images.
- **FID/INP Strategy**: Analyze the main thread; identify heavy JS bundles and plan for code-splitting or `client:idle` hydration.
- **Resource Audit**: Identify unused CSS/JS and plan for removal or deferred loading.

### 3. Programming (Act)
- **Image Optimization**: Implement Astro's `<Image />` component with correct `widths`, `formats` (AVIF/WebP), and `loading="lazy"`.
- **CSS Optimization**: Use Tailwind's JIT compiler and eliminate unused styles. Inline critical-path CSS for the fold.
- **JS Reduction**: Move non-essential logic to Web Workers or defer it using Astro's `client:only` or `client:visible`.
- **Font Tuning**: Implement `font-display: swap` and self-host fonts to reduce FOIT/FOUT.

### 4. Verification (Evaluate)
- Re-run Lighthouse and PageSpeed Insights to verify score improvements.
- Use Chrome DevTools "Performance" tab to ensure the main thread is clear of long tasks (>50ms).
- Verify that CLS is near zero across different devices and connection speeds.
- Monitor real-user metrics (RUM) if integrated via GA4 or Vercel Analytics.

## Tech Stack Alignment
- **Astro**: Optimized build output and partial hydration.
- **Tailwind CSS**: Lean CSS generation.
- **Cloudflare Pages**: Edge caching and asset delivery.
- **GA4**: Monitoring performance trends.
