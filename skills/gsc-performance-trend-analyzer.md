---
name: GSC Performance Trend Analyzer
description: Transforms GSC raw data into actionable growth insights by analyzing keyword volatility and CTR trends.
---

# GSC Performance Trend Analyzer

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- Fetch performance data (Queries, Pages, Countries, Devices) via GSC API.
- Compare current 3-month window vs. previous 3-month window.
- Identify "Striking Distance" keywords (Position 4-10) that are close to Page 1.
- Spot "Decaying" pages (significant drop in impressions or position over 30 days).

### 2. Analysis (Plan)
- Categorize trends:
    - **Growth**: Increasing impressions + stable position (Market expansion).
    - **Opportunity**: High impressions + low CTR (Metadata optimization needed).
    - **Risk**: Dropping position + dropping impressions (Content obsolescence).
- Calculate "Potential Traffic Gain" if striking distance keywords move to Top 3.
- Correlate GSC trends with GA4 conversion data to identify "High-ROI" keywords.

### 3. Programming (Act)
- Build a Python/Node.js script to automate the GSC data export to a CSV/JSON.
- Generate "Action Lists":
    - **Optimize Metadata**: For high-impression, low-CTR pages.
    - **Update Content**: For decaying pages.
    - **Internal Link Boost**: For striking distance keywords.
- Create a visualization (Artifact) showing the "Position vs. CTR" matrix.

### 4. Verification (Evaluate)
- Monitor "Average Position" movement for the targeted "Striking Distance" keywords.
- Track the increase in Organic CTR after metadata updates.
- Verify the recovery of "Decaying" pages through GSC performance logs.
- Measure the final impact on Organic Conversions in GA4.