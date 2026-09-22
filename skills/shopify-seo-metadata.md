---
name: shopify-seo-metadata-backfill
description: Safe-mode backfill of missing search-appearance metadata across Shopify products, collections, pages, and blog articles.
---

# Shopify SEO Metadata Backfill

This skill performs a "safe-mode" backfill of missing search-appearance metadata (SEO titles and meta descriptions). The core operating principle is **fill blanks, never overwrite**: a merchant's hand-written metadata is prioritized over model-generated content.

## Agentic Workflow (Perceive-Plan-Act-Evaluate)

The `AgentOrchestrator` shall execute this skill using the following phased approach:

### Phase 1: Diagnosis (Perceive)
**Goal:** Identify the scope of missing metadata.
- **Action:** Invoke `shopify-catalog-audit` to scan the store's products, collections, pages, and blog articles.
- **Perception:** Extract a list of resource IDs where `seo_title` or `meta_description` is null or empty.
- **Constraint:** Ensure the agent distinguishes between "empty" and "intentionally blank" (if applicable).

### Phase 2: Strategy (Plan)
**Goal:** Determine the optimal metadata generation strategy for the identified gaps.
- **Action:** 
    1. Analyze the existing high-performing metadata in the store to establish a brand voice and length guideline.
    2. Group the missing resources by type (e.g., all "Collections" together) to maintain thematic consistency.
    3. Map each missing field to a generation prompt tailored to the Shopify resource type.
- **Plan:** Create a queue of API updates, ensuring the "fill blanks only" rule is strictly enforced in the logic.

### Phase 3: Execution (Act)
**Goal:** Programmatically update the missing metadata via the Shopify Admin API.
- **Tech Stack Implementation:**
    - **Runtime:** Use `Node.js` or `Python` functions (deployed via Cloudflare Functions) to handle the API requests.
    - **API:** Utilize the Shopify Admin GraphQL API for efficient bulk mutations.
    - **Logic:** 
        ```typescript
        if (!resource.seo.title) {
            resource.seo.title = generatedTitle;
        }
        // repeat for meta_description
        ```
- **Safety:** Implement rate-limiting to respect Shopify API quotas and avoid triggering store-wide locks.

### Phase 4: Verification (Evaluate)
**Goal:** Validate that the backfill was successful and no existing data was overwritten.
- **Action:** 
    1. Re-run a targeted `shopify-catalog-audit` on the modified resources.
    2. Compare the "Before" and "After" states to confirm that previously populated fields remain unchanged.
    3. Log the total number of fields filled vs. the total number of resources processed.
- **Report:** Deliver a summary report to the user detailing the coverage increase.

## Tech Stack Integration
- **Primary:** Cloudflare Functions (for execution logic), TypeScript (for type-safe API interactions).
- **Secondary:** Shopify Admin API, Node.js.
- **Orchestration:** Managed by `core/ai_agent.py` via the `AgentOrchestrator`.

## Dependencies
- `shopify-catalog-audit`: Required for the Diagnosis phase.
- `shopify-alt-text` / `shopify-json-ld`: Sister skills for complementary SEO optimization.