---
name: Stripe Tax Compliance Auditor
description: Audits and configures Stripe Tax settings to ensure global VAT/GST/Sales Tax compliance.
---

# Stripe Tax Compliance Auditor

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **Jurisdiction Audit**: Identify all countries and states where the business has a "tax nexus" (physical or economic presence).
- **Product Taxability Review**: Categorize products/services according to global tax codes (e.g., digital services vs. physical goods).
- **Current Config Audit**: Review existing Stripe Tax settings and registration status.
- **Regulation Mapping**: Identify specific tax requirements for target regions (e.g., EU VAT OSS, US Sales Tax).

### 2. Analysis (Plan)
- **Tax Calculation Logic**: Map how taxes should be calculated (e.g., inclusive vs. exclusive) per region.
- **Registration Roadmap**: List the tax authorities where the business needs to register based on current volume.
- **Audit Plan**: Design a sampling method to verify that taxes are being collected correctly on past invoices.
- **Integration Strategy**: Plan how tax data will be exported for official tax filings.

### 3. Programming (Act)
- **Configuration**:
    - Enable and configure Stripe Tax in the dashboard or via API.
    - Set up the correct tax categories for each Stripe Product.
- **Integration**:
    - Ensure the checkout flow captures the correct customer address for tax calculation.
    - Implement logic to handle tax-exempt customers (e.g., B2B customers with valid VAT IDs).
- **Reporting**: Develop a Python script to aggregate tax collected by jurisdiction from Stripe's reports.

### 4. Verification (Evaluate)
- **Calculation Validation**: Use a tax calculator (e.g., Avalara) to cross-verify Stripe's tax calculations for various addresses.
- **Invoice Audit**: Randomly sample 50 invoices and verify the tax amount against local laws.
- **Compliance Check**: Verify that tax IDs are correctly displayed on invoices as required by law (e.g., EU VAT invoices).
- **Exception Review**: Analyze any failed tax calculations or "tax not applicable" flags.