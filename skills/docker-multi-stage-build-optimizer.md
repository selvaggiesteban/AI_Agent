---
name: Docker Multi-Stage Build Optimizer
description: Reduces container image size and attack surface through advanced multi-stage build patterns.
---

# Docker Multi-Stage Build Optimizer

This skill minimizes the footprint of Docker images by separating build-time dependencies from runtime artifacts, resulting in faster pulls and tighter security.

## Workflow

### 1. Perceive (Diagnosis)
- **Image Analysis**: Use `docker images` and `dive` to inspect layer sizes and wasted space.
- **Build Log Review**: Identify slow steps and redundant package installations.
- **Dependency Audit**: Distinguish between `devDependencies` (build-time) and `dependencies` (runtime).
- **Base Image Audit**: Check if the current base image is bloated (e.g., using `ubuntu` where `alpine` or `distroless` would work).

### 2. Plan (Analysis)
- **Stage Decomposition**: Define the "Build", "Test", and "Runtime" stages.
- **Artifact Identification**: Determine the exact files needed in the final image (e.g., just the `dist/` folder and `node_modules`).
- **Base Image Selection**: Choose the smallest viable runtime image (e.g., `node:alpine` or `gcr.io/distroless/nodejs`).
- **Layer Ordering**: Plan the `COPY` commands to maximize layer caching.

### 3. Act (Programming)
- **Dockerfile Refactoring**: Implement the `FROM ... AS build` pattern.
- **Build-time Optimization**: Use `--mount=type=cache` for `npm` or `pip` to speed up subsequent builds.
- **Minimal Copying**: Use `COPY --from=build /app/dist /app/dist` to transfer only the final bundle.
- **User Hardening**: Implement `USER node` or a custom non-root user in the final stage.
- **Package Pruning**: Run `npm prune --production` before the final copy to remove dev-dependencies.

### 4. Evaluate (Verification)
- **Size Comparison**: Compare the image size of the old vs. new Dockerfile.
- **Vulnerability Scan**: Use `trivy` or `docker scan` to verify the reduced attack surface.
- **Runtime Validation**: Ensure the minimal image contains all necessary runtime binaries and libraries.
- **Build Speed Audit**: Measure the time to rebuild after a small code change to verify cache effectiveness.
