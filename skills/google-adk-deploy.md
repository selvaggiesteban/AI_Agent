---
name: adk-deployment-skill
description: Specialized skill for deploying ADK-based agentic services to GCP, Cloud Run, and GKE using Terraform and Docker.
---

# ADK Deployment Skill

This skill enables the `AgentOrchestrator` to execute a standardized deployment pipeline for ADK services. It follows the agentic architecture of **Perceive -> Plan -> Act -> Evaluate** to ensure infrastructure is provisioned correctly and services are healthy.

## Tech Stack Alignment
- **Infrastructure:** GCP (Cloud Run, GKE Autopilot), Terraform.
- **Containerization:** Docker.
- **Orchestration:** AgentOrchestrator (`core/ai_agent.py`).
- **Integration:** Cloudflare Pages/Functions (for frontend/edge hooks), Resend (for deployment notifications).

---

## Execution Phases

### Phase 1: Diagnosis (Perceive)
The agent must first perceive the current environment and deployment state.
- **Environment Audit:** Detect if the project is "Scaffolded" (contains `Makefile`, `.terraform` directory) or "No Scaffold".
- **Reference Analysis:** Read the following files in `references/` to determine the target architecture:
    - `cloud-run.md`: For serverless scaling and networking.
    - `gke.md`: For Kubernetes-managed resources and Workload Identity.
    - `terraform-patterns.md`: For IAM and state management.
    - `event-driven.md`: For Pub/Sub and Eventarc triggers.
- **Constraint Check:** Verify GCP project IDs and service account permissions are present in environment variables.

### Phase 2: Analysis (Plan)
Based on the diagnosis, the agent creates a deployment plan.
- **Path Selection:**
    - If **Scaffolded**: Plan to use `make` command wrappers for Terraform and Docker.
    - If **No Scaffold**: Plan a "Quick Deploy" via ADK CLI or `/adk-scaffold` for production.
- **Dependency Mapping:** Identify if the deployment requires specific Cloudflare Turnstile integration or Resend API keys for notification hooks.
- **Resource Estimation:** Determine required session types and networking rules as specified in `cloud-run.md` or `gke.md`.

### Phase 3: Programming & Deployment (Act)
The agent executes the plan using the provided toolset.
- **Infrastructure Provisioning:**
    - Execute `terraform init` and `terraform apply` (via `make` if scaffolded).
    - Configure IAM roles and Workload Identity for GKE.
- **Container Deployment:**
    - Build and push Docker images to Artifact Registry.
    - Deploy to Cloud Run or GKE Autopilot.
- **Edge Configuration:**
    - Setup Cloudflare Pages/Functions to route traffic to the newly deployed GCP endpoints.
- **Notification:** Trigger a Resend email to notify the team of the deployment status.

### Phase 4: Verification (Evaluate)
The agent evaluates the success of the "Act" phase.
- **Health Check:** Probe the deployed service endpoints for `200 OK` responses.
- **Log Analysis:** Scan Cloud Logging for crash loops or permission errors (e.g., IAM 403s).
- **Observability Integration:** Confirm that the **adk-observability-guide** hooks (Cloud Trace, BigQuery Analytics) are capturing data.
- **Rollback Trigger:** If evaluation fails, the agent must automatically trigger `terraform destroy` or revert to the previous stable image tag.
