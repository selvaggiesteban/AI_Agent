---
name: Robots.txt Security Hardener
description: Optimizes and secures the robots.txt file to protect sensitive areas while ensuring optimal crawlability.
---

# Robots.txt Security Hardener

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- Analyze the current `robots.txt` for overly permissive or restrictive rules.
- Identify "Sensitive Paths" that should not be indexed (e.g., `/admin/`, `/config/`, `/api/private/`, `/staging/`).
- Check for "Crawl Waste": Areas being crawled that provide no SEO value (e.g., internal search result pages).
- Verify the `Sitemap` declaration is present and correct.

### 2. Analysis (Plan)
- Design a "Safe-List" and "Block-List" of directories.
- Determine the correct `User-agent` targets (e.g., `Googlebot`, `Bingbot`, and blocking aggressive scrapers).
- Plan the implementation of `Allow` rules for specific files within `Disallow` folders (e.g., CSS/JS for rendering).
- Evaluate the risk of "Hidden by Robots.txt" vs "Noindex" (Robots.txt prevents crawling, not necessarily indexing).

### 3. Programming (Act)
- Implement the hardened `robots.txt` in the Astro `public/` directory.
- Use Cloudflare Workers to serve a dynamic `robots.txt` based on the environment (Production vs Staging).
- Implement "Crawl-delay" for non-critical bots if server load is an issue.
- Add specific blocks for AI scrapers (e.g., `GPTBot`, `CCBot`) if content protection is required.

### 4. Verification (Evaluate)
- Test the `robots.txt` using the Google Search Console "Robots.txt Tester".
- Monitor GSC "Crawl Stats" to verify the reduction in "Crawl Waste".
- Verify that sensitive paths are no longer appearing in "Indexed" reports.
- Ensure that critical assets (JS/CSS) are still accessible to Googlebot for proper rendering.