---
name: Astro Content Collections Optimizer
description: Optimizes Astro's Content Collections for performance, type safety, and scalable content management.
---

# Astro Content Collections Optimizer

This skill transforms Astro's content layer from a basic folder of Markdown files into a high-performance, type-safe CMS-like system.

## Workflow

### 1. Diagnosis (Perceive)
- Audit existing `src/content/config.ts` for loose schema definitions (e.g., using `z.any()`).
- Analyze the volume of content files; identify slow build times caused by excessive content processing.
- Check for redundant data across Markdown/MDX frontmatter.
- Review how content is queried in `.astro` pages (`getCollection`).

### 2. Analysis (Plan)
- Refine the Zod schemas to include strict validation, defaults, and transformations.
- Plan for "Content Relationships" (e.g., linking a post to an author) using ID-based references.
- Identify opportunities to use `getEntry` for direct lookups instead of filtering large collections.
- Plan the implementation of a content-driven navigation system (e.g., automatic TOC generation).

### 3. Programming (Act)
- **Schema Hardening**: Update `config.ts` with precise Zod schemas, ensuring all required fields are present.
- **Data Transformation**: Use Zod's `.transform()` to pre-process frontmatter (e.g., converting date strings to JS Date objects).
- **Query Optimization**: Optimize `getCollection` calls by filtering early and selecting only necessary fields.
- **Dynamic Routing**: Implement scalable `[...slug].astro` patterns that handle nested content hierarchies.

### 4. Verification (Evaluate)
- Run `astro build` to ensure the content schema validation catches any malformed frontmatter.
- Verify that the generated types for content entries are accurate in the IDE.
- Measure the impact on build time after optimizing collection queries.
- Test the robustness of the routing when content files are added or moved.

## Tech Stack Alignment
- **Astro**: Content Collections API.
- **Zod**: Schema validation and transformation.
- **TypeScript**: End-to-end type safety for content.
