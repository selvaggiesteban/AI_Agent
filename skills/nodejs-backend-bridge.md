---
name: Nodejs Backend Bridge
description: Designs and implements secure, efficient bridges between Astro/Cloudflare edge and Node.js backend services.
---

# Nodejs Backend Bridge

This skill focuses on the architecture and implementation of the communication layer between a modern frontend (Astro/Pages) and a traditional Node.js backend.

## Workflow

### 1. Diagnosis (Perceive)
- Audit existing API endpoints and their authentication methods (e.g., API Keys, OAuth2).
- Identify bottlenecks in the request/response cycle (e.g., oversized JSON payloads, slow database queries).
- Review the network topology: is the backend on a private VPC, a public VPS, or a serverless platform?
- Check for CORS issues and timeout settings.

### 2. Analysis (Plan)
- Design the "API Gateway" pattern: use a Cloudflare Worker as a proxy to handle auth, rate limiting, and caching before hitting the Node.js server.
- Plan the data contract using TypeScript interfaces shared between the frontend and backend.
- Determine the optimal communication protocol: REST for standard CRUD, WebSockets for real-time, or gRPC for internal services.
- Plan for error handling and graceful degradation (e.g., returning cached data if the backend is down).

### 3. Programming (Act)
- **Proxy Implementation**: Build a Cloudflare Worker that forwards requests to the Node.js backend, adding required headers and security tokens.
- **Type-Safe Client**: Create a TypeScript API client on the Astro side that mirrors the Node.js controller types.
- **Security Hardening**: Implement request validation on the Node.js side using `zod` to prevent injection and malformed data.
- **Payload Optimization**: Implement Gzip/Brotli compression and JSON stream processing for large data sets.

### 4. Verification (Evaluate)
- Test the end-to-end request flow using `curl` and Postman.
- Measure the latency added by the bridge/proxy and optimize headers.
- Verify that authentication is strictly enforced at both the proxy and the backend.
- Simulate backend failure to ensure the frontend handles errors gracefully without crashing.

## Tech Stack Alignment
- **Node.js**: Backend runtime.
- **Cloudflare Workers**: API Gateway / Proxy.
- **Astro**: Frontend consumer.
- **TypeScript**: Shared type definitions.
- **Zod**: Request/Response validation.
