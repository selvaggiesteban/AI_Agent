---
name: Python Memory Leak Hunter
description: Diagnoses and resolves memory leaks in long-running Python processes using heap analysis and profiling.
---

# Python Memory Leak Hunter

This skill identifies the root cause of memory growth in Python applications, distinguishing between actual leaks (unreferenced objects) and logical leaks (growing collections).

## Workflow

### 1. Perceive (Diagnosis)
- **Growth Pattern Analysis**: Monitor RSS/VMS memory usage over time using `psutil` or Grafana.
- **Trigger Identification**: Correlate memory spikes with specific API endpoints or background tasks.
- **Baseline Establishment**: Determine the "steady state" memory usage after initial startup.
- **Garbage Collection Audit**: Inspect `gc.get_stats()` to see if the GC is struggling with circular references.

### 2. Plan (Analysis)
- **Profiling Strategy**: Decide between sampling (low overhead) or deterministic profiling (high overhead).
- **Tool Selection**: Choose between `tracemalloc` (standard lib), `objgraph` (visualization), or `memray` (deep analysis).
- **Snapshot Planning**: Define the points where memory snapshots should be taken (e.g., before and after a request).
- **Hypothesis Generation**: Identify suspect areas (e.g., global lists, cached objects, unclosed file handles).

### 3. Act (Programming)
- **Tracemalloc Integration**: Implement `tracemalloc.start()` and compare snapshots using `snapshot.compare_to`.
- **Object Graphing**: Use `objgraph.show_most_common_types()` and `objgraph.show_backrefs()` to find what is holding onto objects.
- **Resource Cleanup**: Implement `with` statements (Context Managers) for all I/O and database connections.
- **Cache Eviction**: Replace unbounded caches with `functools.lru_cache` or a Redis-based TTL cache.
- **Explicit Deletion**: Use `del` and `gc.collect()` in critical paths if circular references are unavoidable.

### 4. Evaluate (Verification)
- **Long-run Validation**: Run the service under load for several hours to ensure a flat memory line.
- **Leak Regression Test**: Create a test case that specifically exercises the previously leaking path.
- **Resource Profiling**: Verify that memory usage returns to baseline after the "leaky" operation completes.
- **Performance Audit**: Ensure that the fixes (like adding LRU caches) didn't introduce significant latency.
