---
name: DevOps Practices Skill
description: Apply modern DevOps practices for deployment automation and infrastructure management tailored for the AI_Agent tech stack.
---

# DevOps Practices Skill

## Overview
Apply modern DevOps practices for deployment automation, container orchestration, and infrastructure management. This skill focuses on ensuring high availability and seamless delivery for applications built with Astro, Tailwind CSS, and Cloudflare Pages/Functions, while integrating with supporting services like Resend and Cloudflare Turnstile.

## Agentic Workflow (Perceive-Plan-Act-Evaluate)

### Phase 1: Diagnosis (Perceive)
**Objective:** Assess the current infrastructure state and deployment bottlenecks.
- **Perceive:** Analyze existing CI/CD pipelines (GitHub Actions), Cloudflare Pages project settings, and environment variable configurations.
- **Audit:** Identify gaps in the deployment flow, specifically looking for manual steps in the Astro build process or improperly configured Cloudflare Functions.
- **Mapping:** Map the flow of data from the frontend (Astro) through the edge (Cloudflare Functions) to external services (Resend, Turnstile).

### Phase 2: Analysis (Plan)
**Objective:** Design a streamlined, automated deployment strategy.
- **Plan:** Define the optimal pipeline for Astro deployment to Cloudflare Pages.
- **IaC Strategy:** Determine where Cloudflare Wrangler or Terraform/Pulumi is needed to manage infrastructure as code.
- **Security Planning:** Plan the integration of Cloudflare Turnstile to protect endpoints and the configuration of secret management for Resend API keys.
- **Optimization:** Design a build cache strategy to minimize Astro build times in the CI environment.

### Phase 3: Programming & Implementation (Act)
**Objective:** Execute the DevOps automation.
- **CI/CD Automation:** Implement GitHub Actions workflows that trigger on push/PR to automate:
    - TypeScript type checking and linting.
    - Astro build execution.
    - Deployment to Cloudflare Pages preview/production environments.
- **Infrastructure as Code:** Use `wrangler.toml` to define environment variables, KV namespaces, and D1 database bindings.
- **Containerization (Optional/Secondary):** For Node.js or Python backend services, build optimized multi-stage Docker images that minimize size and maximize cache efficiency.
- **Integration:** Configure Resend via Cloudflare Functions for transactional email automation.

### Phase 4: Validation & Reporting (Evaluate)
**Objective:** Verify deployment stability and performance.
- **Evaluate:** Run smoke tests against the Cloudflare Pages URL to ensure Astro components and Cloudflare Functions are responding correctly.
- **Performance Audit:** Use GSC and GA4 to monitor the impact of deployment changes on Core Web Vitals and user traffic.
- **Security Validation:** Verify that Cloudflare Turnstile is effectively blocking bot traffic on critical forms.
- **Report:** Provide a summary of the deployment pipeline efficiency, build times, and infrastructure health.
