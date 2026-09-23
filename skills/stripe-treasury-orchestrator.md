---
name: stripe-treasury-orchestrator
description: Manages corporate financial flows, treasury movements, and corporate card issuance via the Stripe Treasury API.
---

# Stripe Treasury Orchestrator

This skill enables the `AgentOrchestrator` to manage corporate financial infrastructure, including funds movement and corporate card management, following the Perceive-Plan-Act-Evaluate loop.

## Tech Stack Alignment
- **Primary:** Node.js, TypeScript (Cloudflare Functions).
- **Orchestration:** AgentOrchestrator (`core/ai_agent.py`).
- **Integration:** Stripe API, `.env` for `STRIPE_SECRET_KEY`.

---

## Execution Phases

### Phase 1: Diagnosis (Perceive)
The agent audits the corporate financial accounts and card statuses.
- **Balance Audit:** Fetch current balances across all Treasury accounts.
- **Card Scanning:** Identify active corporate cards and their current spending limits.
- **Movement Tracking:** Review recent funds transfers for discrepancies or pending authorizations.

### Phase 2: Analysis (Plan)
The agent plans the necessary treasury movements.
- **Treasury Strategy:**
    - If **Low Balance** $\rightarrow$ Plan a funds movement from a primary to a secondary account.
    - If **Card Limit Reached** $\rightarrow$ Plan a limit increase request.
- **Compliance Check:** Ensure all planned movements adhere to the project's predefined spending limits.
- **Security Validation:** Confirm Stripe restricted keys are used for specific treasury operations.

### Phase 3: Programming & Execution (Act)
The agent executes the Stripe API mutations.
- **Funds Movement:** Execute `POST /v1/treasury/financial_accounts` for moving money between accounts.
- **Card Management:** Issue new corporate cards or update existing card limits.
- **Transaction Trigger:** Initiate specific payouts or treasury transfers.

### Phase 4: Verification (Evaluate)
The agent validates the financial operations.
- **Balance Verification:** Re-query account balances to confirm the movement was successful.
- **Status Check:** Verify the new corporate cards are in "active" status.
- **Audit Trail:** Generate a detailed financial log of all movements, including transaction IDs and timestamps.
