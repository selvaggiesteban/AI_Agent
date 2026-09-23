---
name: Resend Email Deliverability Auditor
description: Analyzes and optimizes email delivery rates by auditing SPF, DKIM, DMARC, and content triggers.
---

# Resend Email Deliverability Auditor

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **Infrastructure Audit**: Check DNS settings for SPF, DKIM, and DMARC records.
- **Metric Baseline**: Analyze current delivery, bounce, and complaint rates via Resend's analytics.
- **Sender Reputation Check**: Evaluate the domain's reputation using tools like SenderScore or Postmaster Tools.
- **Content Review**: Analyze current email templates for common spam triggers (e.g., excessive caps, "spammy" keywords).

### 2. Analysis (Plan)
- **DNS Optimization Plan**: Specify the correct record updates for the specific domain and Resend configuration.
- **Content Strategy**: Plan the removal of trigger words and the optimization of the text-to-image ratio.
- **List Hygiene Strategy**: Design a process for pruning inactive subscribers and handling hard bounces.
- **Warm-up Schedule**: Create a gradual volume increase plan for new domains or IP addresses.

### 3. Programming (Act)
- **DNS Implementation**: Update DNS records via the provider API or manual configuration.
- **Template Refactoring**:
    - Edit Resend templates to improve deliverability.
    - Implement personalized subject lines to increase open rates.
- **Automation Setup**:
    - Implement a webhook handler for `email.bounce` and `email.complaint` to automatically mark users as "unsubscribed" in the DB.
    - Integrate a deliverability monitoring tool via API.

### 4. Verification (Evaluate)
- **Validation**: Verify DNS propagation using `dig` or online DNS checkers.
- **A/B Testing**: Run split tests on content versions to see which has a higher inbox placement rate.
- **Post-Optimization Audit**: Monitor delivery metrics in Resend for 7-14 days to verify improvement.
- **Ongoing Monitoring**: Set up alerts for sudden spikes in bounce rates.