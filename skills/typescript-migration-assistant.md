---
name: TypeScript Migration Assistant
description: Guides the incremental migration of JavaScript projects to TypeScript, focusing on risk mitigation and type accuracy.
---

# TypeScript Migration Assistant

This skill provides a structured approach to migrating JS to TS, avoiding "big bang" rewrites in favor of an incremental, stable transition.

## Workflow

### 1. Diagnosis (Perceive)
- Analyze the current JS codebase size and complexity.
- Identify "critical paths" (core business logic) that need immediate typing.
- Audit existing JSDoc comments that can be converted to TS types.
- Check for existing build tools (Webpack, Babel, Vite) and their TS compatibility.

### 2. Analysis (Plan)
- Establish a "Migration Map": (1) Infrastructure/Config -> (2) Type Definitions -> (3) Leaf Components -> (4) Core Logic.
- Define a "Strictness Roadmap": Start with `allowJs: true` and `checkJs: false`, gradually enabling strict flags.
- Identify external libraries that lack `@types` definitions and plan for custom `.d.ts` declaration files.
- Set up a "TS-First" rule for all new files.

### 3. Programming (Act)
- **Environment Setup**: Initialize `tsconfig.json` with `allowJs: true` and `outDir` configured.
- **Ambient Declarations**: Create `types/global.d.ts` to define project-wide interfaces and external library types.
- **Incremental Conversion**: Rename `.js` to `.ts` (or `.jsx` to `.tsx`) file-by-file, starting from the leaves of the dependency graph.
- **Type Refinement**: Replace `any` placeholders with actual types as the migration progresses.

### 4. Verification (Evaluate)
- Run `tsc --noEmit` frequently to catch regression errors.
- Verify that the build process remains stable and the output JS is compatible with the runtime.
- Audit the percentage of `any` usages to track migration progress.
- Ensure that the new TS types actually prevent bugs rather than just adding overhead.

## Tech Stack Alignment
- **TypeScript**: Compiler and configuration.
- **Node.js**: Runtime environment.
- **Astro/Vite**: Build tool integration.
