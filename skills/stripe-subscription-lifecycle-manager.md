---
name: Stripe Subscription Lifecycle Manager
description: Orchestrates the full subscription lifecycle, including trials, upgrades, downgrades, and churn prevention.
---

# Stripe Subscription Lifecycle Manager

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **Current State Audit**: Analyze the existing Stripe Product and Price architecture.
- **Lifecycle Mapping**: Identify the stages of the customer journey: Trial -> Active -> Past Due -> Canceled.
- **Churn Analysis**: Review historical data to identify common drop-off points in the subscription flow.
- **Requirement Gathering**: Define rules for prorating upgrades/downgrades and grace periods.

### 2. Analysis (Plan)
- **State Machine Design**: Map the transitions between subscription statuses (e.g., `trailing` to `active`).
- **Webhook Strategy**: Design the handling for `customer.subscription.updated`, `invoice.payment_failed`, and `customer.subscription.deleted`.
- **Communication Plan**: Plan the automated emails (Resend) for payment failures, renewal reminders, and win-back offers.
- **Logic Specification**: Define the TypeScript logic for handling prorations and credit balances.

### 3. Programming (Act)
- **Implementation**:
    - Develop Cloudflare Workers/Functions to handle Stripe webhooks.
    - Implement the subscription update logic using the Stripe Node.js SDK.
    - Create the portal integration for self-service subscription management.
- **Integration**:
    - Connect subscription state changes to internal databases (e.g., Cloudflare D1).
    - Trigger Resend transactional emails based on subscription events.
- **Security**: Implement Stripe Signature verification for all incoming webhooks.

### 4. Verification (Evaluate)
- **Scenario Testing**: Execute end-to-end tests for:
    - Successful trial conversion.
    - Payment failure and retry sequence (Dunning).
    - Mid-cycle upgrade with proration.
    - Immediate cancellation vs. cancellation at period end.
- **Edge Case Audit**: Test behavior for expired credit cards and disputed payments.
- **Performance Review**: Ensure webhook responses are returned within Stripe's timeout limits.