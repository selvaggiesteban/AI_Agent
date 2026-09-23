---
name: mercado-pago-financial-ops
description: Manages payment processing, refunds, and merchant orders via Mercado Pago for Latin American operations.
---

# Mercado Pago Financial Ops

This skill enables the `AgentOrchestrator` to handle financial transactions and payment audits using the Mercado Pago API, following the Perceive-Plan-Act-Evaluate cycle.

## Tech Stack Alignment
- **Primary:** Python, Node.js (deployed via Cloudflare Functions).
- **Orchestration:** AgentOrchestrator (`core/ai_agent.py`).
- **Integration:** Mercado Pago API, `.env` for secret management.

---

## Execution Phases

### Phase 1: Diagnosis (Perceive)
The agent audits current payment statuses and merchant account health.
- **Transaction Scan:** Fetch recent payments and identify "Pending" or "Failed" transactions.
- **Refund Audit:** Check for open refund requests that require processing.
- **Order Verification:** Compare Mercado Pago orders against the internal order database (Shopify/WooCommerce).

### Phase 2: Analysis (Plan)
The agent determines the financial actions required.
- **Resolution Strategy:**
    - If **Failed Payment** $\rightarrow$ Plan a notification to the user via Resend.
    - If **Valid Refund Request** $\rightarrow$ Plan a `POST /v1/payments/{id}/refund` call.
- **Installment Analysis:** For new payments, determine the optimal installment plan based on the user's regional configuration.
- **API Safety:** Verify `MP_ACCESS_TOKEN` is configured in `.env`.

### Phase 3: Programming & Execution (Act)
The agent executes the financial operations.
- **Payment Processing:** Trigger payment requests or generate QR codes for Point of Sale (POS) operations.
- **Refund Execution:** Programmatically process approved refunds.
- **Order Update:** Update the status of the order in the e-commerce backend (Shopify/WooCommerce) upon payment confirmation.

### Phase 4: Verification (Evaluate)
The agent validates the transaction outcome.
- **Payment Confirmation:** Verify the payment status is now "approved".
- **Refund Validation:** Confirm the refund was successfully processed by Mercado Pago.
- **Financial Reporting:** Generate a transaction summary report including payment IDs and timestamps.
