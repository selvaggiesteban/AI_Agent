---
name: Cloudflare R2 Asset Optimizer
description: Implements high-performance asset storage and delivery pipelines using Cloudflare R2 and Workers.
---

# Cloudflare R2 Asset Optimizer

This skill optimizes the storage, upload, and delivery of large assets (images, videos, PDFs) using Cloudflare's S3-compatible R2 storage.

## Workflow

### 1. Diagnosis (Perceive)
- Identify where assets are currently stored (e.g., local `public/` folder, external S3, WordPress uploads).
- Analyze the size and type of assets causing performance issues.
- Audit the current upload process: is it manual or automated via API?
- Review the asset delivery path: are they served from a CDN or directly from storage?

### 2. Analysis (Plan)
- Design the R2 bucket structure for scalability (e.g., `/uploads/users/{id}/...`).
- Plan the "Signed URL" strategy for private assets to ensure security.
- Determine the need for an "Image Transformation" layer (e.g., using Cloudflare Images or a Worker-based resizer).
- Plan the migration path from old storage to R2 without breaking existing links.

### 3. Programming (Act)
- **R2 Integration**: Implement the R2 API using the `S3` client or Cloudflare's native `R2Bucket` binding in Workers.
- **Upload Pipeline**: Create a secure upload endpoint in a Pages Function that validates files before streaming them to R2.
- **Delivery Optimization**: Configure a Worker to serve assets from R2 with optimal `Cache-Control` headers.
- **Asset Versioning**: Implement a versioning or hashing system (e.g., `image.v1.jpg`) to avoid cache staleness.

### 4. Verification (Evaluate)
- Test upload and download speeds using `wrangler dev`.
- Verify that signed URLs expire correctly and prevent unauthorized access.
- Measure the reduction in origin bandwidth and increase in cache hit rate.
- Ensure that assets are served with the correct `Content-Type` and `Content-Disposition`.

## Tech Stack Alignment
- **Cloudflare R2**: Object storage.
- **Cloudflare Workers**: Asset delivery and transformation logic.
- **Wrangler**: Configuration and deployment.
- **TypeScript**: Type-safe R2 client implementation.
