---
name: Tailwind Accessibility Auditor
description: Audits and fixes accessibility (a11y) issues in Tailwind CSS layouts, ensuring WCAG 2.1 compliance.
---

# Tailwind Accessibility Auditor

This skill ensures that the visual beauty of Tailwind CSS does not come at the cost of accessibility, making the web inclusive for everyone.

## Workflow

### 1. Diagnosis (Perceive)
- Run automated scans using `axe-core`, `Lighthouse`, or `WAVE`.
- Audit color contrast for all text and UI elements using Tailwind's color palette.
- Check for missing `aria-*` attributes and incorrect HTML semantic structure.
- Test keyboard navigation: ensure all interactive elements are reachable and have visible focus states.

### 2. Analysis (Plan)
- Categorize a11y failures into: (a) Color/Contrast, (b) Keyboard/Focus, (c) Semantics/ARIA, (d) Screen Reader compatibility.
- Plan the implementation of a "High Contrast" mode or specific a11y-focused color tokens.
- Design a consistent `focus-visible` strategy using Tailwind's `focus:` and `focus-within:` utilities.
- Map missing ARIA roles to the corresponding Tailwind-styled components.

### 3. Programming (Act)
- **Contrast Correction**: Adjust Tailwind color classes to meet WCAG AA/AAA standards (e.g., changing `text-gray-400` to `text-gray-600` on light backgrounds).
- **Focus Management**: Implement clear, accessible focus rings (e.g., `focus:outline-none focus:ring-2 focus:ring-blue-500`).
- **Semantic Overhaul**: Replace generic `div` tags with `main`, `section`, `nav`, and `article` where appropriate.
- **ARIA Implementation**: Add `aria-expanded`, `aria-controls`, and `role` attributes to interactive components (modals, dropdowns).

### 4. Verification (Evaluate)
- Re-run automated a11y scans to ensure zero "critical" or "serious" errors.
- Perform manual testing with a screen reader (e.g., NVDA, VoiceOver).
- Verify that the tab order is logical and intuitive across the entire page.
- Test the UI with "Reduced Motion" preferences using Tailwind's `motion-safe:` and `motion-reduce:` modifiers.

## Tech Stack Alignment
- **Tailwind CSS**: Contrast utilities and focus states.
- **Astro**: Semantic HTML structure.
- **TypeScript**: Typing ARIA states in component props.
