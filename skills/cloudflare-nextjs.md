---
name: cloudflare-nextjs-deployment
description: Deploy Next.js applications to Cloudflare Workers using the OpenNext Cloudflare adapter, optimizing for App Router, D1, R2, and KV.
---

# Cloudflare Next.js Deployment Skill

This skill enables the AI Agent to migrate or deploy Next.js applications (App or Pages Router) to the Cloudflare global edge network. It leverages the `@opennextjs/cloudflare` adapter to ensure compatibility with Cloudflare Workers, enabling SSR, SSG, and ISR.

## Agentic Workflow (Perceive-Plan-Act-Evaluate)

### Phase 1: Diagnosis (Perceive)
**Goal:** Audit the existing Next.js project and Cloudflare environment to identify compatibility gaps.

- **Project Audit:** Identify Next.js version, router type (App vs. Pages), and usage of Vercel-specific features.
- **Dependency Check:** Verify the presence of `@opennextjs/cloudflare` and `wrangler`.
- **Resource Mapping:** Identify required Cloudflare bindings (D1 databases, R2 buckets, KV namespaces).
- **Environment Analysis:** Check for existing Cloudflare Pages/Functions configurations.

### Phase 2: Strategy (Plan)
**Goal:** Create a technical blueprint for the deployment.

- **Adapter Configuration:** Plan the OpenNext build pipeline to transform Next.js output into Worker-compatible assets.
- **Binding Definition:** Map application data requirements to `wrangler.toml` (e.g., mapping a database call to a D1 binding).
- **Routing Strategy:** Define edge middleware requirements and static asset distribution.
- **Deployment Pipeline:** Determine the optimal path: Cloudflare Pages (integrated Git) or Wrangler CLI (CI/CD).

### Phase 3: Implementation (Act)
**Goal:** Execute the technical migration and deployment.

- **Tooling Setup:**
  - Install and configure `@opennextjs/cloudflare`.
  - Initialize `wrangler.toml` with correct project name and compatibility dates.
- **Infrastructure Provisioning:**
  - Create D1 databases via `wrangler d1 create`.
  - Initialize R2 buckets and KV namespaces.
  - Configure Cloudflare Turnstile for bot protection if required.
- **Build & Deploy:**
  - Execute the OpenNext build process.
  - Deploy to Cloudflare Workers/Pages using `wrangler deploy`.
- **Integration:** Connect Resend for transactional emails and GA4/GSC for analytics and indexing.

### Phase 4: Verification (Evaluate)
**Goal:** Validate the deployment against performance and functional benchmarks.

- **Edge Validation:** Verify that SSR and ISR are functioning correctly at the edge.
- **Binding Test:** Confirm that the application can read/write to D1, R2, and KV without latency spikes.
- **Performance Audit:** Use Web Vitals to ensure the global distribution is reducing TTFB.
- **Security Check:** Validate that Cloudflare Turnstile is effectively filtering malicious traffic.

## Tech Stack Alignment

- **Primary:** Astro (for static parts), Tailwind CSS (styling), Cloudflare Pages/Functions (hosting), Resend (email), Cloudflare Turnstile (security).
- **Secondary:** TypeScript (type safety), Node.js (build toolchain), D1 (SQL), R2 (Object Storage), KV (Key-Value store).

## Use This Skill When
- Migrating Next.js apps from Vercel, AWS, or other platforms to Cloudflare.
- Implementing React Server Components or Server Actions on the edge.
- Integrating Next.js with the Cloudflare ecosystem (D1, R2, KV, Workers AI).
- Seeking global edge deployment to minimize latency.
