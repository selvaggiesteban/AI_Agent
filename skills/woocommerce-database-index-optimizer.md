---
name: WooCommerce Database Index Optimizer
description: analyzes and optimizes the WordPress/WooCommerce database indexes to accelerate search and filter queries.
---

# WooCommerce Database Index Optimizer

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **Slow Query Identification**: Use the `slow_query_log` in MySQL or the Query Monitor plugin to find queries taking >100ms.
- **Index Audit**: Review existing indexes on `wp_posts`, `wp_postmeta`, and `wp_woocommerce_order_items` to find missing or redundant indexes.
- **Data Volume Analysis**: Analyze the size of the `wp_options` and `wp_postmeta` tables to identify potential bottlenecks.

### 2. Analysis (Plan)
- **Index Mapping**: Determine which columns are frequently used in `WHERE`, `JOIN`, and `ORDER BY` clauses but lack indexes.
- **Redundancy Check**: Identify duplicate indexes that slow down `INSERT` and `UPDATE` operations.
- **Maintenance Plan**: Design a schedule for database optimization (e.g., `OPTIMIZE TABLE`) to reclaim unused space.

### 3. Programming (Act)
- **Index Implementation**: Write and execute precise SQL statements to add missing indexes (e.g., adding an index to `meta_key` in `wp_postmeta`).
- **Cleanup**: Remove redundant or unused indexes to improve write performance.
- **Query Refactoring**: Rewrite inefficient WooCommerce queries to leverage the new indexes more effectively.
- **Automation**: Set up a cron job or a Cloudflare Worker to periodically monitor and report on slow queries.

### 4. Verification (Evaluate)
- **Query Timing Comparison**: Re-run the previously slow queries and compare the execution time.
- **Page Load Impact**: Measure the improvement in the loading speed of the shop and archive pages.
- **Stability Check**: Ensure that database changes haven't caused any locks or crashes during high-traffic periods.
