---
name: Automatic Internal Linking Mapper
description: Analyzes site content to automatically suggest and implement strategic internal links to boost PageRank and UX.
---

# Automatic Internal Linking Mapper

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- Crawl the entire site to build a graph of all internal links.
- Identify "Orphan Pages" (pages with zero or very few incoming internal links).
- Identify "Power Pages" (pages with high external backlinks but low internal distribution).
- Extract keywords and entities from every page using NLP (Node.js/Python).

### 2. Analysis (Plan)
- Build a "Semantic Map" connecting pages based on keyword similarity.
- Define "Linking Rules":
    - Priority 1: Power Page -> Conversion Page.
    - Priority 2: High-Traffic Blog Post -> Related Product Page.
    - Priority 3: Content Hub -> Spoke Pages.
- Calculate the "Link Budget" per page to avoid over-optimization.

### 3. Programming (Act)
- Implement an automated internal linking utility in Astro:
  - Create a `link-map.json` containing keyword-to-URL mappings.
  - Develop a custom Markdown component or plugin that automatically wraps target keywords in internal links.
- Use TypeScript to ensure link integrity (verify URLs exist before linking).
- Apply "Descriptive Anchor Text" based on the semantic map.

### 4. Verification (Evaluate)
- Re-crawl the site to verify the removal of orphan pages.
- Monitor "Crawl Depth" in SEO audits (ensure critical pages are within 3 clicks of home).
- Track the redistribution of PageRank/Equity via GSC performance.
- Analyze "Bounce Rate" and "Pages per Session" in GA4 to verify UX improvement.