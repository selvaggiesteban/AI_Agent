---
name: Stripe Invoice Customizer
description: Designs and implements professional, brand-aligned Stripe invoices and receipts for B2B and B2C clients.
---

# Stripe Invoice Customizer

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **Brand Asset Audit**: Collect logos, brand colors, and typography guidelines.
- **Compliance Review**: Identify required legal fields per jurisdiction (e.g., VAT number, business address, payment terms).
- **Existing Invoice Analysis**: Review current Stripe invoice layouts and identify areas for improvement.
- **Customer Feedback**: Analyze common questions customers ask regarding invoices (e.g., "Where is my tax ID?").

### 2. Analysis (Plan)
- **Layout Design**: Plan the visual hierarchy of the invoice (Header -> Bill To/From -> Line Items -> Totals -> Footer).
- **Field Mapping**: Map internal data (e.g., custom metadata) to the Stripe invoice fields.
- **Conditional Logic**: Plan for different layouts based on customer type (e.g., a simplified receipt for B2C, a detailed invoice for B2B).
- **Technical Spec**: Decide between using Stripe's native customization or generating custom PDFs via an external API.

### 3. Programming (Act)
- **Native Customization**: Configure Stripe's branding settings (colors, logos, custom fields) via the dashboard or API.
- **Custom Field Implementation**:
    - Use the Stripe API to add `custom_fields` to invoices for specific business needs.
    - Implement logic to dynamically populate these fields based on the customer's profile.
- **PDF Automation (Optional)**: If native is insufficient, develop a Node.js service using `puppeteer` or `pdfkit` to generate custom invoices from an Astro template.

### 4. Verification (Evaluate)
- **Visual QA**: Generate sample invoices for different customer segments and verify brand alignment.
- **Legal Audit**: Verify that all required tax and legal fields are present and correct.
- **Client Testing**: Send test invoices to a small group of users to verify clarity and professionalism.
- **Cross-Device Review**: Check how the invoice looks when opened as a PDF on mobile vs. desktop.