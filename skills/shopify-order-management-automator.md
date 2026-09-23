---
name: Shopify Order Management Automator
description: Implements automation for order processing, fulfillment, and notification flows to reduce manual overhead.
---

# Shopify Order Management Automator

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **Workflow Mapping**: Document the current manual steps from "Order Placed" to "Order Delivered."
- **Pain Point Identification**: Identify repetitive tasks (e.g., manual tagging, updating fulfillment status, sending custom emails).
- **Error Analysis**: Review common mistakes in the manual process (e.g., missed notifications, incorrect shipping labels).

### 2. Analysis (Plan)
- **Automation Design**: Design a logic flow using Shopify Flow or a custom Node.js app (e.g., "If Order Value > $X $\rightarrow$ Tag as High Priority $\rightarrow$ Notify Manager").
- **Tool Selection**: Determine which parts of the flow can be handled by Shopify native tools vs. external APIs (e.g., Resend for custom emails).
- **Notification Strategy**: Plan the triggers and content for automated customer updates.

### 3. Programming (Act)
- **Shopify Flow Implementation**: Build workflows to automate tagging, customer segmentation, and internal notifications.
- **Custom App Development**: Create a Node.js middleware using the Shopify Admin API to synchronize orders with external 3PL services.
- **Email Automation**: Integrate Resend to send highly personalized, triggered emails based on order status changes.
- **TypeScript Validation**: Implement strict validation for order data moving between Shopify and external systems.

### 4. Verification (Evaluate)
- **Efficiency Measurement**: Calculate the reduction in manual hours spent on order management.
- **Accuracy Audit**: Verify that automated tags and notifications are triggering correctly for all order types.
- **Customer Satisfaction**: Monitor the "Time to Fulfillment" metric and customer feedback regarding notifications.
