---
name: edge_computing_patterns
description: Deploy high-performance code near global users using Cloudflare Workers and V8 Isolates to minimize latency and optimize request handling.
---

# Edge Computing Patterns

This skill enables the agent to architect and deploy logic at the network edge, specifically targeting Cloudflare Workers and V8 Isolates. The objective is to move compute as close to the end-user as possible to achieve sub-50ms latency and reduce origin load.

## Agentic Workflow (Perceive-Plan-Act-Evaluate)

The `AgentOrchestrator` should execute this skill using the following architectural cycle:

1.  **Perceive**: Analyze the current request flow, identify latency bottlenecks, and detect opportunities for edge offloading (e.g., geo-routing needs, auth overhead, or static content delivery).
2.  **Plan**: Map the specific use case to an edge pattern (e.g., Edge Auth, HTML Rewriting, or A/B Testing) and design the Cloudflare Worker logic.
3.  **Act**: Implement the TypeScript/Node.js code, configure `wrangler.toml`, and deploy to Cloudflare Pages/Functions.
4.  **Evaluate**: Measure Time to First Byte (TTFB), verify cache hit ratios in Cloudflare Analytics, and ensure fail-safe fallback to the origin.

## Execution Phases

### Phase 1: Diagnosis (Perceive)
- **Latency Audit**: Use GSC and GA4 data to identify regions with high latency.
- **Bottleneck Identification**: Determine if the delay is caused by origin compute, database distance, or heavy payload processing.
- **Constraint Mapping**: Verify if the required logic fits within V8 Isolate limits (CPU time and memory).

### Phase 2: Analysis & Design (Plan)
- **Pattern Selection**:
    - **Edge Auth**: Move JWT verification or session validation to the edge.
    - **Geo-Routing**: Use `request.cf.country` for localization or routing to the nearest regional bucket.
    - **Dynamic Optimization**: Plan HTML rewriting using `HTMLRewriter` for A/B testing or SEO injections.
    - **Security Layer**: Implement rate limiting and DDoS mitigation via Cloudflare Workers.
- **Tech Stack Alignment**: Ensure integration with Astro (for edge-rendered pages) and Cloudflare Turnstile (for edge-level bot protection).

### Phase 3: Programming & Deployment (Act)
- **Implementation**:
    - Write the Worker in TypeScript.
    - Integrate with Cloudflare KV or Durable Objects for stateful edge data.
    - Configure Resend for edge-triggered transactional emails.
- **Deployment**:
    - Use `wrangler` for deployment to Cloudflare Pages/Functions.
    - Set up environment variables and secrets for API keys.

### Phase 4: Validation & Reporting (Evaluate)
- **Performance Verification**: Compare origin vs. edge response times.
- **Edge-Case Testing**: Validate behavior during origin downtime (stale-while-revalidate patterns).
- **Final Report**: Document the latency reduction and the specific edge patterns implemented.

## Technical Stack Reference
- **Primary**: Astro (SSR/Edge), Tailwind CSS, Cloudflare Pages, Cloudflare Functions, Resend, Cloudflare Turnstile.
- **Secondary**: TypeScript, Node.js, Cloudflare KV, Durable Objects.
