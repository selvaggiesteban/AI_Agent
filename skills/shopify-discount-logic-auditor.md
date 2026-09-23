---
name: Shopify Discount Logic Auditor
description: Reviews and optimizes Shopify discount codes and automatic discounts to prevent revenue leakage and improve margins.
---

# Shopify Discount Logic Auditor

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **Discount Mapping**: List all active discount codes, automatic discounts, and third-party app-driven promotions.
- **Revenue Leakage Audit**: Identify overlapping discounts that allow customers to stack coupons unintentionally (e.g., "20% off" + "Free Shipping" + "Buy 1 Get 1").
- **Usage Analysis**: Review the usage rates of various discounts to identify underperforming or over-used promotions.

### 2. Analysis (Plan)
- **Margin Analysis**: Calculate the impact of current discount combinations on the average order value (AOV) and profit margins.
- **Logic Simplification**: Plan a more streamlined discount structure (e.g., replacing 10 separate codes with 3 clear tiers).
- **Exclusion Strategy**: Design a set of "exclusion rules" to protect high-margin or low-stock products from discounts.

### 3. Programming (Act)
- **Discount Configuration**: Reconfigure Shopify's native discount settings to enforce "Combine" rules strictly.
- **Automation Implementation**: Set up Shopify Flow to automatically deactivate discounts after they reach a certain usage limit.
- **UI Communication**: Use Tailwind CSS to clearly display active discounts on the product and cart pages, reducing checkout friction.
- **Validation Logic**: If using a custom app, implement TypeScript logic to validate the eligibility of a discount before it is applied.

### 4. Verification (Evaluate)
- **Scenario Testing**: Test various "stacking" scenarios in a development store to ensure no unintentional discounts are applied.
- **Margin Tracking**: Monitor the AOV and profit margins in Shopify Analytics over the next 30 days.
- **Customer Feedback**: Review cart abandonment rates to ensure the new discount logic isn't discouraging buyers.
