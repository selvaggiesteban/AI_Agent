---
name: Financial Reconciliation Agent
description: Automates the reconciliation of internal transaction logs against external payment provider statements.
---

# Financial Reconciliation Agent

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **Source Identification**: Identify all financial data sources (e.g., Stripe exports, Shopify orders, Bank statements, Internal DB).
- **Format Analysis**: Audit the formats of the data (CSV, JSON, API responses) and identify common identifiers (Transaction IDs, Order IDs).
- **Discrepancy Mapping**: Document known reasons for mismatches (Fees, Refunds, Currency Conversion, Timing differences).
- **Volume Assessment**: Determine the scale of transactions to choose the right processing strategy (in-memory vs. batch processing).

### 2. Analysis (Plan)
- **Matching Algorithm Design**:
    - Define "Perfect Match" (ID and Amount match exactly).
    - Define "Fuzzy Match" (Date and Amount match, but ID is slightly different).
    - Define "Orphan" (Transaction exists in one source but not the other).
- **Reconciliation Logic**: Plan the sequence of operations: Clean -> Align -> Match -> Flag.
- **Reporting Specification**: Design the output report (Matched, Mismatched, Unreconciled).
- **Tech Stack Selection**: Plan the use of Python (Pandas) for heavy data manipulation or Node.js for API-driven reconciliation.

### 3. Programming (Act)
- **ETL Pipeline Implementation**:
    - Build connectors to fetch data from payment providers (Stripe API) and internal DBs.
    - Implement data normalization to ensure dates and currency formats are consistent.
- **Reconciliation Engine**:
    - Develop the matching logic using Pandas (Python) or optimized TypeScript loops.
    - Implement a "Difference" calculator to quantify mismatches.
- **Automation**: Schedule the reconciliation process using GitHub Actions or Cloudflare Workers Cron Triggers.

### 4. Verification (Evaluate)
- **Accuracy Testing**: Run the agent against a known "golden dataset" with intentional errors to verify detection.
- **Performance Profiling**: Ensure the reconciliation completes within the required window for large datasets.
- **Audit Trail Review**: Verify that every match and mismatch is logged with a clear reason.
- **False Positive Audit**: Review flagged discrepancies to refine the matching algorithm.