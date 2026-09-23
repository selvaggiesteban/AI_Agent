---
name: Tailwind Design System Generator
description: Automates the creation of a consistent Tailwind CSS design system including config tokens, utility classes, and theme extensions.
---

# Tailwind Design System Generator

This skill automates the generation of a production-ready Tailwind CSS design system, ensuring consistency across the project while leveraging the full power of Tailwind's configuration.

## Workflow

### 1. Diagnosis (Perceive)
- Scan `tailwind.config.js` (or `.ts`) for existing theme extensions.
- Analyze global CSS files (e.g., `globals.css`, `app.css`) for hardcoded hex values or arbitrary spacing.
- Identify recurring UI patterns in Astro components to determine necessary design tokens (colors, spacing, typography).
- Check for existing design documentation or Figma specs if available.

### 2. Analysis (Plan)
- Map identified patterns to Tailwind's theme structure: `colors`, `spacing`, `fontFamily`, `borderRadius`, and `boxShadow`.
- Define a semantic naming convention (e.g., `brand-primary`, `surface-muted`, `text-accent`) instead of descriptive names (e.g., `blue-500`).
- Determine the need for custom plugins (e.g., for complex grids or specific animations).
- Plan the integration of CSS variables for dynamic theme switching.

### 3. Programming (Act)
- **Update Config**: Modify `tailwind.config.js` to include the analyzed tokens. Use `extend` to preserve default Tailwind utilities.
- **CSS Variables**: Implement a `:root` block in the main CSS file to map Tailwind tokens to CSS variables for runtime flexibility.
- **Utility Generation**: Create a set of reusable `@apply` directives for common design system patterns (e.g., `.btn-primary`, `.card-surface`).
- **TypeScript Integration**: If using TS, create a type-safe mapping of the design system tokens to prevent magic strings in components.

### 4. Verification (Evaluate)
- Run `npx tailwindcss` to check for config syntax errors.
- Perform a visual audit of key components to ensure the new design system is applied correctly.
- Verify that no arbitrary values (`[... ]`) remain in the codebase where a token should exist.
- Test responsiveness and dark mode compatibility of the generated tokens.

## Tech Stack Alignment
- **Tailwind CSS**: Core implementation via `tailwind.config.js`.
- **Astro**: Integration with `.astro` components.
- **TypeScript**: Type-safe token definitions.
