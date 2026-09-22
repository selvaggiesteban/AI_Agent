---
name: cloudflare-workers-frameworks
description: Expert guide for deploying full-stack applications on Cloudflare Workers using Hono, Astro, Remix, and SvelteKit.
---

# Workers Frameworks Integration

This skill enables the AI Agent to architect, deploy, and optimize full-stack applications on the Cloudflare edge. It leverages the **Perceive-Plan-Act-Evaluate** architecture to ensure the chosen framework aligns with the project's performance and scalability requirements.

## Agentic Workflow

### Phase 1: Diagnosis (Perceive)
**Goal:** Understand the application requirements and current environment.
- **Perceive:** Analyze the project requirements (e.g., content-heavy vs. highly dynamic), existing tech stack (Astro, Tailwind), and target audience.
- **Identify:** Determine if the application requires Server-Side Rendering (SSR), Static Site Generation (SSG), or a pure API layer.
- **Evaluate:** Check for existing Cloudflare resources (Pages, Workers, KV, D1, R2).

### Phase 2: Analysis & Strategy (Plan)
**Goal:** Select the optimal framework and design the integration path.
- **Framework Selection:**
    - **Hono:** For lightweight APIs, middleware-heavy apps, or pure Worker-native performance.
    - **Astro:** For content-driven sites requiring exceptional SEO and minimal client-side JS (Primary stack).
    - **Remix:** For complex, data-intensive full-stack applications with deep nested routing.
    - **SvelteKit:** For highly interactive UIs with a seamless developer experience.
- **Architecture Mapping:** Plan the data flow between the framework and Cloudflare services (e.g., Resend for emails, Turnstile for bot protection).
- **Infrastructure Plan:** Define the deployment target (Cloudflare Pages vs. Workers).

### Phase 3: Implementation (Act)
**Goal:** Execute the programming and deployment.
- **Programming:**
    - Initialize the framework using the appropriate Cloudflare adapter.
    - Implement routing and business logic using TypeScript.
    - Integrate **Tailwind CSS** for styling.
    - Configure **Cloudflare Turnstile** for secure forms.
    - Set up **Resend** for transactional emails via Cloudflare Functions.
- **Deployment:** 
    - Configure `wrangler.toml` or Cloudflare Pages dashboard.
    - Set up environment variables and secrets.
    - Execute deployment to Cloudflare Pages/Functions.

### Phase 4: Validation & Optimization (Evaluate)
**Goal:** Verify performance and security.
- **Evaluate:** Run smoke tests on the deployed edge functions.
- **Performance Check:** Analyze TTFB (Time to First Byte) and Core Web Vitals.
- **Security Audit:** Verify Turnstile integration and secret management.
- **Refine:** Optimize bundle sizes and edge caching strategies.

## Tech Stack Reference

| Component | Tool/Technology | Role |
| :--- | :--- | :--- |
| **Primary Frameworks** | Astro, Hono, Remix, SvelteKit | Application Logic & Routing |
| **Styling** | Tailwind CSS | UI/UX Implementation |
| **Hosting** | Cloudflare Pages / Functions | Edge Execution |
| **Security** | Cloudflare Turnstile | Bot Mitigation |
| **Communication** | Resend | Email Delivery |
| **Languages** | TypeScript, Node.js, Python | Core Development |
| **Integrations** | WordPress, Shopify, GA4, GSC | Ecosystem Connectivity |

## Execution Guide for AgentOrchestrator

When calling this skill in `core/ai_agent.py`, the orchestrator should:
1. **Initialize** the `Perceive` loop to gather the "Framework Decision Tree" variables.
2. **Validate** the plan against the Primary Tech Stack (Astro/Tailwind/Cloudflare) before proceeding to `Act`.
3. **Monitor** the `Evaluate` phase to ensure the edge deployment meets latency benchmarks.
