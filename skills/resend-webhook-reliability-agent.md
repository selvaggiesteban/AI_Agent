---
name: Resend Webhook Reliability Agent
description: Ensures 100% delivery and processing of Resend webhooks through idempotent handlers and retry logic.
---

# Resend Webhook Reliability Agent

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **Audit Current Handling**: Review the existing webhook endpoint implementation.
- **Failure Mode Analysis**: Identify where losses occur (e.g., server timeouts, unhandled exceptions, database locks).
- **Volume Analysis**: Determine peak webhook traffic to ensure the handler can scale.
- **Logging Review**: Analyze existing logs for 4xx and 5xx errors coming from Resend.

### 2. Analysis (Plan)
- **Reliability Architecture**:
    - Plan the implementation of a "Webhook Queue" (e.g., Cloudflare Queues) to decouple reception from processing.
    - Design the Idempotency strategy (using a `webhook_id` to prevent duplicate processing).
- **Retry Strategy**: Define the exponential backoff and max-retry logic for failed processing tasks.
- **Dead Letter Queue (DLQ)**: Design a system to capture and alert on permanently failed webhooks.
- **Monitoring Specification**: Define the metrics for "Webhook Latency" and "Processing Success Rate".

### 3. Programming (Act)
- **Handler Implementation**:
    - Develop a high-performance Cloudflare Worker to receive webhooks and immediately push them to a queue.
    - Implement the consumer logic with idempotency checks (using Cloudflare KV or D1).
- **Security**: Implement Resend signature verification to prevent spoofing.
- **Error Handling**: Wrap processing in robust try-catch blocks with detailed logging of the payload and error.
- **Alerting**: Integrate with a notification system (e.g., Slack) for DLQ events.

### 4. Verification (Evaluate)
- **Chaos Testing**: Simulate server crashes and database timeouts to verify that the queue and retry logic work.
- **Idempotency Test**: Send the same webhook payload multiple times to ensure it is only processed once.
- **Load Testing**: Use a tool to flood the endpoint with webhooks to verify performance under pressure.
- **Log Audit**: Verify that every incoming webhook has a corresponding "processed" or "failed" entry in the logs.