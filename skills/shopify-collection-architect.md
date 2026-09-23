---
name: Shopify Collection Architect
description: Designs and implements an optimized collection structure for Shopify stores to improve navigation and SEO.
---

# Shopify Collection Architect

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **Navigation Audit**: Analyze the current collection hierarchy and user journeys using GA4.
- **SEO Gap Analysis**: Identify collections with poor keyword targeting or overlapping content (cannibalization).
- **Catalog Review**: Review the total number of products and their current tagging/categorization system.

### 2. Analysis (Plan)
- **Taxonomy Design**: Create a logical hierarchy of "Parent" and "Sub-collections" (simulated via navigation or tags).
- **Automation Strategy**: Plan the transition from "Manual" to "Automated" collections based on product tags and conditions.
- **URL Structure Plan**: Design SEO-friendly handles for collections to ensure clear keyword signals.

### 3. Programming (Act)
- **Collection Implementation**: Create automated collections with precise conditions to ensure product accuracy.
- **Navigation Logic**: Build advanced collection filters (facets) using Shopify's Search & Discovery app or custom Liquid logic.
- **Tailwind UI Integration**: Design a responsive collection grid using Tailwind CSS that adapts to the number of products.
- **Schema Alignment**: Implement `ItemList` schema for collection pages to improve SERP visibility.

### 4. Verification (Evaluate)
- **Indexing Check**: Use GSC to verify that new collections are indexed and showing the correct metadata.
- **User Flow Testing**: Conduct a "find-a-product" test to ensure users can reach a product in 3 clicks or fewer.
- **Performance Audit**: Ensure that collection pages with large product counts still load efficiently.
