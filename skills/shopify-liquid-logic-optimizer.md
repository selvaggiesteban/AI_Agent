---
name: Shopify Liquid Logic Optimizer
description: Audits and optimizes Liquid templates to reduce server-side render time and eliminate redundant logic.
---

# Shopify Liquid Logic Optimizer

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **Identify Bottlenecks**: Analyze Shopify theme templates (`.liquid` files) for deeply nested loops, redundant `for` loops, and expensive filters.
- **Log Analysis**: Review Shopify's theme speed reports and browser developer tools (TTFB) to pinpoint slow-rendering pages.
- **Logic Mapping**: Map the current flow of data from the Storefront API or Shopify objects into the Liquid templates.

### 2. Analysis (Plan)
- **Complexity Audit**: Calculate the time complexity of current Liquid loops (e.g., $O(n^2)$ loops inside product grids).
- **Redundancy Check**: Identify repeated calls to the same object properties or expensive filters (e.g., `where`, `map`, `uniq`) within the same request.
- **Optimization Strategy**:
    - Plan the implementation of "capture" tags to store repeated calculations.
    - Identify opportunities to move logic from Liquid to the Storefront API or JavaScript.
    - Plan the replacement of nested loops with more efficient filtering logic.

### 3. Programming (Act)
- **Logic Refactoring**:
    - Replace nested `for` loops with a single loop and conditional logic where possible.
    - Use `assign` and `capture` to cache frequently used values.
    - Optimize `case/when` statements over long `if/elsif` chains.
- **Asset Alignment**: Ensure that Liquid logic does not generate bloated HTML that conflicts with Tailwind CSS utility classes.
- **TypeScript Integration**: If moving logic to the frontend, implement the logic in TypeScript using the Shopify Storefront API for better performance.

### 4. Verification (Evaluate)
- **Render Time Comparison**: Compare the TTFB (Time to First Byte) before and after the optimizations.
- **Visual Regression**: Verify that the output HTML remains identical and the UI (Tailwind CSS) is not broken.
- **Edge Case Testing**: Test with various product counts and collection sizes to ensure the logic scales efficiently.
