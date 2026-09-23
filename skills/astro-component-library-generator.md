---
name: Astro Component Library Generator
description: Creates a scalable, documented, and type-safe UI component library using Astro, Tailwind CSS, and TypeScript.
---

# Astro Component Library Generator

This skill establishes a professional UI foundation by building a reusable component library that follows the "Island Architecture" and Atomic Design principles.

## Workflow

### 1. Diagnosis (Perceive)
- Analyze the project's UI requirements and recurring patterns (e.g., buttons, inputs, cards, modals).
- Review existing styles to ensure the library aligns with the design system.
- Identify which components should be static (`.astro`) and which require interactivity (React/Vue/Svelte islands).
- Assess the need for accessibility (a11y) standards (WCAG 2.1).

### 2. Analysis (Plan)
- Organize components by Atomic Design: Atoms (basic), Molecules (combinations), Organisms (complex sections).
- Define a consistent prop API for all components (e.g., `className` for overrides, `children` for nesting).
- Plan the documentation strategy (e.g., a `/components` route in Astro with live previews).
- Design the theme integration using Tailwind CSS variables.

### 3. Programming (Act)
- **Base Components**: Build the Atomic components in `.astro` for maximum performance (zero JS).
- **Interactive Islands**: Implement complex components as framework-specific islands (e.g., `Client:visible` for modals).
- **Type Definitions**: Create strict TypeScript interfaces for all component props.
- **Tailwind Integration**: Use the `clsx` or `tailwind-merge` utility to handle dynamic class merging.
- **Documentation**: Create an Astro-based style guide showcasing every component state (default, hover, active, disabled).

### 4. Verification (Evaluate)
- Test components across multiple screen sizes using Tailwind's responsive utilities.
- Verify accessibility using tools like axe-core or WAVE.
- Ensure that only necessary JS is shipped to the client (minimal hydration).
- Audit the component API for consistency and ease of use.

## Tech Stack Alignment
- **Astro**: Component framework and build tool.
- **Tailwind CSS**: Styling and utility-first design.
- **TypeScript**: Prop safety and interface definitions.
- **React/Svelte/Vue**: Interactivity for Astro Islands.
