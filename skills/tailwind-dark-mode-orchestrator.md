---
name: Tailwind Dark Mode Orchestrator
description: Implements a robust, flicker-free dark mode system using Tailwind CSS, CSS variables, and local storage.
---

# Tailwind Dark Mode Orchestrator

This skill implements a professional dark mode system that respects user preferences and avoids the dreaded "white flash" on page load.

## Workflow

### 1. Diagnosis (Perceive)
- Review current color usage to see if it's based on fixed colors (e.g., `bg-white`) or semantic tokens (e.g., `bg-surface`).
- Check if the project uses the `class` or `media` strategy for dark mode in `tailwind.config.js`.
- Identify components with hardcoded colors that will break in dark mode.
- Analyze the current theme-switching logic (if any).

### 2. Analysis (Plan)
- Design a semantic color palette for both themes (e.g., `surface-primary` -> White in Light, Dark Grey in Dark).
- Plan the "Blocking Script" implementation to detect theme preference before the browser renders the first pixel.
- Determine the storage strategy for user preference (`localStorage` vs. `cookies` for SSR).
- Design the UI for the theme toggle (e.g., Sun/Moon icon with smooth transition).

### 3. Programming (Act)
- **Config Setup**: Set `darkMode: 'class'` in `tailwind.config.js`.
- **Semantic Tokens**: Define CSS variables in the global CSS file for both `.light` and `.dark` classes.
- **Flicker-Fix Script**: Implement a small, inline `<script>` in the `<head>` of the Astro layout to apply the correct theme class immediately.
- **Toggle Component**: Build a type-safe Astro component to handle the theme switch and update `localStorage`.

### 4. Verification (Evaluate)
- Test the transition between light and dark modes to ensure no "visual popping".
- Verify that the theme persists across page reloads and different browser sessions.
- Audit the contrast ratios of the dark theme using accessibility tools.
- Ensure that the "system preference" (prefers-color-scheme) is respected by default.

## Tech Stack Alignment
- **Tailwind CSS**: `darkMode: 'class'`, dark: modifiers.
- **Astro**: Layout-level script implementation.
- **CSS Variables**: Theme-based tokenization.
- **TypeScript**: Type-safe theme state management.
