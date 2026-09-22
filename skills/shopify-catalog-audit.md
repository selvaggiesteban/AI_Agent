---
name: shopify-catalog-audit
description: A non-mutating diagnostic skill to identify, rank, and justify product-data defects in Shopify catalogs using a deterministic indexing and sampling method.
---

# Shopify Catalog Audit

This skill implements the **FIND** stage of catalog management. Its sole purpose is to produce a ranked, justified list of product-data defects for hand-off to remediation skills. 

**CRITICAL CONSTRAINT:** This is a read-only diagnostic. Do not mutate any data. Remediation is handled by sibling skills: `shopify-catalog-cleanup`, `shopify-seo-metadata`, and `shopify-alt-text`.

## Agentic Workflow (Perceive-Plan-Act-Evaluate)

The `AgentOrchestrator` shall execute this skill following the agentic architecture:

### Phase 1: Diagnosis (Perceive)
**Goal:** Map the catalog landscape without exhaustive reading.
- **Perceive:** Connect to the Shopify Admin API. Query the total product count and basic metadata distribution.
- **Plan:** Identify the "cheap deterministic index" strategy. Instead of reading every Product Detail Page (PDP), determine which fields (e.g., `title`, `body_html`, `tags`, `variants`) will be indexed to identify patterns.
- **Act:** Execute bulk GraphQL queries to fetch the index of the entire catalog.
- **Evaluate:** Confirm the index is complete and representative of the full dataset.

### Phase 2: Analysis (Plan)
**Goal:** Form hypotheses about defect clusters.
- **Perceive:** Analyze the deterministic index for anomalies (e.g., empty descriptions, repetitive titles, missing tags, abnormal character lengths).
- **Plan:** Formulate "Defect Hypotheses" (e.g., "Products in Collection X likely lack ALT text"). 
- **Act:** Use the model to rank these hypotheses by potential impact and probability.
- **Evaluate:** Validate that the sampling slice chosen for the next phase is statistically significant.

### Phase 3: Programming/Report (Act & Evaluate)
**Goal:** Verify hypotheses and produce the audit report.
- **Perceive:** Perform "deep-reads" on the identified slices of the catalog via the Admin API.
- **Plan:** Compare the deep-read data against quality benchmarks (SEO standards, brand guidelines).
- **Act:** 
    - Generate a ranked list of defects.
    - Provide justification for each finding (e.g., "Hypothesis A confirmed: 85% of sampled items in 'Summer Wear' lack Meta-Descriptions").
    - Format the output as a structured report compatible with the `AgentOrchestrator`'s reporting module.
- **Evaluate:** Cross-reference findings against the original index to ensure no major clusters were missed.

## Tech Stack Integration

- **Primary Interface:** Shopify Admin API (GraphQL).
- **Orchestration:** Executed via `core/ai_agent.py` (Python).
- **Data Handling:** TypeScript/Node.js for high-throughput API requests if utilizing Cloudflare Workers/Functions for the indexing phase.
- **Reporting:** Final audit delivered via Astro-based internal dashboard or emailed via Resend.

## Reference Material
- **Triage Method:** Refer to `references/triage-method.md` for detailed sampling logic.
- **GraphQL Recipes:** Refer to `references/queries.md` for optimized Admin API queries.
