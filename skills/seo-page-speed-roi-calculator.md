---
name: SEO Page Speed ROI Calculator
description: Quantifies the potential revenue and conversion increase resulting from improvements in page load speed.
---

# SEO Page Speed ROI Calculator

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- Collect current performance metrics (LCP, TTFB) from PageSpeed Insights.
- Extract current "Conversion Rate" (CVR) and "Average Order Value" (AOV) from GA4.
- Identify "Revenue per Session" for the slowest vs. fastest pages.
- Research industry benchmarks for "Conversion Drop-off per 100ms" (e.g., Deloitte/Google studies).

### 2. Analysis (Plan)
- Create a "Performance-Revenue Correlation" model:
    - `Current Revenue = Sessions * CVR * AOV`.
    - `Estimated CVR Improvement = (Current LCP - Target LCP) * % Increase per 100ms`.
- Estimate the "Cost of Implementation" (Developer hours, Tooling).
- Calculate the "Projected ROI": `(Projected Revenue Gain - Implementation Cost) / Implementation Cost`.

### 3. Programming (Act)
- Develop a "ROI Calculator" Artifact (HTML/JS) where stakeholders can input LCP and CVR.
- Use Python to run a regression analysis on historical speed vs. conversion data from GA4/BigQuery.
- Create a "Business Case" report highlighting the most "Expensive" slow pages.
- Define "Success KPIs" (e.g., "Reducing LCP by 500ms to gain $X in monthly revenue").

### 4. Verification (Evaluate)
- After implementation, compare the "Actual Revenue Gain" against the "Projected ROI".
- Monitor the "Conversion Rate" increase in GA4 specifically for the optimized pages.
- Validate the speed improvement using CrUX (Real User Metrics).
- Recalculate the ROI to refine the model for future performance sprints.