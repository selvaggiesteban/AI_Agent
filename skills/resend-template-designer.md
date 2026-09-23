---
name: Resend Template Designer
description: Designs, tests, and deploys high-conversion transactional email templates using Resend and Tailwind CSS.
---

# Resend Template Designer

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **Audit Current State**: Analyze existing email templates or design requirements.
- **Brand Alignment**: Review brand guidelines, color palettes (Tailwind config), and typography.
- **Goal Identification**: Determine the primary action (CTA) and user journey for the transactional email.
- **Constraint Mapping**: Identify dynamic variables (e.g., `{{user_name}}`, `{{order_id}}`) required from the backend.

### 2. Analysis (Plan)
- **Wireframing**: Map the information hierarchy (Header -> Value Prop -> CTA -> Footer).
- **Technical Specification**:
    - Define the layout strategy (Fluid hybrid or table-based for maximum client compatibility).
    - Map Tailwind CSS utility classes to inline styles for email client support.
    - Specify the data schema for Resend's dynamic tags.
- **Testing Matrix**: Define target email clients (Gmail, Outlook, Apple Mail) and device breakpoints.

### 3. Programming (Act)
- **Template Construction**:
    - Use Astro or a dedicated React-email component library to build the template.
    - Implement Tailwind CSS for rapid styling, ensuring a fallback for non-supporting clients.
    - Integrate Resend SDK for template management.
- **Variable Integration**: Implement the dynamic content placeholders using Resend's template syntax.
- **Deployment**: Push the template to Resend via API or the dashboard.

### 4. Verification (Evaluate)
- **Visual QA**: Use tools like Litmus or Email on Acid to verify rendering across clients.
- **Functional Testing**: Send test emails with real data payloads via Resend to verify variable interpolation.
- **Deliverability Check**: Ensure the HTML is lean, avoids spam-triggering patterns, and includes a valid unsubscribe link.
- **Iteration**: Refine styles based on rendering issues found in the QA phase.