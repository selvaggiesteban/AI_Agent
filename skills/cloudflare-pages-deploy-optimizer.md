---
name: Cloudflare Pages Deploy Optimizer
description: Optimizes the Cloudflare Pages build pipeline for speed, efficiency, and minimal cold-start latency.
---

# Cloudflare Pages Deploy Optimizer

This skill optimizes the end-to-end deployment pipeline on Cloudflare Pages, focusing on reducing build times and maximizing edge performance.

## Workflow

### 1. Diagnosis (Perceive)
- Analyze Cloudflare Pages build logs to identify bottlenecks (e.g., long `npm install` times, slow Astro build steps).
- Review the `Build command` and `Build output directory` in the Cloudflare dashboard.
- Check the size of the final build artifacts and the number of assets being deployed.
- Audit the use of environment variables and secrets across different environments (Preview vs Production).

### 2. Analysis (Plan)
- Determine if `pnpm` or `bun` can replace `npm` for faster dependency installation.
- Identify static assets that can be optimized or moved to Cloudflare R2.
- Plan the implementation of build caching strategies.
- Analyze the Astro output format (Static vs Hybrid vs SSR) to optimize the deployment target.

### 3. Programming (Act)
- **Build Command Tuning**: Optimize the build script (e.g., `npm ci && npm run build`) and set the correct Node.js version via `.node-version`.
- **Astro Optimization**: Configure `astro.config.mjs` for the `cloudflare` adapter, optimizing the `output` mode.
- **Asset Pipeline**: Implement image optimization using Astro's built-in `<Image />` component and Cloudflare Images.
- **CI/CD Integration**: Configure GitHub Actions or GitLab CI to trigger builds only on relevant file changes.

### 4. Verification (Evaluate)
- Compare build durations before and after optimizations using the Pages dashboard.
- Verify that the production site loads correctly and all environment variables are active.
- Test the "Preview" deployment flow to ensure fast iteration for developers.
- Run Lighthouse audits to ensure the optimized build didn't regress performance.

## Tech Stack Alignment
- **Cloudflare Pages**: Deployment platform and build settings.
- **Astro**: Build tool and adapter configuration.
- **Wrangler**: Local testing of Pages functions.
- **Node.js**: Runtime environment for build scripts.
