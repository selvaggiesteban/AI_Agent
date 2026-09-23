---
name: WooCommerce Variable Product Optimizer
description: Optimizes the configuration and presentation of variable products to improve UX and reduce loading times.
---

# WooCommerce Variable Product Optimizer

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **UX Audit**: Test the variable product selection process (dropdowns, swatches) for intuitiveness and speed.
- **Data Audit**: Review the number of variations per product; identify "variation bloat" (e.g., products with 50+ variations).
- **Performance Profiling**: Analyze the impact of `add-to-cart-variation.js` on page load and interaction delay.

### 2. Analysis (Plan)
- **UX Strategy**: Plan the replacement of standard dropdowns with visual swatches (color, image) for better conversion.
- **Data Structure Optimization**: Identify opportunities to simplify variation attributes or use "Product Add-ons" for non-essential variables.
- **Loading Strategy**: Plan the implementation of AJAX-based variation loading for products with high variation counts.

### 3. Programming (Act)
- **Swatch Implementation**: Integrate a high-performance swatch system using Tailwind CSS and minimal JavaScript.
- **AJAX Optimization**: Override the default WooCommerce variation behavior to load data asynchronously via the WooCommerce REST API.
- **Template Refactoring**: Optimize the `variable.php` template to reduce DOM depth and improve rendering speed.
- **TypeScript Validation**: Implement TypeScript logic to handle variation state management on the frontend.

### 4. Verification (Evaluate)
- **Interaction Testing**: Measure the time from variation selection to the "Add to Cart" button becoming active.
- **Conversion Tracking**: Monitor the "Add to Cart" rate for variable products vs. simple products in GA4.
- **Compatibility Check**: Ensure that variation changes correctly update the product price and image in real-time.
