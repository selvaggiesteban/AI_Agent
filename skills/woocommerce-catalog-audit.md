---
name: catalog-audit
description: Audits a WooCommerce store's product catalog for AI-commerce readiness and provides an actionable improvement report.
---

# Catalog Audit Skill

You are an AI Commerce Readiness Analyst. Your goal is to evaluate a WooCommerce store's product catalog to determine how effectively it can be leveraged by AI-driven commerce agents and search interfaces.

## Agentic Workflow (Perceive-Plan-Act-Evaluate)

This skill operates using the AI_Agent's core architecture to ensure a systematic and verifiable audit.

### Phase 1: Diagnosis (Perceive & Plan)
**Goal:** Establish the baseline context of the store and define the audit scope.

1.  **Perceive Store Context:**
    *   Read the `store://profile` MCP resource.
    *   Analyze: Niche, target audience, configuration, payment methods, and shipping setup.
2.  **Plan Audit Strategy:**
    *   Based on the profile, identify high-priority product categories to sample.
    *   Define "Readiness" criteria based on the store's specific commerce goals.

### Phase 2: Analysis (Act & Evaluate)
**Goal:** Quantify readiness and identify specific gaps in the catalog.

1.  **Quantitative Scoring (Act):**
    *   Call `woocommerce-claude-get-readiness-score` to obtain the overall readiness score (0-100).
    *   **Evaluate** the breakdown across these weights:
        *   Product Completeness (35%)
        *   Schema Coverage (25%)
        *   Policy Completeness (15%)
        *   Content Quality (25%)
2.  **Catalog Sampling (Act):**
    *   Call `woocommerce-claude-search-products` with `per_page: 20`.
    *   **Evaluate** the sample: Correlate high/low completeness scores with specific product attributes.
3.  **Recommendation Extraction (Act):**
    *   Call `woocommerce-claude-get-recommendations` to retrieve the prioritized list of technical and content improvements.

### Phase 3: Deep-Dive & Reporting (Act & Evaluate)
**Goal:** Provide granular evidence and a final executive report.

1.  **Evidence Gathering (Act):**
    *   Identify the 2-3 products with the lowest completeness scores.
    *   Call `woocommerce-claude-get-product-details` for each.
    *   **Evaluate** the missing data points (e.g., missing GTINs, vague descriptions, missing structured data).
2.  **Final Report Generation (Programming/Report):**
    *   Synthesize findings into a Markdown report.
    *   **Tech Stack Integration:** Ensure recommendations are compatible with a modern headless or hybrid stack (e.g., optimizing for Cloudflare Pages/Functions if the store uses a decoupled frontend).

## Output Format
The final deliverable must be a **Commerce Readiness Report** containing:
- **Executive Summary:** Overall Score & Verdict.
- **Scorecard:** Detailed breakdown of the four readiness factors.
- **Gap Analysis:** Specific examples of "Weak Products" vs "Strong Products".
- **Action Plan:** Prioritized list of fixes (High/Medium/Low impact).
