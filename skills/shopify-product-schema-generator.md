---
name: Shopify Product Schema Generator
description: Generates and implements high-performance JSON-LD structured data for Shopify products to maximize SERP visibility.
---

# Shopify Product Schema Generator

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **Schema Audit**: Use Google's Rich Results Test to identify missing or incorrect structured data on product pages.
- **Competitor Analysis**: Analyze top-ranking competitors in the niche to identify high-performing schema types (e.g., `AggregateRating`, `Offer`, `Brand`).
- **Data Availability**: Check the availability of required fields in the Shopify Admin (e.g., SKU, price, availability, reviews).

### 2. Analysis (Plan)
- **Schema Architecture**: Design a comprehensive JSON-LD structure that includes `Product`, `Offer`, `Review`, and `BreadcrumbList`.
- **Dynamic Mapping**: Plan how to map Shopify Liquid variables to JSON-LD properties.
- **Performance Strategy**: Plan the injection of schema as a script tag to avoid blocking the main thread.

### 3. Programming (Act)
- **Liquid Implementation**: Create a dedicated snippet (`product-schema.liquid`) that generates the JSON-LD block.
- **Logic Integration**: Implement conditional logic to handle different product types (e.g., simple vs. variants).
- **TypeScript Validation**: If using a headless Storefront API, create TypeScript interfaces to validate the schema object before rendering.
- **GSC Alignment**: Ensure the schema attributes match the requirements for Google Merchant Center.

### 4. Verification (Evaluate)
- **Validation Testing**: Run all product URLs through the Schema Markup Validator and Google Rich Results Test.
- **Search Console Monitoring**: Monitor "Enhancements" in GSC to ensure "Product snippets" are detected without errors.
- **CTR Analysis**: Track the click-through rate (CTR) in GA4/GSC to see if rich snippets are increasing traffic.
