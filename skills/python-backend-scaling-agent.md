---
name: Python Backend Scaling Agent
description: Optimizes Python services for high throughput and low latency, focusing on concurrency and resource utilization.
---

# Python Backend Scaling Agent

This skill scales Python backends (FastAPI, Flask, Django) to handle increased load by optimizing the runtime, concurrency model, and integration layers.

## Workflow

### 1. Perceive (Diagnosis)
- **Bottleneck Identification**: Analyze CPU/Memory profiles using `py-spy`, `cProfile`, or Prometheus metrics.
- **Concurrency Audit**: Evaluate the current use of `sync` vs `async` endpoints.
- **Database Pressure**: Inspect slow query logs and connection pool exhaustion.
- **I/O Analysis**: Identify blocking calls in the event loop (e.g., `requests` in an `async def` function).

### 2. Plan (Analysis)
- **Concurrency Model Shift**: Determine if `asyncio` (FastAPI/Starlette) or multi-processing (Gunicorn/Uvicorn) is the primary lever.
- **Caching Layer Design**: Plan the implementation of Redis or Memcached for frequently accessed data.
- **Worker Configuration**: Calculate optimal worker counts based on CPU cores and I/O wait times.
- **Payload Optimization**: Plan for Pydantic model optimizations or moving to `msgpack` for internal service communication.

### 3. Act (Programming)
- **Async Refactoring**: Replace blocking I/O with `httpx`, `motor`, or `aiopg`.
- **Server Tuning**: Configure `uvicorn` with optimal `loop` (uvloop) and `http` (httptools) implementations.
- **Connection Pooling**: Implement robust connection pooling for PostgreSQL/MySQL using `SQLAlchemy` or `Tortoise-ORM`.
- **Load Balancing**: Configure Nginx or Cloudflare Load Balancers to distribute traffic across multiple Python instances.
- **Task Offloading**: Move heavy computations to background workers using `Celery` or `RQ`.

### 4. Evaluate (Verification)
- **Load Testing**: Run `Locust` or `k6` to measure requests per second (RPS) and P99 latency.
- **Resource Monitoring**: Verify that memory usage remains stable under load (no leaks).
- **Stability Test**: Perform soak tests to ensure the system doesn't degrade over time.
- **Latency Comparison**: Compare response times before and after the scaling interventions.
