---
name: Edge Middleware Architect
description: Designs and implements high-performance middleware on Cloudflare Workers for request routing, authentication, and A/B testing.
---

# Edge Middleware Architect

This skill focuses on shifting logic from the origin to the edge using Cloudflare Workers/Pages Functions, reducing latency and server load.

## Workflow

### 1. Diagnosis (Perceive)
- Identify "heavy" origin tasks that can be handled at the edge (e.g., redirects, geolocation-based content, authentication checks).
- Analyze current request flow and latency using Cloudflare Analytics.
- Review existing authentication mechanisms (e.g., JWTs, Cookies).
- Audit the current routing logic in Astro or other framework.

### 2. Analysis (Plan)
- Design a middleware pipeline: Request -> Edge Auth -> Geolocation -> Routing/Rewriting -> Origin.
- Determine the optimal storage for middleware state (e.g., Cloudflare KV for session data, Durable Objects for real-time state).
- Map specific routes to middleware logic to avoid unnecessary execution on static assets.
- Plan for fail-safe mechanisms (e.g., fallback to origin if edge logic fails).

### 3. Programming (Act)
- **Middleware Implementation**: Write the middleware logic in TypeScript using the Cloudflare Workers API.
- **Request Manipulation**: Implement `request.rewrite()` or `request.redirect()` for SEO-friendly URL management.
- **Auth Integration**: Integrate JWT verification at the edge to block unauthorized requests before they reach the origin.
- **Dynamic Routing**: Implement A/B testing logic using `crypto.getRandomValues()` and cookie-based persistence.

### 4. Verification (Evaluate)
- Test middleware locally using `wrangler dev`.
- Verify that requests are being intercepted and modified correctly using browser DevTools.
- Measure the reduction in origin server load and response time (TTFB).
- Ensure that static assets are still served efficiently without unnecessary middleware overhead.

## Tech Stack Alignment
- **Cloudflare Workers/Pages Functions**: Runtime for edge logic.
- **Wrangler**: Development and deployment tool.
- **TypeScript**: Type-safe middleware implementation.
- **Cloudflare KV**: Fast edge state storage.
