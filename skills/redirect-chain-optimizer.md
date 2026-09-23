---
name: Redirect Chain Optimizer
description: Detects and eliminates redirect chains and loops to improve crawl efficiency and page load speed.
---

# Redirect Chain Optimizer

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- Crawl the site using an SEO spider (Screaming Frog or custom Node.js crawler) to find redirect paths.
- Identify "Redirect Chains" (A -> B -> C) and "Redirect Loops" (A -> B -> A).
- Locate "Broken Redirects" (A -> B where B is 404).
- Analyze the impact on "Time to First Byte" (TTFB) caused by multiple hops.

### 2. Analysis (Plan)
- Map every chain to its final destination (A -> Final Destination).
- Prioritize critical paths (Home, Top Landing Pages, Checkout).
- Determine the most efficient redirect type: `301 Moved Permanently` for SEO equity.
- Identify redundant redirects caused by protocol (HTTP -> HTTPS) or trailing slash mismatches.

### 3. Programming (Act)
- Implement "Direct Redirects" via Cloudflare Bulk Redirects or `_redirects` file in Cloudflare Pages:
  - Replace `A -> B -> C` with `A -> C` and `B -> C`.
- Use TypeScript/Node.js to automate the discovery and mapping of redirects from a CSV.
- Configure Cloudflare Page Rules to handle global patterns (e.g., removing `/blog/old-category/` in one rule).
- Ensure all internal links are updated to point directly to the final destination.

### 4. Verification (Evaluate)
- Re-crawl the site to verify that all redirects are now single-hop.
- Use `curl -I` to verify the response headers for target URLs.
- Monitor TTFB improvements in PageSpeed Insights.
- Check GSC for "Crawl stats" improvements and reduced "Redirect errors".