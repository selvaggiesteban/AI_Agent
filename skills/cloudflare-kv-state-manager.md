---
name: Cloudflare KV State Manager
description: Implements efficient state management using Cloudflare KV for low-latency edge data storage and retrieval.
---

# Cloudflare KV State Manager

This skill optimizes the use of Cloudflare KV to store and manage state at the edge, providing near-instant access to data globally.

## Workflow

### 1. Diagnosis (Perceive)
- Identify data that is "read-heavy" and "write-infrequent" (the ideal use case for KV).
- Analyze current state management (e.g., centralized database) and identify latency bottlenecks.
- Audit the size and structure of the data to be stored in KV.
- Check for potential race conditions or consistency requirements (KV is eventually consistent).

### 2. Analysis (Plan)
- Design a KV key-naming convention (e.g., `user:{id}:profile`, `config:global:settings`) for fast lookups.
- Plan the data serialization format (JSON is standard, but binary/MsgPack may be needed for large sets).
- Determine the TTL (Time To Live) for different data types to automate cleanup.
- Plan the "Write" strategy: when to update KV from the origin vs. when to update at the edge.

### 3. Programming (Act)
- **KV Integration**: Implement `KVNamespace` access in Cloudflare Workers or Pages Functions.
- **Data Access Layer**: Create a TypeScript wrapper for KV operations (get, put, delete) with built-in Zod validation for retrieved values.
- **Caching Layer**: Implement a "Read-through" cache pattern: Check KV -> If miss, fetch from origin -> Store in KV.
- **Wrangler Config**: Configure `kv_namespaces` in `wrangler.toml` for different environments.

### 4. Verification (Evaluate)
- Test read/write latency using `wrangler dev` and Cloudflare's production logs.
- Verify eventual consistency by writing a value and reading it from different global regions.
- Audit the storage usage in the Cloudflare dashboard to ensure no "leaking" keys.
- Stress test the system to ensure it handles high-concurrency reads without failure.

## Tech Stack Alignment
- **Cloudflare KV**: Primary storage engine.
- **Wrangler**: Configuration and deployment.
- **TypeScript**: Type-safe KV wrappers.
- **Zod**: Validation of KV data.
