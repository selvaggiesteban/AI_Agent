---
name: CI/CD Secret Rotation Manager
description: Implements automated and manual rotation of API keys, certificates, and passwords across the delivery pipeline.
---

# CI/CD Secret Rotation Manager

This skill reduces the impact of credential leakage by implementing short-lived secrets and automated rotation policies across GitHub, Cloudflare, and backend services.

## Workflow

### 1. Perceive (Diagnosis)
- **Secret Inventory**: Locate all secrets stored in GitHub Actions, Cloudflare Pages, and `.env` files.
- **Leakage Audit**: Search commit history for accidentally committed secrets using `trufflehog` or `gitleaks`.
- **Lifecycle Review**: Identify secrets that have never been rotated or have no defined expiration.
- **Dependency Mapping**: Map which services depend on which secrets to understand the "blast radius" of a rotation.

### 2. Plan (Analysis)
- **Rotation Strategy**: Decide between `Manual-Scheduled` (e.g., every 90 days) or `Automated-API` (using a secret manager).
- **Zero-Downtime Path**: Plan the "Double-Secret" window (where both old and new keys are valid) to prevent outages during rotation.
- **Storage Transition**: Plan the move from GitHub Secrets to a dedicated manager like HashiCorp Vault or AWS Secrets Manager.
- **Notification Flow**: Define who is notified when a rotation fails.

### 3. Act (Programming)
- **Secret Update**: Rotate keys via the provider API (e.g., Cloudflare API token regeneration).
- **Pipeline Injection**: Update GitHub Secrets using the GitHub CLI (`gh secret set`).
- **OIDC Implementation**: Replace long-lived keys with OIDC tokens (e.g., GitHub Actions -> Cloudflare) to eliminate secrets entirely.
- **Rotation Scripting**: Write Python/Node.js scripts to automate the rotation of DB passwords or third-party API keys.
- **Audit Logging**: Implement logging to track when secrets were last rotated.

### 4. Evaluate (Verification)
- **Deployment Test**: Trigger a pipeline run to ensure the new secrets are being picked up and authenticated.
- **Old Key Revocation**: After verifying the new key, revoke the old one and attempt to use it to ensure it is truly dead.
- **Rotation Timing Audit**: Verify that the rotation occurred within the planned window.
- **Recovery Drill**: Test the "emergency rotation" process for a suspected breach.
