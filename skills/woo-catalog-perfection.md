---
name: woo-catalog-perfection
description: Elevates WooCommerce catalog quality scores to 90+ by identifying and fixing gaps in images, descriptions, brands, and identifiers to optimize AI shopping surface rankings.
---

# Woo Catalog Perfection

This skill implements a high-precision pipeline to optimize WooCommerce product data for AI-driven discovery. It follows the AgentOrchestrator's Perceive-Plan-Act-Evaluate loop to ensure data integrity and ranking improvement.

## Phase 1: Diagnosis (Perceive)
**Goal:** Establish a baseline quality score and identify specific data gaps.

1. **Catalog Extraction**: 
   - Use a Node.js script or Cloudflare Function to fetch the product catalog via the WooCommerce REST API.
   - Extract key fields: `title`, `description`, `short_description`, `images`, `categories`, `attributes` (specifically brands/MPN/GTIN).
2. **Gap Analysis**:
   - **Image Audit**: Check for missing featured images, low resolution, or lack of alt text.
   - **Content Audit**: Measure description length and keyword density against category benchmarks.
   - **Identifier Audit**: Identify products missing unique identifiers (SKU, GTIN, MPN) or Brand attributes.
3. **Scoring**: Assign a numerical score (0-100) based on the presence and quality of the above elements.

## Phase 2: Analysis (Plan)
**Goal:** Create a prioritized roadmap for remediation.

1. **Prioritization Matrix**:
   - High Priority: Products with high traffic/conversion but low scores.
   - Medium Priority: Core catalog items missing critical identifiers.
   - Low Priority: Long-tail items with minor description gaps.
2. **Remediation Strategy**:
   - **Missing Images**: Plan for scraping manufacturer assets or generating placeholders.
   - **Weak Descriptions**: Define prompts for LLM-based enrichment using existing product attributes and category context.
   - **Missing Brands/IDs**: Cross-reference existing SKUs against external manufacturer databases (using Python scripts).
3. **Execution Batching**: Group products by category to optimize API rate limits on Cloudflare Functions.

## Phase 3: Programming (Act)
**Goal:** Execute data enrichment and updates.

1. **Data Enrichment**:
   - **Content Generation**: Use an LLM to rewrite descriptions for "AI-readiness" (structured, feature-rich, and descriptive).
   - **Asset Retrieval**: Automate the upload of missing images to the WordPress Media Library via REST API.
   - **Identifier Mapping**: Inject missing Brand, MPN, and GTIN data into product attributes.
2. **Batch Processing**:
   - Deploy a Cloudflare Worker/Function to handle asynchronous batch updates to the WooCommerce API to avoid server timeouts.
   - Implement exponential backoff for API 429 (Too Many Requests) errors.
3. **Commitment**: Update the WooCommerce store in staged batches, logging all changes for potential rollback.

## Phase 4: Verification (Evaluate)
**Goal:** Validate the improvements and confirm the 90+ score.

1. **Re-Diagnosis**: Run the Phase 1 diagnosis again on the updated product set.
2. **Quality Assurance**:
   - Verify that images are rendering correctly and alt tags are present.
   - Validate that new descriptions maintain brand voice and factual accuracy.
   - Ensure unique identifiers are correctly mapped to the appropriate WooCommerce attribute fields.
3. **Ranking Simulation**: Use an AI-agent simulation to test if the products are now more "discoverable" via natural language queries (e.g., "Find me a [Brand] [Product] with [Specific Feature]").
4. **Final Report**: Output a "Before vs. After" score report for the catalog.