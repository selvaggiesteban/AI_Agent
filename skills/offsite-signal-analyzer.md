---
name: off-site-signal-analyzer
description: Analyzes domain authority via backlink profiles and AI-assistant referral traffic to evaluate off-site trust and visibility.
---

# Off-Site Signal Analyzer

This skill analyzes the two primary off-site signal families a domain earns: the **backlink profile** (external trust graph) and the **AI-assistant referral channel** (AI engine visibility). These signals feed into the CITE framework to determine domain trust and authority.

## Agentic Workflow (Perceive-Plan-Act-Evaluate)

The `AgentOrchestrator` executes this skill using the following loop:

1.  **Perceive**: Identify the target domain and the requested analysis mode (`backlinks` or `ai-referrals`). Detect available data sources (CSV exports, GA4/GSC API access, or server logs).
2.  **Plan**: Determine the data extraction path. 
    - For `backlinks`: Plan the parsing of link databases or CSVs to extract anchor text and referring domains.
    - For `ai-referrals`: Plan the query for GA4/GSC to isolate AI-agent traffic patterns.
3.  **Act**: Execute the data processing. Perform the correlation between referral sources and landing page conversion rates.
4.  **Evaluate**: Validate that the datasets are not blended. Ensure each mode's figures are reported under distinct headings before handing off to the `domain-authority-auditor`.

## Execution Phases

### Phase 1: Diagnosis
- **Input Validation**: Confirm target domain and mode.
- **Source Audit**: Verify the integrity of the provided data source (e.g., checking CSV headers or GA4 property access).
- **Baseline Establishment**: Identify current known domain rating or existing CITE score.

### Phase 2: Analysis
Depending on the mode selected:

#### Mode: `backlinks`
- **Link Graph Mapping**: Extract referring domains and evaluate the "cleanliness" of the profile.
- **Anchor Mix Analysis**: Analyze the distribution of anchor text to identify over-optimization or natural growth.
- **Toxic Link Detection**: Identify high-risk links and generate a list of disavow candidates.
- **Gap Analysis**: Compare the backlink profile against primary competitors.

#### Mode: `ai-referrals`
- **Traffic Isolation**: Use GA4/GSC to isolate sessions originating from AI assistants (e.g., Perplexity, ChatGPT, Claude).
- **Referral Trend Tracking**: Analyze the growth curve of AI-driven citations-as-traffic.
- **Landing Page Audit**: Identify which specific pages are being cited most frequently by AI engines.
- **Conversion Correlation**: Compare AI-referral conversion rates against standard organic search traffic.

### Phase 3: Programming & Report
- **Data Synthesis**: Format findings into a structured report.
- **Constraint Check**: Ensure `backlinks` and `ai-referrals` data remain strictly separated.
- **CITE Integration**: Provide the finalized metrics to the `domain-authority-auditor` for final CITE score calculation.

## Tech Stack Integration

- **Data Processing**: TypeScript/Node.js for CSV parsing and API orchestration.
- **Analytics Integration**: GA4 and GSC via Python/Node.js scripts.
- **Reporting**: Results rendered via Astro/Tailwind CSS for internal dashboards.
- **Deployment**: Cloudflare Pages/Functions for hosting the analyzer interface.
- **Notification**: High-priority "Toxic Link" alerts sent via Resend.
