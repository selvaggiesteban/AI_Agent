---
name: Tailwind Responsive Audit
description: Performs a comprehensive audit of Tailwind CSS responsive utilities to ensure a seamless experience across all device breakpoints.
---

# Tailwind Responsive Audit

This skill ensures that a website is truly responsive, not just "mobile-friendly," by auditing and refining Tailwind's breakpoint usage.

## Workflow

### 1. Diagnosis (Perceive)
- Use browser DevTools to test the site across standard breakpoints (`sm`, `md`, `lg`, `xl`, `2xl`).
- Identify "broken" layouts: horizontal scrolling, overlapping elements, or excessive whitespace on large screens.
- Search for hardcoded widths/heights (`w-[500px]`) that override responsive behavior.
- Audit the usage of `flex` and `grid` to see where they fail at specific widths.

### 2. Analysis (Plan)
- Map the "breaking points" of the current UI.
- Determine if custom breakpoints are needed in `tailwind.config.js` for specific device targets (e.g., tablets in portrait).
- Plan the transition from "Mobile-First" (default) to "Desktop-Down" if the current implementation is inconsistent.
- Identify components that should switch layouts entirely (e.g., a burger menu vs. a horizontal nav).

### 3. Programming (Act)
- **Breakpoint Refinement**: Replace arbitrary values with Tailwind's responsive prefixes (e.g., `w-full md:w-1/2 lg:w-1/3`).
- **Grid/Flex Optimization**: Implement `grid-cols-1 md:grid-cols-2 lg:grid-cols-4` for fluid content layouts.
- **Visibility Toggling**: Use `hidden md:block` and `block md:hidden` to swap components based on screen size.
- **Config Extension**: Add custom screens to `tailwind.config.js` if the standard ones are insufficient.

### 4. Verification (Evaluate)
- Perform "stress tests" by resizing the browser window continuously to find "jittery" transitions.
- Verify that typography scales correctly (e.g., `text-base md:text-lg lg:text-xl`).
- Test on actual physical devices (iOS, Android, MacOS, Windows) if possible.
- Ensure that interaction patterns (touch vs. click) are appropriately handled at each breakpoint.

## Tech Stack Alignment
- **Tailwind CSS**: Responsive prefixes and config.
- **Astro**: Ensuring responsive components render correctly on the server.
- **TypeScript**: Typing responsive prop variations if applicable.
