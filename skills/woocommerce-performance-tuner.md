---
name: WooCommerce Performance Tuner
description: Optimizes WooCommerce stores for speed, focusing on database efficiency, asset loading, and server response time.
---

# WooCommerce Performance Tuner

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- **Baseline Measurement**: Run a full performance audit using PageSpeed Insights, GTmetrix, and Query Monitor.
- **Database Profiling**: Identify slow queries and bloated tables (e.g., `wp_options` with excessive autoloaded data).
- **Asset Audit**: Analyze the size and number of CSS/JS files being loaded, specifically looking for redundant plugin scripts.

### 2. Analysis (Plan)
- **Bottleneck Categorization**: Split issues into Server-side (PHP/DB), Network (TTFB), and Client-side (JS/CSS).
- **Caching Strategy**: Plan the implementation of object caching (Redis/Memcached) and page caching.
- **Asset Optimization**: Plan the removal of unused CSS/JS and the implementation of a critical CSS strategy.

### 3. Programming (Act)
- **DB Optimization**: Clean up expired transients and optimize the database using SQL queries to remove orphaned metadata.
- **Asset Orchestration**: Use a plugin or custom code to dequeue unnecessary scripts on non-ecommerce pages.
- **Infrastructure Tuning**: Configure Cloudflare's APO (Automatic Platform Optimization) or a similar edge caching solution.
- **PHP Optimization**: Update PHP versions and optimize `wp-config.php` settings (e.g., increasing memory limit).

### 4. Verification (Evaluate)
- **Comparison Audit**: Compare the "before" and "after" PageSpeed scores, focusing on LCP and TTFB.
- **Load Testing**: Use tools like k6 or Loader.io to ensure the store remains stable under high traffic.
- **UX Validation**: Verify that the performance optimizations have not broken any WooCommerce functionality (e.g., cart updates).
