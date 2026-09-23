---
name: Cloudflare Load Balancer Configurator
description: Sets up global traffic management, health checks, and failover strategies for high-availability applications.
---

# Cloudflare Load Balancer Configurator

This skill ensures application availability by distributing traffic across multiple origins and automatically rerouting users away from unhealthy endpoints.

## Workflow

### 1. Perceive (Diagnosis)
- **Origin Inventory**: Map all available origin servers (IPs, hostnames, regions).
- **Health Definition**: Define what constitutes a "healthy" service (e.g., HTTP 200 on `/health` every 60s).
- **Traffic Pattern Analysis**: Identify if traffic is regional or global and where the users are concentrated.
- **SLA Review**: Determine the required availability (e.g., 99.9% uptime) and maximum acceptable failover time.

### 2. Plan (Analysis)
- **Steering Policy Selection**: Choose between `Geo-steering` (nearest data center), `Dynamic steering` (best performance), or `Random`.
- **Pool Architecture**: Group origins into "Pools" based on region or capability (e.g., `US-East-Pool`, `EU-West-Pool`).
- **Failover Sequence**: Define the priority order for pools when the primary pool fails.
- **Monitoring Thresholds**: Set the number of failed checks before an origin is marked "unhealthy".

### 3. Act (Programming)
- **Pool Creation**: Configure origin pools and assign member origins.
- **Health Check Implementation**: Create and attach health checks with specific intervals and expected responses.
- **Load Balancer Provisioning**: Create the LB and link the pools and health checks.
- **DNS Integration**: Set the LB hostname as the active record for the application's domain.
- **Traffic Weighting**: Adjust weights for A/B testing or gradual migration between origins.

### 4. Evaluate (Verification)
- **Simulated Failure**: Manually shut down a target origin and verify the LB reroutes traffic to the standby pool.
- **Latency Audit**: Use `curl` from different global locations to verify that steering is sending users to the nearest pool.
- **Health Check Validation**: Verify that the LB correctly detects a 500 error on the health check endpoint and removes the origin.
- **Log Review**: Inspect Cloudflare LB logs to confirm traffic distribution matches the planned weights.
