---
name: TypeScript API Client Generator
description: Automates the creation of type-safe API clients that mirror backend schemas, eliminating runtime type errors.
---

# TypeScript API Client Generator

This skill removes the guesswork from API integrations by generating a strictly typed client that ensures the frontend and backend are always in sync.

## Workflow

### 1. Diagnosis (Perceive)
- Analyze the backend API specification (e.g., Swagger/OpenAPI, GraphQL schema, or existing Node.js controllers).
- Identify common patterns in API responses (e.g., pagination wrappers, error formats).
- Audit the current frontend API calls to find "magic strings" and `any` casts.
- Check for existing API client libraries (e.g., `axios`, `fetch`).

### 2. Analysis (Plan)
- Design a "Single Source of Truth" for types: determine if types should be shared via a monorepo, a private npm package, or generated from a schema.
- Plan the client architecture: implement a base `HttpClient` class to handle headers, logging, and error interceptors.
- Map API endpoints to typed methods (e.g., `api.users.getById(id): Promise<User>`).
- Plan for the integration of `zod` for runtime validation of the API responses.

### 3. Programming (Act)
- **Type Generation**: Create TypeScript interfaces/types that exactly match the backend's data models.
- **Client Implementation**: Build the typed API client, utilizing generics for paginated responses (e.g., `PaginatedResponse<T>`).
- **Interceptors**: Implement logic for automatic token injection (JWT) and global error handling (e.g., redirecting to `/login` on 401).
- **Validation Layer**: Integrate `zod.parse()` in the client to catch backend schema changes immediately at the network boundary.

### 4. Verification (Evaluate)
- Run the client against a staging API to verify that all types match the actual responses.
- Verify that the IDE provides accurate autocomplete and type-checking for all API methods.
- Test error handling for various HTTP status codes (400, 403, 404, 500).
- Ensure that the client is lightweight and doesn't introduce unnecessary bundle bloat.

## Tech Stack Alignment
- **TypeScript**: Interfaces, Generics, and Type-safety.
- **Zod**: Runtime response validation.
- **Node.js/Astro**: Integration into the frontend service layer.
