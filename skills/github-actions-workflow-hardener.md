---
name: GitHub Actions Workflow Hardener
description: Secures and optimizes CI/CD pipelines to prevent secret leakage, reduce execution time, and ensure deployment integrity.
---

# GitHub Actions Workflow Hardener

This skill transforms fragile CI/CD YAMLs into production-grade pipelines with strict security boundaries and high efficiency.

## Workflow

### 1. Perceive (Diagnosis)
- **Static Analysis**: Scan `.github/workflows/*.yml` for insecure patterns (e.g., `run: echo $SECRET`, `uses: untrusted-action@master`).
- **Permission Audit**: Check for over-privileged `GITHUB_TOKEN` settings (e.g., `permissions: write-all`).
- **Performance Profiling**: Analyze workflow run durations to identify bottlenecks (e.g., redundant `npm install` steps).
- **Dependency Check**: Identify outdated or unpinned actions.

### 2. Plan (Analysis)
- **Least Privilege Mapping**: Define the minimum required permissions for each job.
- **Caching Strategy**: Design a caching layer for `node_modules`, Python `pip` caches, and Astro build artifacts.
- **Security Boundary Definition**: Plan the use of GitHub Environments and required reviewers for production deploys.
- **Concurrency Control**: Define `concurrency` groups to prevent race conditions during deployments.

### 3. Act (Programming)
- **Permission Lockdown**: Implement `permissions: { contents: read, pull-requests: write }` at the job level.
- **Action Pinning**: Replace `@master` or `@v1` with specific commit SHAs for immutable builds.
- **Cache Implementation**: Add `actions/cache` or use native caching in `setup-node` / `setup-python`.
- **Secret Masking**: Implement strict secret handling and use OIDC (OpenID Connect) for Cloudflare/AWS instead of long-lived keys.
- **Workflow Optimization**: Use `matrix` strategies for parallel testing and `if` conditionals to skip redundant steps.

### 4. Evaluate (Verification)
- **Dry Run**: Execute workflows on a feature branch to verify logic.
- **Security Scan**: Run `action-validator` or similar tools to ensure no regressions in security.
- **Timing Audit**: Compare "Before" and "After" execution times to quantify optimization gains.
- **Log Inspection**: Verify that secrets are properly masked in the GitHub Actions logs.
