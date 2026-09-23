---
name: Shopify App Conflict Resolver
description: Diagnoses and resolves performance and functional conflicts between installed Shopify apps.
---

# Shopify App Conflict Resolver

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **Conflict Identification**: Identify overlapping app functionality (e.g., two apps both attempting to modify the "Add to Cart" button).
- **Performance Profiling**: Use Chrome DevTools to find apps injecting heavy JavaScript or CSS that causes Layout Shift (CLS) or slows down LCP.
- **Error Log Review**: Check the browser console for JavaScript errors caused by app script collisions.

### 2. Analysis (Plan)
- **Dependency Mapping**: Map which apps modify which parts of the Liquid templates and which inject scripts into the `<head>` or `<body>`.
- **Priority Ranking**: Determine which app provides the critical functionality and should take precedence in the DOM.
- **Removal Strategy**: Plan the removal of redundant apps to reduce the overall script load.

### 3. Programming (Act)
- **Script Management**: Use `theme.liquid` or app blocks to reorganize the loading order of app scripts.
- **CSS Overrides**: Write specific Tailwind CSS utility overrides to fix UI glitches caused by app-injected styles.
- **Liquid Cleanup**: Remove "ghost" code—snippets left behind by uninstalled apps—from `.liquid` files.
- **JS Isolation**: Use JavaScript to prevent multiple apps from attaching the same event listener to a single DOM element.

### 4. Verification (Evaluate)
- **Functional Testing**: Verify that all remaining apps are functioning as intended without interfering with each other.
- **Speed Benchmarking**: Compare PageSpeed Insights scores before and after app cleanup.
- **Visual Audit**: Ensure the store's UI is consistent across all device types and browsers.
