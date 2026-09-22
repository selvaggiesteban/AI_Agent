---
name: GA4 Manager
description: Standardized approach to setting up, verifying, and optimizing Google Analytics 4 properties using a perceive-plan-act-evaluate loop.
---

# GA4 Manager

This skill provides a structured methodology for the end-to-end management of Google Analytics 4 (GA4) properties. It leverages the AI_Agent's agentic architecture to ensure that tracking is not only implemented but verified and optimized for the specific tech stack.

## Agentic Workflow (Perceive-Plan-Act-Evaluate)

The AgentOrchestrator executes this skill by cycling through the following architecture:
- **Perceive**: Scrape source code, audit existing G-IDs, and analyze the current site architecture (Astro/WordPress/Shopify).
- **Plan**: Determine the integration strategy (Admin API vs. Manual), map required custom events, and select the optimal injection method.
- **Act**: Execute the programmatic creation of properties or inject the tracking code into the codebase.
- **Evaluate**: Verify the data stream is active via real-time reports and validate event triggers against the original plan.

---

## Execution Phases

### Phase 1: Diagnosis & Perception
**Goal**: Establish the current analytics baseline.

1. **Site Audit**: Use web scraping (Firecrawl/Native) to detect existing `G-XXXXXXXXXX` tags.
2. **Stack Identification**: Identify the primary platform:
   - **Astro**: Check for component-level injection in `Layout.astro`.
   - **WordPress/Shopify/WooCommerce**: Check for plugin-based or theme-based integration.
3. **Access Review**: Verify if Google Cloud Service Account credentials are provided for Admin API access.

### Phase 2: Analysis & Planning
**Goal**: Design the tracking architecture.

1. **Setup Strategy**:
   - If no property exists $\rightarrow$ Plan for creation via `ga_admin.py` or manual UI.
   - If property exists $\rightarrow$ Plan for data stream configuration.
2. **Event Mapping**: Analyze the UI/UX to define key conversion events:
   - Lead form submissions (integrated with Resend).
   - E-commerce transactions (Shopify/WooCommerce).
   - Outbound clicks and interaction depth.
3. **Integration Mapping**: Select the implementation method:
   - **Astro/Tailwind**: Direct injection into the `<head>` of the root layout.
   - **Node.js/TypeScript**: Use appropriate wrapper libraries or raw `gtag.js`.

### Phase 3: Programming & Implementation
**Goal**: Deploy the tracking solution.

1. **Programmatic Setup**: If enabled, execute the Google Analytics Admin API scripts to create the property and data stream.
2. **Code Injection**:
   - **Astro**: Insert the GA4 global site tag into the main layout.
   - **WordPress/Shopify**: Update the `header.php` or `theme.liquid` files.
3. **Event Coding**: Implement custom `gtag('event', ...)` calls for the mapped interactions identified in Phase 2.

### Phase 4: Evaluation & Optimization
**Goal**: Validate data accuracy and refine.

1. **Connectivity Test**: Verify that the site is sending hits to the GA4 Realtime report.
2. **Event Validation**: Trigger the mapped custom events and confirm they are recorded with correct parameters.
3. **Performance Audit**: Ensure the GA4 script is not negatively impacting Core Web Vitals (LCP/CLS) on Cloudflare Pages.
4. **Report Generation**: Provide a summary of the implemented tracking and instructions for the user to view the data in the GA4 dashboard.
