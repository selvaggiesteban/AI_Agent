---
name: seo-monitoring
description: Comprehensive SEO data analysis and monitoring system for tracking indexing, traffic, keywords, and backlinks. Use when the user mentions "SEO data analysis," "SEO monitoring," "article database," "traffic benchmark," "penalty recovery," "SEO dashboard," "keyword tracking," "ranking monitoring," "indexing report," or "backlink monitoring."
---

# Skill: SEO Monitoring

This skill guides the AI Agent through the implementation and management of a holistic SEO data analysis system. It leverages a phased approach to move from initial data perception to actionable reporting, integrated within the AI_Agent's agentic architecture.

## Agentic Workflow (Perceive-Plan-Act-Evaluate)

The Agent should execute this skill using the following cycle:
1. **Perceive**: Extract current SEO metrics from GSC, GA4, and third-party SEO tools. Identify gaps in indexing or traffic drops.
2. **Plan**: Define the monitoring frequency, target keywords for the article database, and the benchmark baseline.
3. **Act**: Configure API integrations (GSC/GA4), build the tracking database, and implement monitoring dashboards.
4. **Evaluate**: Compare actual performance against the natural traffic benchmark and adjust the optimization strategy.

## Execution Phases

### Phase 1: Diagnosis (Perceive & Analyze)
**Goal**: Establish the current state of the site's SEO health.

1. **Indexing Audit**:
    - Check **Pages indexed vs. not indexed** via GSC.
    - Verify **Index coverage** (target pages must be findable).
    - **Action**: If critical pages are missing, trigger the `indexing` skill.
2. **Traffic Baseline**:
    - Analyze **Total traffic** and **Subdirectory traffic** via GA4.
    - Identify **Organic by page/country** to find high-performing regions.
3. **Keyword & Backlink Snapshot**:
    - Map **Rank changes** and **Keyword count** per page.
    - Evaluate **Referring domains vs. backlinks** ratio to assess link quality.

### Phase 2: Architecture & Setup (Plan & Act)
**Goal**: Build the infrastructure for continuous monitoring.

1. **Tool Stack Integration**:
    - **Primary Data**: Google Search Console (GSC) API, GA4.
    - **Secondary Data**: Third-party SEO tools for competitive benchmarks.
    - **Implementation**: Use Python/Node.js functions deployed on **Cloudflare Pages/Functions** to automate data fetching.
2. **Article Database Construction**:
    - Create a structured database (TypeScript/Python) tracking:
      - `URL`, `Publish Date`, `Target Keywords`.
      - `Index Status`, `Current Rank`, `Traffic`, `Backlinks`.
      - `Performance vs. Benchmark`.
3. **Natural Traffic Benchmark**:
    - Set a baseline in GA4 (Acquisition > Traffic acquisition).
    - Record monthly totals to detect long-term trends.

### Phase 3: Optimization & Recovery (Act & Evaluate)
**Goal**: Improve metrics and recover from penalties.

1. **Traffic Diversification**:
    - Audit search share (keep organic $\approx 75\%$ or less).
    - Increase direct and referral share via brand building and social engagement.
2. **Penalty Recovery Workflow**:
    - **Identify**: Match traffic drops to specific algorithm update dates.
    - **Analyze**: Audit site quality and content thinness.
    - **Execute**: Implement fixes and monitor for $\approx 3$ months.
3. **Monitoring Loop**:
    - Populate the **Monthly Record Template** (sessions, channel share, referring domains, articles published).

## Tech Stack Alignment

- **Automation**: Use **Cloudflare Functions** to pull GSC API data and push to the Article Database.
- **Dashboarding**: Build a monitoring UI using **Astro** and **Tailwind CSS** for high-performance, static-first reporting.
- **Notifications**: Use **Resend** to send monthly SEO health reports to stakeholders.
- **Security**: Implement **Cloudflare Turnstile** on any public-facing SEO tool or submission form.
- **CMS Integration**: For sites on **WordPress, Shopify, or WooCommerce**, ensure GSC/GA4 tags are correctly deployed via header/footer injections or plugins.

## Monitoring Metrics Reference

| Category | Metric | Source | Agent Focus |
| :--- | :--- | :--- | :--- |
| **Traffic** | Total Sessions, Channel Share | GA4 | Trend Analysis |
| **Engagement** | Pages/Session, Bounce Rate | GA4 | Content Quality |
| **Backlinks** | Domain Authority, Ref. Domains | SEO Tools | Authority Growth |
| **Keywords** | Keyword Count, Rank Movement | GSC/Tools | Visibility |
| **Content** | Published vs. Indexed | GSC | Pipeline Efficiency |

## Output Requirements

When completing this skill, the Agent must provide:
- A **Core Metrics Summary** (Indexing, Traffic, Keywords, Backlinks).
- A **Benchmark Analysis** showing current performance vs. baseline.
- The **Article Database Structure** implemented or proposed.
- A **Customized Monitoring Table** with specific owners and frequencies.
- A prioritized list of **Action Items** for the next 30 days.

## Related Skills
- `traffic-analysis`: Deep dive into attribution and diversification.
- `analytics-tracking`: GA4 event configuration and User ID setup.
- `google-search-console`: API integration and indexing fixes.
- `backlink-analysis`: Audit of toxic links and authority building.
