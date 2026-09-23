---
name: aws-ecs-deploy-github-actions
description: Orchestrate the deployment of Amazon ECS containers using GitHub Actions and CloudFormation, integrating with the AI_Agent's Perceive-Plan-Act-Evaluate architecture.
---

# AWS ECS Deploy with GitHub Actions

This skill enables the `AgentOrchestrator` to automate the full CI/CD pipeline for Amazon ECS. It leverages CloudFormation for infrastructure as code and GitHub Actions for orchestration, ensuring a secure and scalable deployment process.

## Agentic Workflow (Perceive-Plan-Act-Evaluate)

The `AgentOrchestrator` executes this skill following the core AI_Agent architectural loop:

### 1. Perceive (Diagnosis)
The agent scans the current environment and repository state to identify:
- **Infrastructure State:** Current CloudFormation stack status and ECS cluster configuration.
- **Authentication:** Availability of AWS OIDC provider configuration for GitHub Actions.
- **Artifacts:** Presence of Dockerfiles and existing ECR repositories.
- **Requirements:** Target task definitions, service names, and deployment strategies (Rolling vs. Blue/Green).

### 2. Plan (Analysis)
Based on the perceived state, the agent constructs a deployment blueprint:
- **Auth Strategy:** Define the OIDC role assumptions to eliminate long-lived AWS keys.
- **Build Pipeline:** Sequence the Docker build, tag, and push operations to ECR.
- **Infra Update:** Determine the necessary CloudFormation template modifications for the ECS task and service.
- **Validation Gate:** Define the health check criteria for the new deployment.

### 3. Act (Programming/Execution)
The agent implements the plan through the following technical steps:
- **CI/CD Configuration:** Generate or update `.github/workflows/deploy.yml` using TypeScript/Node.js scripts to ensure type-safe configuration.
- **Infrastructure as Code:** Deploy/Update CloudFormation stacks using the AWS CLI or SDK.
- **Image Management:** Execute `docker build` and `docker push` to the Amazon Elastic Container Registry (ECR).
- **Service Update:** Update the ECS service to use the newly pushed image via a dynamic task definition update.

### 4. Evaluate (Report)
The agent verifies the success of the action:
- **Deployment Monitoring:** Track the ECS service rollout until the desired count of healthy tasks is reached.
- **Log Analysis:** Scan CloudWatch logs for application startup errors.
- **Health Verification:** Perform synthetic checks on the deployed endpoint.
- **Final Report:** Provide a detailed summary of the deployment version, stack status, and any encountered warnings.

## Tech Stack Integration

- **Primary Orchestration:** GitHub Actions (YAML) & CloudFormation (JSON/YAML).
- **Language Support:** 
    - **TypeScript/Node.js:** For pipeline configuration scripts and deployment triggers.
    - **Python:** For complex infrastructure analysis and post-deployment validation scripts.
- **Cloud Integration:** AWS ECS, ECR, IAM (OIDC).
- **Compatibility:** Works alongside the AI_Agent's Cloudflare-based frontend/functions stack for seamless full-stack orchestration.

## When to Use
- Setting up new ECS deployment pipelines via GitHub Actions.
- Migrating from static AWS keys to OIDC-based authentication.
- Managing dynamic task definition updates without manual AWS Console intervention.
- Implementing automated rolling or blue/green deployment strategies.
- Synchronizing infrastructure changes via CloudFormation through GitHub commits.
