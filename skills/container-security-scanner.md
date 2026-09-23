---
name: Container Security Scanner
description: Implements automated vulnerability scanning and hardening for Docker images and container runtimes.
---

# Container Security Scanner

This skill secures the container supply chain by detecting vulnerabilities in base images, scanning for secrets, and hardening the runtime environment.

## Workflow

### 1. Perceive (Diagnosis)
- **Image Inventory**: List all images used in production and their provenance.
- **Vulnerability Baseline**: Run an initial scan using `Trivy`, `Grype`, or `Snyk` to find CVEs.
- **Secret Leakage Check**: Scan image layers for hardcoded keys or passwords.
- **Runtime Audit**: Inspect the running container's capabilities (e.g., is it running as root?).

### 2. Plan (Analysis)
- **Risk Prioritization**: Categorize CVEs by severity (Critical/High/Medium) and reachability.
- **Remediation Path**: Determine if the fix is a base image update, a package upgrade, or a configuration change.
- **Scanning Integration**: Plan where the scan happens (e.g., locally, in GitHub Actions, or in the Registry).
- **Policy Definition**: Define "Breaking" criteria (e.g., "Fail the build if any Critical CVE is found").

### 3. Act (Programming)
- **Scan Automation**: Integrate `Trivy` into the CI/CD pipeline to block vulnerable images.
- **Base Image Hardening**: Switch to `distroless` or `alpine` to remove unnecessary binaries (like `curl` or `sh`).
- **Runtime Lockdown**: Implement `securityContext` in Kubernetes (e.g., `allowPrivilegeEscalation: false`, `runAsNonRoot: true`).
- **Secret Removal**: Use `.dockerignore` to prevent sensitive files from entering the image.
- **Patching**: Update `apt-get` / `apk` packages in the Dockerfile to resolve known CVEs.

### 4. Evaluate (Verification)
- **Clean Scan**: Re-run the scanner to verify that all Critical/High vulnerabilities are resolved.
- **Runtime Validation**: Verify the container cannot perform privileged actions (e.g., cannot modify the host filesystem).
- **Pipeline Check**: Confirm that a intentionally vulnerable image is correctly blocked by the CI/CD gate.
- **Size Audit**: Ensure that hardening didn't significantly increase the image size.
