---
name: SaaS Unit Economics Calculator
description: Calculates and analyzes LTV, CAC, Churn, and Payback Period to determine the financial health of a SaaS business.
---

# SaaS Unit Economics Calculator

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **Revenue Audit**: Extract MRR (Monthly Recurring Revenue) and ARPU (Average Revenue Per User) from Stripe.
- **Cost Audit**: Gather all acquisition costs (Ad spend, Sales commissions, Content marketing) from marketing tools.
- **Retention Audit**: Calculate the churn rate (Logo Churn vs. Revenue Churn) from subscription data.
- **COGS Analysis**: Identify the cost of serving one customer (Server costs, Support, Third-party API fees).

### 2. Analysis (Plan)
- **Formula Specification**:
    - LTV (Lifetime Value) = (ARPU * Gross Margin %) / Monthly Churn Rate.
    - CAC (Customer Acquisition Cost) = Total Sales & Marketing Spend / New Customers Acquired.
    - LTV/CAC Ratio = Target > 3x.
    - Payback Period = CAC / (ARPU * Gross Margin %).
- **Data Pipeline Design**: Plan how to automate the extraction of these metrics from Stripe and internal DBs.
- **Benchmark Selection**: Identify industry benchmarks for the specific SaaS niche.

### 3. Programming (Act)
- **Calculator Implementation**:
    - Develop a Python script (using Pandas) to calculate these metrics from raw CSV/API exports.
    - Build a dashboard (Astro + Tailwind + Chart.js) to visualize these metrics over time.
- **Automation**: Create a monthly report generator that emails the unit economics to the leadership team via Resend.
- **Scenario Modeling**: Implement a "What-If" tool to see how changes in churn or ARPU affect the LTV/CAC ratio.

### 4. Verification (Evaluate)
- **Data Integrity Check**: Verify that the calculated MRR matches the Stripe dashboard exactly.
- **Sensitivity Analysis**: Check how a small change in churn (e.g., 2% to 3%) impacts the overall LTV.
- **Benchmark Comparison**: Compare the results against the identified industry standards.
- **Actionable Insight Generation**: Determine if the results suggest a need for "Price Increase" or "Churn Reduction" strategies.