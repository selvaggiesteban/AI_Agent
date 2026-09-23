---
name: GA4 Event Taxonomy Architect
description: Designs and implements a scalable event tracking schema for GA4 to ensure consistent data collection and reporting.
---

# GA4 Event Taxonomy Architect

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- Audit existing GA4 event implementation using the GA4 DebugView and BigQuery exports.
- Map current business goals (KPIs) to required user interactions (events).
- Identify "dark data" gaps where critical user journeys are not tracked.
- Analyze existing naming inconsistencies (e.g., `button_click` vs `clickedButton`).

### 2. Analysis (Plan)
- Define a hierarchical event taxonomy:
    - **Event Name**: Standardized snake_case names.
    - **Parameters**: Custom dimensions and metrics required for each event.
    - **Value**: Assigning monetary or weight values to conversion events.
- Map events to GA4 "Enhanced Measurement" to avoid duplication.
- Design the implementation map for developers (Trigger -> Event Name -> Parameters).

### 3. Programming (Act)
- Implement event tracking using Google Tag Manager (GTM) or `gtag.js`.
- Configure Custom Dimensions and Custom Metrics in the GA4 Admin interface.
- Use TypeScript to create a type-safe event wrapper for Astro/Node.js apps:
  ```typescript
  type GA4Event = 'sign_up' | 'purchase' | 'lead_form_submit';
  interface EventParams { [key: string]: string | number | boolean; }
  function trackEvent(name: GA4Event, params: EventParams) {
    window.gtag('event', name, params);
  }
  ```
- Set up GA4 Audiences based on the new taxonomy for targeted marketing.

### 4. Verification (Evaluate)
- Validate event triggers using GA4 DebugView in real-time.
- Verify data flow into BigQuery to ensure parameter persistence.
- Compare event counts against expected conversion rates.
- Document the final taxonomy in a shared data dictionary.