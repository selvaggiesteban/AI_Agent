---
name: WooCommerce Payment Gateway Auditor
description: Audits payment gateway configurations and integrations for security, stability, and transaction success rates.
---

# WooCommerce Payment Gateway Auditor

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **Transaction Review**: Analyze failed transaction logs in WooCommerce to identify common error codes from payment gateways (e.g., Stripe, PayPal).
- **Security Audit**: Check for outdated payment plugins and verify that SSL/TLS configurations are current.
- **User Experience Audit**: Test the payment flow on multiple devices to identify "silent failures" or poor error messaging.

### 2. Analysis (Plan)
- **Failure Analysis**: Categorize transaction failures into Gateway Errors, User Errors (e.g., insufficient funds), and Integration Errors (e.g., API timeout).
- **Configuration Audit**: Review API keys, webhook settings, and currency compatibility.
- **Redundancy Plan**: Design a failover strategy (e.g., offering a second payment method if the primary one fails).

### 3. Programming (Act)
- **API Optimization**: Update payment gateway API versions and optimize webhook handlers using Node.js or PHP.
- **Error Handling**: Implement custom error messages for common gateway failures to guide users toward a solution.
- **Security Hardening**: Ensure all payment-related data is handled via encrypted channels and that no sensitive data is logged.
- **Turnstile Integration**: Add Cloudflare Turnstile to the payment submission to prevent card-testing attacks.

### 4. Verification (Evaluate)
- **Success Rate Monitoring**: Compare the transaction success rate before and after the audit.
- **Sandbox Testing**: Perform comprehensive test transactions in the gateway's sandbox environment.
- **Latency Check**: Measure the response time of the payment gateway API calls during the checkout process.
