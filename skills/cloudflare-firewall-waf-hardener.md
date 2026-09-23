---
name: Cloudflare Firewall WAF Hardener
description: Configures the Web Application Firewall (WAF) to block malicious traffic, prevent DDoS, and stop common exploits.
---

# Cloudflare Firewall WAF Hardener

This skill builds a multi-layered defense system using Cloudflare's WAF, Custom Rules, and Rate Limiting to protect applications from the OWASP Top 10 and automated bots.

## Workflow

### 1. Perceive (Diagnosis)
- **Traffic Analysis**: Review "Security Events" in the Cloudflare dashboard to identify common attack patterns.
- **Attack Surface Mapping**: Identify sensitive endpoints (e.g., `/admin`, `/login`, `/api/upload`).
- **False Positive Audit**: Check for legitimate users being blocked by default rules.
- **Log Review**: Analyze HTTP request headers and payloads of blocked requests.

### 2. Plan (Analysis)
- **Rule Hierarchy**: Design a layered approach: (1) IP Blocklist -> (2) Geo-blocking -> (3) Rate Limiting -> (4) WAF Custom Rules.
- **Challenge Strategy**: Determine when to use `Block` vs `Managed Challenge` (Turnstile) vs `JS Challenge`.
- **Threat Level Definition**: Define the criteria for "high-risk" traffic (e.g., known bad ASNs, specific User-Agents).
- **Exception Mapping**: Identify internal IPs or trusted partners that need to bypass certain rules.

### 3. Act (Programming)
- **Custom Rule Implementation**: Write expression-based rules (e.g., `(http.request.uri.path contains "/admin" and ip.src ne 1.2.3.4)`) to block unauthorized access.
- **Rate Limit Configuration**: Set thresholds for sensitive endpoints to prevent brute-force attacks.
- **WAF Managed Rules Tuning**: Enable specific OWASP rule sets and disable those causing false positives.
- **Bot Management**: Configure Bot Fight Mode and custom rules to block aggressive scrapers.
- **Security Level Adjustment**: Tune the "Security Level" (Essentially Off -> I'm Under Attack) based on the current threat climate.

### 4. Evaluate (Verification)
- **Penetration Testing**: Use tools like `curl` or `Postman` to simulate attacks and verify they are blocked.
- **False Positive Monitoring**: Review logs to ensure legitimate traffic is still flowing.
- **Challenge Effectiveness**: Verify that Turnstile challenges are appearing for high-risk traffic but not for trusted users.
- **Performance Audit**: Ensure that complex WAF rules aren't introducing significant latency to requests.
