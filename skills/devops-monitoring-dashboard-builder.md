---
name: DevOps Monitoring Dashboard Builder
description: Designs and implements observability dashboards that correlate infrastructure metrics with application performance.
---

# DevOps Monitoring Dashboard Builder

This skill creates actionable observability views (using Grafana, Datadog, or Cloudflare Analytics) that allow teams to detect and diagnose issues in seconds.

## Workflow

### 1. Perceive (Diagnosis)
- **KPI Identification**: Determine the "Golden Signals" for the app (Latency, Traffic, Errors, Saturation).
- **Data Source Audit**: Identify where metrics live (e.g., Prometheus, Cloudflare Logs, AWS CloudWatch, Python logs).
- **Stakeholder Mapping**: Define who the dashboard is for (e.g., SREs need deep infra metrics; PMs need business KPIs).
- **Alert Gap Analysis**: Identify current "silent failures" that aren't caught by existing monitoring.

### 2. Plan (Analysis)
- **Information Architecture**: Design the layout (e.g., Top: Global Health -> Middle: Per-Service Metrics -> Bottom: Detailed Logs).
- **Visual Encoding**: Choose the right chart type for each metric (e.g., Time-series for latency, Gauges for CPU, Heatmaps for request distribution).
- **Alert Thresholding**: Define the "Danger Zone" for metrics (e.g., P99 Latency > 2s = Critical).
- **Query Optimization**: Plan efficient PromQL or SQL queries to avoid slowing down the dashboard.

### 3. Act (Programming)
- **DataSource Connection**: Configure connections to Prometheus, Loki, or Cloudflare.
- **Panel Implementation**: Build the visual components (e.g., "Error Rate %" over the last 24h).
- **Dynamic Filtering**: Add dashboard variables (e.g., `Environment: Prod/Staging`, `Region: US/EU`) for easy drilling.
- **Alert Integration**: Connect dashboard thresholds to notification channels (Slack, PagerDuty).
- **Log Correlation**: Implement "Jump to Logs" links that filter logs based on the time window selected in the metric chart.

### 4. Evaluate (Verification)
- **Actionability Test**: Perform a "Fire Drill" (simulate an error) and verify if the dashboard makes the root cause obvious.
- **Load Test**: Ensure the dashboard remains responsive when querying large datasets.
- **Visual Review**: Verify that the layout is intuitive and not cluttered with "noise".
- **Alert Accuracy**: Confirm that alerts trigger exactly when the threshold is hit and not before.
