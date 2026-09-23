---
name: Resend Audience Segmenter
description: Implements advanced audience segmentation for targeted email campaigns based on user behavior and metadata.
---

# Resend Audience Segmenter

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **Data Audit**: Review available user metadata (e.g., signup date, last login, purchase history, industry).
- **Goal Identification**: Define the purpose of the segments (e.g., "Re-engage inactive users", "Upsell power users").
- **Tooling Review**: Evaluate how user data is currently stored (e.g., Cloudflare D1, PostgreSQL, MongoDB).
- **Existing List Analysis**: Audit current Resend audiences for overlap or redundancy.

### 2. Analysis (Plan)
- **Segmentation Logic**:
    - Define "Power Users" (e.g., >10 logins/month).
    - Define "At-Risk Users" (e.g., no login in 14 days).
    - Define "High-Value Customers" (e.g., MRR > $100).
- **Sync Strategy**: Plan whether to use "Dynamic Sync" (real-time API updates) or "Batch Sync" (nightly script).
- **Tagging Taxonomy**: Design a consistent tagging system for Resend audiences (e.g., `status:active`, `tier:gold`).
- **Campaign Mapping**: Map each segment to a specific Resend template and send schedule.

### 3. Programming (Act)
- **Segmentation Engine**:
    - Develop a Python or TypeScript script to query the database and identify users for each segment.
- **Resend Integration**:
    - Implement API calls to `audiences.create` and `contacts.create` to manage segments in Resend.
    - Automate the adding/removing of contacts from audiences based on behavior changes.
- **Automation**: Schedule the segmentation sync using GitHub Actions or a Cron trigger.

### 4. Verification (Evaluate)
- **Segment Accuracy**: Manually verify a sample of users in each segment against the database.
- **Conversion Testing**: Run an A/B test comparing a segmented campaign vs. a generic blast.
- **Sync Latency Review**: Measure the time it takes for a user's behavior change to reflect in their Resend segment.
- **List Growth Audit**: Monitor the size and health of each segment over time.