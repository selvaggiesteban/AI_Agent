---
name: Canonical Tag Auditor
description: Ensures correct canonicalization across the site to prevent duplicate content issues and consolidate link equity.
---

# Canonical Tag Auditor

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- Crawl the site to extract all `<link rel="canonical">` tags.
- Identify "Canonical Mismatches": Page A points to Page B, but Page B points to Page C.
- Locate "Self-Referencing" canonicals on pages that should be redirects.
- Identify "Missing" canonicals on pages with multiple URL parameters (UTM, pagination, filters).

### 2. Analysis (Plan)
- Define the "Canonical Truth" for every URL pattern:
    - Product variations -> Main Product Page.
    - Paginated lists -> Page 1 (or self-referencing for indexability).
    - HTTP/HTTPS and www/non-www -> Single unified version.
- Map duplicate content clusters and decide which URL should be the "Master".
- Evaluate the impact of "Canonical vs 301" for specific use cases.

### 3. Programming (Act)
- Implement dynamic canonical logic in Astro:
  ```astro
  ---
  const { canonicalURL } = Astro.props;
  const currentURL = Astro.url.href;
  const finalCanonical = canonicalURL || currentURL;
  ---
  <link rel="canonical" href={finalCanonical} />
  ```
- Fix "Canonical Loops" by updating the source logic in the CMS or Astro config.
- Set up Cloudflare Page Rules to enforce the primary domain/protocol (preventing duplicates).
- Ensure sitemap.xml only contains the canonical versions of URLs.

### 4. Verification (Evaluate)
- Re-crawl the site to ensure 100% canonical consistency.
- Use GSC "URL Inspection" to verify "User-declared canonical" matches "Google-selected canonical".
- Monitor GSC "Indexing" report for a decrease in "Duplicate, Google chose different canonical than user".
- Track the consolidation of link equity via increased rankings for Master URLs.