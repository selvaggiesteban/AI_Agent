---
name: GA4 Conversion Path Mapper
description: Visualizes and analyzes the user journeys leading to conversions to optimize the conversion rate (CRO).
---

# GA4 Conversion Path Mapper

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- Identify "Conversion Events" in GA4 (e.g., `purchase`, `generate_lead`).
- Extract "User Path" data using GA4 Explorations (Path Exploration).
- Identify the most common "First Touch" and "Last Touch" points.
- Spot "Looping" behavior: Where users go back and forth between pages without converting.

### 2. Analysis (Plan)
- Map the "Ideal Path" (Home -> Category -> Product -> Checkout).
- Contrast the "Ideal Path" with the "Actual Path" for converters vs. non-converters.
- Identify "High-Friction" pages: Pages that appear frequently in the paths of non-converters.
- Determine the "Average Time to Convert" and "Number of Sessions to Convert".

### 3. Programming (Act)
- Implement "Funnel Exploration" in GA4 to quantify drop-off at each step.
- Use TypeScript/Node.js to pull path data via GA4 Data API and visualize it in an Artifact.
- Implement "Conversion-Driven" UX changes in Astro:
    - Add "Quick-Buy" buttons on high-traffic path pages.
    - Simplify the navigation for users on the most common conversion paths.
- Set up GA4 "Custom Events" to track micro-conversions (e.g., `added_to_cart`).

### 4. Verification (Evaluate)
- Compare the "Conversion Rate" of the optimized path vs. the original path.
- Monitor the reduction in "Drop-off Rate" at high-friction points.
- Track the decrease in "Time to Convert" for new users.
- Analyze the "Attribution Model" changes in GA4 to see how different touchpoints contribute.