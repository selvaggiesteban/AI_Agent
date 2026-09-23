---
name: Python Asyncio Performance Tuner
description: Optimizes asynchronous Python code to maximize concurrency, resolve event loop bottlenecks, and reduce latency.
---

# Python Asyncio Performance Tuner

This skill transforms sluggish `asyncio` applications into high-performance engines by eliminating blocking calls and optimizing task orchestration.

## Workflow

### 1. Perceive (Diagnosis)
- **Loop Lag Detection**: Use `asyncio` debug mode (`PYTHONASYNCIODEBUG=1`) to find "Executing <Task> took X seconds" warnings.
- **Blocking Call Search**: Scan for `time.sleep()`, `requests.*`, or heavy CPU-bound functions inside `async def`.
- **Task Volume Audit**: Check for "task explosions" (e.g., spawning 10,000 tasks without a semaphore).
- **Wait-state Analysis**: Identify where the program is spending most of its time (e.g., waiting for DB vs waiting for API).

### 2. Plan (Analysis)
- **Concurrency Control**: Plan the use of `asyncio.Semaphore` or `asyncio.Queue` to limit concurrent operations.
- **Offloading Strategy**: Determine which CPU-bound tasks should be moved to `run_in_executor` (ThreadPoolExecutor or ProcessPoolExecutor).
- **Batching Logic**: Design a way to batch multiple small I/O calls into a single request (e.g., using `asyncio.gather` or `asyncio.TaskGroup`).
- **Library Swap**: Identify non-async libraries and find their async counterparts (e.g., `requests` -> `httpx`).

### 3. Act (Programming)
- **Blocking Removal**: Replace all blocking calls with `await` equivalents.
- **Executor Implementation**: Wrap CPU-heavy functions in `loop.run_in_executor`.
- **Task Orchestration**: Implement `asyncio.TaskGroup` (Python 3.11+) for better error handling and structured concurrency.
- **Timeout Hardening**: Wrap all network calls in `asyncio.wait_for` to prevent hanging tasks.
- **Loop Optimization**: Switch to `uvloop` for a faster event loop implementation.

### 4. Evaluate (Verification)
- **Concurrency Measurement**: Compare the time taken to process N items sequentially vs. concurrently.
- **Lag Audit**: Run the application with debug mode enabled to ensure no task blocks the loop for more than 100ms.
- **Throughput Test**: Measure the increase in requests per second (RPS).
- **Stability Test**: Ensure that high concurrency doesn't lead to "Too Many Open Files" (ulimit) errors.
