---
name: Astro API Route Generator
description: Builds secure, type-safe API endpoints using Astro's server-side routing and Cloudflare Pages Functions.
---

# Astro API Route Generator

This skill focuses on creating a robust backend layer within Astro, leveraging its ability to handle server-side logic via API routes.

## Workflow

### 1. Diagnosis (Perceive)
- Identify the necessary API endpoints (e.g., `/api/contact`, `/api/get-posts`, `/api/auth`).
- Determine the required request methods (`GET`, `POST`, `PUT`, `DELETE`).
- Audit the data sources (e.g., Content Collections, external APIs, Cloudflare KV).
- Review the authentication and authorization requirements for each route.

### 2. Analysis (Plan)
- Design the API structure: use a consistent response format (e.g., `{ success: boolean, data: T, error: string | null }`).
- Plan the validation strategy using `zod` for all incoming request bodies and query parameters.
- Determine the appropriate Cloudflare adapter configuration for the routes (e.g., Hybrid vs SSR).
- Plan for rate limiting and CORS policies to protect the endpoints.

### 3. Programming (Act)
- **Route Implementation**: Create `.ts` files in `src/pages/api/` implementing the `APIRoute` handler.
- **Input Validation**: Integrate `zod` schemas to validate `request.json()` or `url.searchParams`.
- **Business Logic**: Implement the core logic, integrating with Cloudflare KV, D1, or external services.
- **Response Handling**: Standardize responses using a helper function to ensure consistent HTTP status codes and JSON structures.

### 4. Verification (Evaluate)
- Test endpoints using `curl` or Postman, ensuring all edge cases (invalid input, unauthorized access) are handled.
- Verify that the API routes are correctly deployed as Cloudflare Pages Functions.
- Measure response times and optimize slow database queries or external API calls.
- Audit the security of the endpoints (e.g., checking for XSS or CSRF vulnerabilities).

## Tech Stack Alignment
- **Astro**: API route routing (`src/pages/api/`).
- **Cloudflare Pages Functions**: Runtime for API execution.
- **Zod**: Request validation.
- **TypeScript**: Type-safe request/response handling.
