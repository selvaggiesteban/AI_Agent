---
name: WooCommerce Upsell Cross-Sell Strategist
description: Designs and implements data-driven upsell and cross-sell mechanisms in WooCommerce to increase Average Order Value (AOV).
---

# WooCommerce Upsell Cross-Sell Strategist

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **Product Affinity Analysis**: Use GA4 and WooCommerce order history to identify which products are frequently bought together.
- **UX Audit**: Review current "Related Products" or "Upsell" sections for relevance and visual appeal.
- **Conversion Audit**: Analyze the click-through rate (CTR) of existing cross-sell recommendations.

### 2. Analysis (Plan)
- **Offer Mapping**: Create a matrix of "Primary Product" $\rightarrow$ "Upsell" (Higher Value) and "Primary Product" $\rightarrow$ "Cross-sell" (Complementary).
- **Placement Strategy**: Design the optimal points of intervention: Product Page, Cart Page, and Post-Purchase "Thank You" page.
- **Incentive Design**: Plan a tiered incentive structure (e.g., "Add X for only $Y more" or "Get 10% off if you add Z").

### 3. Programming (Act)
- **Dynamic Recommendations**: Implement custom PHP logic to fetch related products based on categories, tags, or custom metadata.
- **UI Development**: Build high-converting "Offer Modals" or "Cart Bump" sections using Tailwind CSS.
- **Logic Integration**: Use the WooCommerce API to automatically add recommended products to the cart based on a single click.
- **A/B Test Setup**: Implement different recommendation algorithms to test for the highest AOV increase.

### 4. Verification (Evaluate)
- **AOV Monitoring**: Track the average order value in WooCommerce analytics before and after implementation.
- **CTR Analysis**: Measure the conversion rate of the new upsell/cross-sell components.
- **User Friction Check**: Ensure the recommendations are helpful and not intrusive, avoiding an increase in cart abandonment.
