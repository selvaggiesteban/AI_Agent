---
name: Astro Island Hydration Optimizer
description: Minimizes client-side JavaScript by auditing and optimizing Astro's hydration directives for maximum performance.
---

# Astro Island Hydration Optimizer

This skill focuses on the "surgical" application of JavaScript, ensuring that only the absolute minimum amount of code is hydrated on the client.

## Workflow

### 1. Diagnosis (Perceive)
- Audit all components using `client:*` directives (e.g., `client:load`, `client:only`).
- Use Chrome DevTools "Coverage" tab to identify unused JS shipped to the browser.
- Analyze the "Total Blocking Time" (TBT) and "Interaction to Next Paint" (INP).
- Identify components that are hydrated immediately but not used until much later.

### 2. Analysis (Plan)
- Categorize components by "Hydration Urgency":
    - **Critical**: Needs immediate interaction (e.g., mobile menu) -> `client:load`.
    - **Visible**: Interaction happens when seen (e.g., carousel) -> `client:visible`.
    - **Idle**: Background tasks (e.g., analytics, chat widget) -> `client:idle`.
    - **Event-driven**: Only on specific action (e.g., clicking a button) -> `client:only` or custom event.
- Plan the conversion of interactive components back to static `.astro` components where possible.

### 3. Programming (Act)
- **Directive Refinement**: Replace `client:load` with `client:visible` or `client:idle` for non-critical components.
- **Component Splitting**: Break large interactive components into smaller, independently hydrated islands.
- **Static Conversion**: Remove hydration from components that only need JS for a one-time action (replace with vanilla JS in a `<script>` tag).
- **Conditional Hydration**: Implement logic to only hydrate components based on user device or state.

### 4. Verification (Evaluate)
- Measure the reduction in "Total JS Bundle Size" and "Hydration Time".
- Verify that the user experience remains seamless (no "jank" when components hydrate).
- Check that components using `client:visible` trigger correctly as the user scrolls.
- Use Lighthouse to verify improvement in "Total Blocking Time".

## Tech Stack Alignment
- **Astro**: Hydration directives (`client:load`, `client:visible`, etc.).
- **React/Svelte/Vue**: Framework-specific island implementation.
- **Web Vitals**: Monitoring INP and TBT.
