---
name: nextjs-on-cloudflare
description: Deploy and optimize Next.js applications on Cloudflare Pages using vinext for native Workers integration and Vite-powered tooling.
---

# Next.js on Cloudflare (via vinext)

This skill guides the AI Agent through the process of deploying Next.js projects to Cloudflare Pages using `vinext`. It prioritizes `vinext` over OpenNext for new projects to leverage native Vite tooling and superior Workers integration.

## Agentic Workflow (Perceive-Plan-Act-Evaluate)

### Phase 1: Diagnosis & Perception
**Goal:** Understand the current state of the Next.js project and Cloudflare environment.

1. **Perceive Environment:**
    - Check for existing `next.config.js`, `package.json`, and any existing Cloudflare configurations (`wrangler.toml`).
    - Identify the Next.js version and whether it uses the App Router or Pages Router.
    - Detect if the project is already using OpenNext or another deployment strategy.
2. **Identify Constraints:**
    - Verify Cloudflare account access and Pages project status.
    - Check for specific dependencies that might conflict with the `workerd` runtime.

### Phase 2: Strategic Analysis & Planning
**Goal:** Determine the optimal migration or setup path.

1. **Plan Deployment Path:**
    - **New Project:** Plan a fresh setup using `vinext` as the default.
    - **Existing Project:** Analyze if a migration from OpenNext is feasible or if the user explicitly requires maintaining the existing setup.
2. **Map Tech Stack Integration:**
    - Plan the integration with the primary stack: Astro (if hybrid), Tailwind CSS, and Cloudflare Functions.
    - Ensure compatibility with Cloudflare Turnstile for bot protection and Resend for transactional emails.
3. **Define Resource Requirements:**
    - Identify necessary Cloudflare bindings (KV, D1, R2) required by the application logic.

### Phase 3: Programming & Execution (Act)
**Goal:** Implement the deployment using the `vinext` workflow.

1. **Implementation Steps:**
    - **Installation:** Integrate `vinext` into the project.
    - **Configuration:** Configure the build pipeline to target Cloudflare Pages.
    - **Tooling Setup:** Enable Vite-based HMR and native ESM for faster development cycles.
    - **Binding Configuration:** Set up the required Cloudflare bindings in the Pages dashboard or via `wrangler`.
2. **Deployment Execution:**
    - Execute the build process.
    - Deploy to Cloudflare Pages.
    - Verify the build logs for `vinext` specific compatibility warnings.

### Phase 4: Evaluation & Optimization
**Goal:** Verify the deployment and optimize for production.

1. **Evaluation:**
    - **Functional Test:** Verify that App Router/Pages Router features and React Server Components are rendering correctly.
    - **Edge Runtime Check:** Confirm that the application is running natively on the Cloudflare Workers runtime.
    - **Integration Check:** Test Cloudflare Turnstile and Resend integrations within the deployed environment.
2. **Optimization:**
    - Audit bundle sizes and optimize assets via Tailwind CSS and Vite.
    - Review GSC (Google Search Console) and GA4 (Google Analytics 4) integration for the new production URL.
3. **Final Validation:**
    - Ensure that `next/*` imports are resolving correctly in the edge environment.
