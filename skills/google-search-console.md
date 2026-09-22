---
name: analytics-gsc
description: Guides the analysis of Google Search Console (GSC) data to extract actionable SEO insights, monitor indexing health, and optimize performance metrics.
---

# Skill: Analytics: Google Search Console

This skill implements a structured approach to Google Search Console (GSC) analysis, integrating the AI_Agent's **Perceive-Plan-Act-Evaluate** architecture to transform raw search data into strategic SEO improvements.

## Agentic Workflow

The AgentOrchestrator shall execute this skill using the following phased approach:

### Phase 1: Diagnosis (Perceive)
**Goal**: Establish the current state of visibility and identify immediate anomalies.
- **Perceive**: Collect raw data from GSC (via API `searchanalytics.query` or UI export).
- **Focus Areas**:
    - **Performance**: Clicks, impressions, CTR, and average position.
    - **Indexing**: Compare "Indexed" vs "Not Indexed" counts; identify top "Reasons" for non-indexing.
    - **Technical**: Review Sitemap status and Core Web Vitals (CWV) reports.
- **Output**: A "Current State" snapshot identifying the most critical regressions or opportunities.

### Phase 2: Analysis (Plan)
**Goal**: Correlate data to find the "Why" behind the "What".
- **Plan**: Develop a hypothesis for performance shifts.
- **Analysis Patterns**:
    - **Query-Page Correlation**: Identify "Striking Distance" keywords (Position 4-10) with high impressions but low CTR.
    - **Indexing Gaps**: Analyze the "Coverage" report to distinguish between intentional exclusions (noindex) and technical errors (404, server errors).
    - **Trend Analysis**: Correlate GSC dips/spikes with site releases, content updates, or algorithm volatility.
    - **Rich Results**: Evaluate the performance of Enhancements (Schema.org) against standard results.
- **Output**: A prioritized list of SEO hypotheses and an action plan.

### Phase 3: Programming & Implementation (Act)
**Goal**: Execute technical and content optimizations based on the analysis.
- **Act**: Implement changes across the tech stack.
- **Tech Stack Integration**:
    - **Astro/Tailwind**: Optimize Page Speed and CWV (LCP, CLS) by refining component architecture and CSS.
    - **Cloudflare Pages/Functions**: Implement edge caching or redirects via Cloudflare to resolve indexing errors.
    - **CMS (WordPress/Shopify/WooCommerce)**: Update metadata, fix broken internal links, or optimize content structures.
    - **Technical SEO**: Submit updated sitemaps or request re-indexing for critical fixed pages.
- **Output**: Log of implemented changes.

### Phase 4: Verification & Reporting (Evaluate)
**Goal**: Measure the impact of actions and refine the strategy.
- **Evaluate**: Monitor GSC for 14-30 days post-implementation.
- **Metrics for Success**:
    - Increase in CTR for targeted "Striking Distance" queries.
    - Reduction in "Not Indexed" pages due to technical errors.
    - Improvement in Core Web Vitals "Good" URL percentage.
- **Output**: Final Performance Report comparing "Before" vs "After" metrics.

## Analysis Best Practices

### Chart Reading & Data Interpretation
- **Avoid the "Average" Trap**: Look at the distribution. A high average position can be skewed by a few very high-ranking low-volume pages.
- **CTR vs. Position**: Always analyze CTR relative to position. A drop in CTR without a drop in position often indicates a need for better Meta Titles/Descriptions.
- **Indexing Latency**: Account for GSC's data lag (typically 2-3 days) when correlating with real-time deployments.

## Invocation Guidance
- **First Use**: Provide a brief overview of the skill's scope and its importance for organic growth, then proceed to the Diagnosis phase.
- **Subsequent Use**: Move directly to the requested phase or the main output.
