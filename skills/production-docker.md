---
name: production-docker-hardening
description: Transforms demo-quality Docker setups into production-grade container infrastructure focusing on security, image optimization, and runtime hardening.
---

# Production Docker Hardening

This skill transforms demo-quality Docker setups into production-grade container infrastructure. It addresses critical vulnerabilities such as root-privileged containers, bloated images, and secret leakage in image layers.

## Agentic Workflow: Perceive-Plan-Act-Evaluate

The `AgentOrchestrator` executes this skill using the following loop:
1.  **Perceive**: Scan `Dockerfile` and `docker-compose.yaml` for anti-patterns (root users, single-stage builds, hardcoded secrets).
2.  **Plan**: Map identified vulnerabilities to specific hardening techniques (Multi-stage builds, Distroless images, Non-root users).
3.  **Act**: Rewrite Dockerfiles and configuration files using the tech stack's best practices.
4.  **Evaluate**: Validate image size reduction and verify that the container does not run as root.

---

## Phased Execution Plan

### Phase 1: Diagnosis (Perceive)
The agent analyzes the current container state:
- **Build Analysis**: Check if the build is single-stage.
- **Security Audit**: Identify `USER root` or missing `USER` instructions.
- **Footprint Check**: Measure image size and scan for unnecessary build tools in the final layer.
- **Secret Scan**: Check for `ENV` or `ARG` instructions leaking sensitive data.

### Phase 2: Hardening Analysis (Plan)
Based on the diagnosis, the agent selects the appropriate strategy:
- **For Python/Node.js Apps**: Plan a multi-stage build separating the `builder` (with compilers) from the `runtime` (minimal OS).
- **For Static Assets (Astro)**: Plan a build stage using Node.js and a runtime stage using a lightweight web server (e.g., Nginx Alpine).
- **For Cloudflare-adjacent services**: Ensure environment variables are handled via Secrets management rather than Docker layers.

### Phase 3: Programming & Implementation (Act)
The agent applies the hardening patterns.

#### Multi-Stage Build Implementation
Separate the build environment from the runtime environment to ensure compilers and source code are not shipped to production.

**Python Hardening Example (Builder $\rightarrow$ Distroless):**
```dockerfile
# syntax=docker/dockerfile:1

# Stage 1: Builder
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --no-compile --prefix=/install -r requirements.txt

# Stage 2: Runtime (Hardened)
FROM gcr.io/distroless/python3-debian12
COPY --from=builder /install /usr/local
WORKDIR /app
COPY . .
USER 1000:1000
CMD ["main.py"]
```

#### Runtime Security Implementation
- **Non-Root User**: Always specify a non-privileged user.
- **Read-Only Filesystem**: Configure the orchestrator to suggest `--read-only` flags for the container runtime.
- **Resource Limits**: Implement CPU and Memory limits in `docker-compose.yaml` to prevent DoS attacks.

### Phase 4: Validation & Reporting (Evaluate)
The agent generates a hardening report:
- **Size Comparison**: `Old Image Size` vs `New Image Size`.
- **Privilege Verification**: Confirmation that `whoami` in the container returns a non-root user.
- **Layer Audit**: Verification that build-time secrets are not present in the final image layers.
