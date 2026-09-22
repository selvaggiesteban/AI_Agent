---
name: Astro SEO Optimizer
description: Audits and improves the SEO setup of Astro sites, focusing on technical foundation, structured data, and Cloudflare Pages integration.
---

# Astro SEO Optimizer

This skill audits and optimizes the SEO performance of Astro sites. It follows the agentic Perceive-Plan-Act-Evaluate cycle to ensure technical SEO excellence, leveraging `@jdevalk/astro-seo-graph` as the opinionated foundation.

## Agentic Workflow

### Phase 1: Diagnosis (Perceive)
**Goal:** Understand the current state of the project and identify SEO gaps.

1. **Environment Scan:** 
   - Confirm the project is an Astro site.
   - Detect the hosting environment (target: Cloudflare Pages).
   - Check for the presence of `@jdevalk/astro-seo-graph`.
2. **Technical Audit:** Score the site across nine critical categories:
   - Technical Foundation (HTML tags, robots.txt)
   - Structured Data (JSON-LD, Schema.org)
   - Content (Header hierarchy, meta tags)
   - Site Structure (Internal linking, URL patterns)
   - Performance (Core Web Vitals, Astro build optimization)
   - Sitemaps & Indexing (sitemap.xml, indexing directives)
   - Agent Discovery (AI-friendly metadata)
   - Redirects (Cloudflare Functions/Pages redirect rules)
   - Analytics (GA4, GSC integration)

### Phase 2: Analysis (Plan)
**Goal:** Create a prioritized roadmap for improvements.

1. **Gap Analysis:** Compare audit results against the [Astro SEO Definitive Guide](https://joost.blog/astro-seo-complete-guide/).
2. **Implementation Strategy:**
   - If `@jdevalk/astro-seo-graph` is missing, prioritize its installation.
   - Map missing SEO elements to specific "Code Recipes" (referencing `AGENTS.md`).
   - Identify necessary Cloudflare Pages/Functions configurations for redirects or headers.
3. **Constraint Check:** Ensure proposed changes align with the tech stack (TypeScript, Tailwind CSS).

### Phase 3: Programming (Act)
**Goal:** Execute the plan by generating and modifying code.

1. **Foundation Setup:** Install and configure `@jdevalk/astro-seo-graph`.
2. **Component Implementation:** 
   - Generate/modify Astro components to include dynamic meta tags and structured data.
   - Apply Tailwind CSS optimizations for performance-centric SEO.
3. **Infrastructure Configuration:**
   - Configure `_redirects` or `_headers` for Cloudflare Pages.
   - Set up sitemap generation and robots.txt.
4. **Metadata Refinement:** 
   - Invoke `metadata-check` on all generated strings (titles, descriptions, FAQ answers, frontmatter excerpts).

### Phase 4: Verification (Evaluate)
**Goal:** Validate that changes are correct and effective.

1. **Build Validation:** Run the Astro build process to ensure no regressions.
2. **Schema Validation:** Verify JSON-LD outputs against official validators.
3. **Infrastructure Check:** Confirm Cloudflare Turnstile or Resend integrations (if present) do not interfere with crawler access.
4. **User Hand-off:** Provide a checklist of non-file tasks:
   - Google Search Console (GSC) verification.
   - Bing Webmaster Tools setup.
   - IndexNow key verification.

## Tech Stack Alignment
- **Primary:** Astro, Tailwind CSS, Cloudflare Pages/Functions.
- **Secondary:** TypeScript, Node.js.
- **Tools:** `@jdevalk/astro-seo-graph`, GA4, GSC.