---
name: GA4 Audience Segment Builder
description: Creates complex, high-value user segments in GA4 based on behavioral and demographic data for targeted marketing.
---

# GA4 Audience Segment Builder

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- Review current user behavior flows in GA4 "Explorations".
- Identify "High-Value" user patterns (e.g., users who visit pricing page 3x but haven't converted).
- Analyze churn points: Where do users drop off in the conversion funnel?
- Define target personas (e.g., "Window Shoppers", "Power Users", "At-Risk Customers").

### 2. Analysis (Plan)
- Design segment logic using GA4 dimensions and metrics:
    - **Behavioral**: `event_count` > X AND `session_source` = 'google'.
    - **Sequence**: `page_view` (Home) -> `page_view` (Pricing) -> `event` (Contact).
    - **Exclusion**: Exclude users who have already triggered the `purchase` event.
- Map segments to specific marketing actions (e.g., Google Ads Remarketing, Email drip).

### 3. Programming (Act)
- Configure audiences in the GA4 Admin panel using the Audience Builder.
- Implement "Predictive Audiences" (if available) for churn probability.
- Sync GA4 audiences with Google Ads via the linked accounts interface.
- Use `gtag` to send custom user properties for tighter segmentation:
  ```javascript
  gtag('set', 'user_properties', {
    'customer_tier': 'premium',
    'industry': 'ecommerce'
  });
  ```

### 4. Verification (Evaluate)
- Monitor "Audience Size" growth in the GA4 Audience report.
- Use "Comparison" reports to analyze the behavior of the new segment vs. all users.
- Measure the Conversion Rate (CVR) of remarketing campaigns targeting these segments.
- Audit segment accuracy using the "DebugView" for a test user.