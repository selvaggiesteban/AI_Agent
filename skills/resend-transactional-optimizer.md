---
name: resend-transactional-optimizer
description: High-performance transactional email orchestration using Resend, supporting batching, scheduling, and delivery auditing.
---

# Resend Transactional Optimizer

This skill optimizes the delivery of transactional emails by leveraging Resend's batching and scheduling capabilities, ensuring maximum deliverability and minimum API latency.

## Tech Stack Alignment
- **Primary:** TypeScript, Cloudflare Pages/Functions.
- **Orchestration:** AgentOrchestrator (`core/ai_agent.py`).
- **Integration:** Resend API, `.env` for `RESEND_API_KEY`.

---

## Execution Phases

### Phase 1: Diagnosis (Perceive)
The agent analyzes the email queue and delivery health.
- **Queue Audit:** Identify the number of pending notifications (e.g., deployment alerts, payment confirmations).
- **Delivery Analysis:** Scan Resend logs for bounce rates or spam flags on recent broadcasts.
- **Payload Check:** Verify that all email templates have the required dynamic variables (e.g., `{{user_name}}`).

### Phase 2: Analysis (Plan)
The agent chooses the most efficient delivery method.
- **Routing Strategy:**
    - If **Single Email** $\rightarrow$ Plan `POST /emails` for immediate delivery.
    - If **Multiple Emails (<100)** $\rightarrow$ Plan `POST /emails/batch` to minimize API roundtrips.
    - If **Future Delivery** $\rightarrow$ Plan a scheduled send using the `send_at` parameter.
- **Template Selection:** Match the notification type to the appropriate Resend template.

### Phase 3: Programming & Execution (Act)
The agent executes the delivery.
- **Batch Execution:** Dispatch grouped emails via the batch endpoint to stay within the 2 req/sec rate limit.
- **Dynamic Injection:** Programmatically populate templates with real-time data from the `StateStore` or external APIs.
- **Scheduling:** Set the `send_at` timestamp for time-zone optimized delivery.

### Phase 4: Verification (Evaluate)
The agent ensures the emails reached their destination.
- **Delivery Probe:** Use the Resend API to check the status of the dispatched emails (Sent $\rightarrow$ Delivered).
- **Error Handling:** If a batch fails, the agent identifies the specific failed email and retries it individually.
- **Audit Log:** Record the delivery success rate and latency in the project's observability logs.
