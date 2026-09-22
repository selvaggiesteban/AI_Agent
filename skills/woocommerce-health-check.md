---
name: WooCommerce Health Check
description: Detects checkout issues, cart problems, and configuration errors silently losing sales in WooCommerce stores.
---

# WooCommerce Health Check

This skill scans WooCommerce stores for common configuration issues that break the checkout flow and cause cart abandonment. It identifies technical failures in payment gateways, AJAX URL mismatches, caching errors, and SSL problems, providing a data-driven path to revenue recovery.

## Agentic Architecture: Perceive-Plan-Act-Evaluate

The agent executes this skill using the following loop:

1.  **Perceive**: Gather current store state via `woocommerce_*` read tools and `respira_find_element` to identify existing checkout widgets and blocks.
2.  **Plan**: Map detected anomalies against known failure patterns (e.g., AJAX mismatches or caching conflicts on `/checkout`).
3.  **Act**: Execute targeted diagnostics and safe-fix suggestions on duplicate/staging pages.
4.  **Evaluate**: Compare "before" and "after" snapshots using `respira_get_snapshot` to verify the fix prevents order loss.

## Execution Phases

### Phase 1: Diagnosis (Perceive)
- **Store Audit**: Utilize `woocommerce_list_orders`, `woocommerce_sales_report`, and `woocommerce_get_stock_status` to establish a baseline of current store performance.
- **Element Validation**: Use `respira_find_element` to locate and validate the presence and functionality of critical cart and checkout widgets.
- **Technical Scan**: Check for:
    - Mobile checkout responsiveness and interaction failures.
    - Payment gateway configuration errors.
    - AJAX URL mismatches preventing "Add to Cart" or "Update Cart" actions.
    - Caching rules affecting dynamic cart/checkout pages.
    - SSL/HTTPS mixed content issues.

### Phase 2: Analysis (Plan)
- **Issue Correlation**: Cross-reference technical errors with sales data to quantify potential revenue leakage.
- **Root Cause Mapping**: Determine if issues stem from the theme, a conflicting plugin, or server-level caching (e.g., Cloudflare Pages/Functions interference).
- **Safe-Fix Strategy**: Develop a specific, low-risk remediation plan for each detected issue.

### Phase 3: Programming & Remediation (Act)
- **Pre-Fix Snapshot**: Capture the current state using `respira_get_snapshot`.
- **Safe Implementation**: Apply recommended fixes (TypeScript/Node.js scripts or WordPress configuration changes) on duplicate pages to avoid live site disruption.
- **Validation**: Re-run the Diagnosis phase on the fixed page to ensure the technical block is removed.

### Phase 4: Reporting (Evaluate)
- **Revenue Protection Report**: Generate a `respira_generate_activity_report` framed as "Prevented X lost orders / Revenue protected."
- **Final Handoff**: Provide a detailed list of implemented fixes and any remaining secondary recommendations for the tech stack (e.g., optimizing Cloudflare Turnstile for checkout bot protection).

## Tech Stack Integration
- **Primary**: Tailored for environments utilizing Cloudflare Pages/Functions for edge logic and Resend for transactional order emails.
- **Secondary**: Compatible with TypeScript-based custom blocks and Node.js middleware.
