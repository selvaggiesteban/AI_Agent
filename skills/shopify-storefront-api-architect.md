---
name: Shopify Storefront API Architect
description: Designs and implements headless commerce experiences using the Shopify Storefront API for maximum performance.
---

# Shopify Storefront API Architect

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **Bottleneck Analysis**: Identify performance limitations of the current Liquid-based theme (e.g., slow TTFB, limited interactivity).
- **Requirement Gathering**: Define the desired user experience (e.g., instant page transitions, complex product filtering).
- **API Capability Audit**: Review the Shopify Storefront API documentation to ensure all required features (e.g., cart, checkout, product search) are available.

### 2. Analysis (Plan)
- **Architecture Design**: Choose the frontend framework (e.g., Astro) and define the data fetching strategy (Static vs. Server-side vs. Client-side).
- **GraphQL Schema Mapping**: Design the GraphQL queries to fetch only the necessary data, minimizing payload size.
- **State Management Plan**: Plan how to manage the cart state and user authentication across the headless site.

### 3. Programming (Act)
- **Frontend Implementation**: Build the storefront using Astro and Tailwind CSS, integrating the Shopify Storefront API via GraphQL.
- **Query Optimization**: Implement fragmented GraphQL queries to keep responses lean and fast.
- **Cart Logic**: Build a custom cart experience using the Storefront API's `cartCreate` and `cartLinesAdd` mutations.
- **TypeScript Integration**: Define strict types for all Shopify API responses to ensure codebase stability.

### 4. Verification (Evaluate)
- **Performance Benchmarking**: Compare the Core Web Vitals (LCP, CLS, INP) of the headless site vs. the original Liquid theme.
- **Functional Testing**: Verify the end-to-end checkout flow, from product selection to payment completion.
- **SEO Audit**: Ensure that the headless implementation maintains a proper SEO structure (SSG/SSR) and correct meta tags.
