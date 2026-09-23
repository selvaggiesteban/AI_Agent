---
name: Wrangler CLI Power User
description: Advanced orchestration and deployment of Cloudflare Workers, Pages, and KV/D1/R2 resources using Wrangler.
---

# Wrangler CLI Power User

This skill optimizes the deployment lifecycle of Cloudflare edge resources, ensuring minimal cold starts, efficient resource allocation, and seamless environment management.

## Workflow

### 1. Perceive (Diagnosis)
- **Analyze `wrangler.toml`**: Check for deprecated settings, missing environment definitions, or suboptimal compatibility dates.
- **Inspect Resource Bindings**: Verify KV namespaces, D1 databases, and R2 buckets are correctly mapped for the target environment.
- **Audit Deployment History**: Review recent deployments for frequent failures or version regressions.
- **Check Local State**: Validate `.wrangler` state and local development configurations.

### 2. Plan (Analysis)
- **Environment Strategy**: Define the promotion path (e.g., `dev` -> `staging` -> `production`).
- **Binding Optimization**: Determine if resources should be shared across environments or isolated.
- **Script Optimization**: Plan for bundle size reductions or the use of `wasm` for performance-critical paths.
- **CLI Command Chain**: Sequence the necessary `wrangler` commands for a safe rollout (e.g., `wrangler d1 migrations apply` before `wrangler deploy`).

### 3. Act (Programming)
- **Configuration Hardening**: Update `wrangler.toml` with strict compatibility dates and optimized `main` entry points.
- **Secret Management**: Securely inject environment variables using `wrangler secret put`.
- **Migration Execution**: Run D1 migrations and verify schema integrity.
- **Deployment**: Execute `wrangler deploy --env <env>` with appropriate flags for canary or blue-green patterns.
- **Resource Provisioning**: Create and link KV/D1/R2 resources via CLI where automated scripts are required.

### 4. Evaluate (Verification)
- **Log Streaming**: Use `wrangler tail` to monitor real-time requests and errors post-deploy.
- **Binding Validation**: Test API endpoints to ensure all bindings (KV, D1, etc.) are returning data.
- **Latency Audit**: Measure Time to First Byte (TTFB) across different global regions.
- **Version Rollback**: In case of failure, use `wrangler rollback` to return to the last known stable version.
