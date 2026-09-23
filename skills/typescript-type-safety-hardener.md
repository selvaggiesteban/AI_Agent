---
name: TypeScript Type Safety Hardener
description: Enhances codebase type safety by eliminating 'any', implementing strict null checks, and introducing advanced TS utility types.
---

# TypeScript Type Safety Hardener

This skill transforms a "loose" TypeScript codebase into a strictly typed, resilient system, reducing runtime errors and improving developer experience.

## Workflow

### 1. Diagnosis (Perceive)
- Search for all occurrences of `any` and `unknown` across the project.
- Identify "type holes" where `as any` or `@ts-ignore` are used to bypass the compiler.
- Audit API response types and external library integrations for missing or generic types.
- Check `tsconfig.json` for `strict: true` and related strictness flags.

### 2. Analysis (Plan)
- Categorize `any` usages into: (a) easily replaceable with specific types, (b) requiring complex generics, (c) external library limitations.
- Design a strategy for implementing `Zod` or `Valibot` for runtime validation of API boundaries.
- Plan the migration from optional properties (`?`) to explicit `null` or `undefined` where business logic requires it.
- Identify opportunities for `Discriminated Unions` to replace boolean flags.

### 3. Programming (Act)
- **Strict Config**: Update `tsconfig.json` to enable `strictNullChecks`, `noImplicitAny`, and `noImplicitReturns`.
- **Type Replacement**: Systematically replace `any` with precise interfaces, types, or generics.
- **Boundary Hardening**: Implement `zod` schemas for all API responses and environment variables, ensuring type safety at the edge.
- **Utility implementation**: Create custom utility types (e.g., `DeepPartial`, `RequiredBy`) to handle complex object transformations.

### 4. Verification (Evaluate)
- Run `tsc --noEmit` to identify new type errors introduced by strictness.
- Resolve all compiler errors without using `@ts-ignore`.
- Verify that the runtime validation (Zod) correctly catches malformed data before it reaches the business logic.
- Audit the "type-to-value" ratio to ensure types are aiding development, not hindering it.

## Tech Stack Alignment
- **TypeScript**: Core language features, `tsconfig` optimization.
- **Zod**: Runtime schema validation.
- **Node.js/Astro**: Applying types to server-side functions and component props.
