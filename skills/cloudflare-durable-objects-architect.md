---
name: Cloudflare Durable Objects Architect
description: Designs stateful, globally consistent systems using Cloudflare Durable Objects for real-time collaboration and coordination.
---

# Cloudflare Durable Objects Architect

This skill enables the creation of "stateful" applications on the edge, allowing for consistent data synchronization and real-time coordination.

## Workflow

### 1. Diagnosis (Perceive)
- Identify requirements for "Strong Consistency" (e.g., a shared counter, a real-time chat room, a game state).
- Analyze the concurrency needs: how many users will access a single state object simultaneously?
- Evaluate the data volume: is the state small enough to fit in a DO's local storage?
- Check for existing "stateless" workarounds (e.g., polling a database) that cause latency.

### 2. Analysis (Plan)
- Design the "DO Topology": determine how to map users/entities to specific Durable Object IDs.
- Plan the communication flow: Client <-> Worker <-> Durable Object.
- Define the state schema and storage strategy using `this.storage.put()` and `get()`.
- Plan for WebSocket integration for real-time, bi-directional communication.

### 3. Programming (Act)
- **DO Implementation**: Write the Durable Object class in TypeScript, implementing the `fetch` handler.
- **State Persistence**: Implement robust read/write operations using the DO storage API.
- **WebSocket Orchestration**: Set up WebSocket connections within the DO to broadcast updates to all connected clients.
- **Worker Integration**: Implement the "Gateway" Worker that routes requests to the correct DO instance.

### 4. Verification (Evaluate)
- Test consistency by simulating concurrent writes from different global regions.
- Verify WebSocket stability and latency using `wrangler dev`.
- Audit the "Storage" usage and ensure the DO is not leaking memory or state.
- Measure the reduction in database load compared to the previous stateless approach.

## Tech Stack Alignment
- **Cloudflare Durable Objects**: Stateful edge compute.
- **Wrangler**: Deployment and local emulation.
- **TypeScript**: Type-safe state management.
- **WebSockets**: Real-time communication.
