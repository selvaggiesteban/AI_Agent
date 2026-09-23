---
name: TypeScript Generic Utility Builder
description: Develops reusable, high-order TypeScript utilities for complex data transformations and type manipulations.
---

# TypeScript Generic Utility Builder

This skill focuses on creating advanced, reusable type logic to eliminate boilerplate and ensure consistency across large-scale TypeScript projects.

## Workflow

### 1. Diagnosis (Perceive)
- Search for repetitive type declarations that follow a similar pattern (e.g., mapping API responses to UI models).
- Identify complex object transformations that currently rely on `any` or manual casting.
- Audit existing utility types for redundancy or lack of flexibility.
- Analyze the data structures of the project's core domain.

### 2. Analysis (Plan)
- Identify the "variable" parts of the repetitive types to determine where generics are needed.
- Plan the implementation of advanced TS features: `Conditional Types`, `Mapped Types`, `Template Literal Types`, and `Infer`.
- Design the utility API to be intuitive (e.g., `Select<T, K>` instead of complex nested generics).
- Determine if the utility should be a type-only helper or a runtime function with generic constraints.

### 3. Programming (Act)
- **Core Utilities**: Implement high-order types like `DeepReadonly<T>`, `PartialBy<T, K>`, or `OmitByValue<T, V>`.
- **Domain-Specific Generics**: Create utilities tailored to the project (e.g., `ApiResponse<T>`, `EntityWithId<T>`).
- **Type Guards**: Implement generic type predicates (e.g., `isNotNull<T>(val: T | null): val is T`) to safely narrow types.
- **Documentation**: Provide clear examples of "Before" and "After" usage for each utility.

### 4. Verification (Evaluate)
- Create a "Type Test Suite" using `.ts` files that intentionally trigger compiler errors if the utility fails.
- Verify that the utilities maintain type inference without requiring explicit casting.
- Audit the impact on IDE performance (ensure complex types don't slow down the TS Server).
- Peer review the utilities for readability and maintainability.

## Tech Stack Alignment
- **TypeScript**: Advanced type system (Generics, Conditional Types).
- **Node.js/Astro**: Applying utilities to server-side data and component props.
