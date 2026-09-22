---
name: product-page-seo
description: Optimizes e-commerce product pages (Shopify, WooCommerce) for search engine visibility using a structured Perceive-Plan-Act-Evaluate cycle.
---

# Product Page SEO 🔎

Optimize e-commerce product pages for search engine visibility. This skill implements a comprehensive SEO framework covering on-page elements, structured data, and technical performance specifically tailored for Shopify and WooCommerce environments.

## Agentic Architecture: Perceive-Plan-Act-Evaluate

The AgentOrchestrator executes this skill through the following cognitive cycle:

1.  **Perceive**: Crawl the target URL, extract current metadata, analyze page speed (via Web-Perf), and identify existing schema markups.
2.  **Plan**: Map findings against SEO benchmarks and platform-specific constraints (e.g., Shopify liquid limitations or WooCommerce plugin conflicts).
3.  **Act**: Generate optimized copy, JSON-LD structured data, and technical implementation steps.
4.  **Evaluate**: Validate the proposed changes against SEO best practices and accessibility standards before final delivery.

## Implementation Phases

### Phase 1: Diagnosis (Perceive)
- **URL Analysis**: Extract Title tags, Meta descriptions, H1-H6 hierarchy, and URL slugs.
- **Technical Audit**: Analyze PageSpeed Insights (LCP, CLS, FID) and mobile responsiveness.
- **Schema Detection**: Identify existing Product, Review, and FAQ schema.
- **Content Gap Analysis**: Compare current product descriptions against top-ranking competitors for the target keywords.

### Phase 2: Strategy & Analysis (Plan)
- **Keyword Mapping**: Align product features with high-intent search queries.
- **Platform Optimization**: 
    - **Shopify**: Plan for SEO apps or theme-level liquid edits.
    - **WooCommerce**: Plan for Yoast/RankMath configurations or custom function hooks.
- **Prioritization**: Categorize fixes into "Critical" (Indexing/Errors), "High" (Conversion/CTR), and "Medium" (Enrichment).

### Phase 3: Programming & Execution (Act)
- **On-Page Optimization**:
    - Rewrite Title Tags and Meta Descriptions for maximum CTR.
    - Optimize H1s and image Alt text for accessibility and search.
- **Structured Data Generation**: Create valid JSON-LD for:
    - `Product` (Price, Availability, Brand)
    - `AggregateRating` & `Review`
    - `FAQPage` for product-specific questions.
- **Technical Recommendations**:
    - Image compression and WebP conversion strategies.
    - Minification of CSS/JS specific to the platform's asset pipeline.
- **Content Enrichment**: Draft FAQ sections, comparison tables, and internal linking anchors.

### Phase 4: Verification & Reporting (Evaluate)
- **Validation**: Run generated schema through the Rich Results Test.
- **Benchmark Comparison**: Estimated impact of changes on organic visibility.
- **Actionable Roadmap**: Provide a prioritized checklist for the user.

## Tech Stack Integration

- **Primary**: Leveraging **Cloudflare Pages/Functions** for edge-side SEO injections or redirects; **Tailwind CSS** for mobile-first UI optimization.
- **Secondary**: Integration with **GSC (Google Search Console)** and **GA4** for data-driven auditing; Python/Node.js scripts for bulk metadata analysis.

## Output Format

- **Executive Summary**: High-level SEO health score and primary bottlenecks.
- **Technical Audit Table**: Current vs. Proposed state for all on-page elements.
- **Code Blocks**: Ready-to-paste JSON-LD schema and HTML snippets.
- **Priority Matrix**:
    - 🔴 **Critical**: Fix immediately to avoid indexing issues.
    - 🟡 **High**: Significant impact on ranking/CTR.
    - 🔵 **Medium**: Long-term growth and conversion optimization.
- **Next Steps**: Concrete implementation guide for the specific platform (Shopify/WooCommerce).

⚠️ *Estimates are marked with this symbol when based on incomplete data or third-party API approximations.*