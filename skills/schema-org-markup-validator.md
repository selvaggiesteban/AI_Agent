---
name: Schema.org Markup Validator
description: Implements and validates advanced JSON-LD structured data to enhance SERP visibility and Rich Snippets.
---

# Schema.org Markup Validator

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- Audit current structured data using the "Schema Markup Validator" and "Rich Results Test".
- Identify missing opportunities for: `Product`, `FAQPage`, `Review`, `Organization`, `BreadcrumbList`, `Article`.
- Analyze competitor rich snippets in SERPs to identify high-impact schema types.
- Check GSC for "Enhancements" reports (e.g., Merchant listings, Sitelinks search box).

### 2. Analysis (Plan)
- Map page types to appropriate Schema.org types:
    - Product Page -> `Product` + `Offer` + `AggregateRating`.
    - Blog Post -> `BlogPosting` + `Person` (Author).
    - Home Page -> `Organization` + `LocalBusiness`.
- Design the data mapping from the CMS (WordPress/Shopify) or Astro frontmatter to JSON-LD.

### 3. Programming (Act)
- Implement JSON-LD in Astro as a reusable component:
  ```astro
  ---
  const { product } = Astro.props;
  const schema = {
    "@context": "https://schema.org/",
    "@type": "Product",
    "name": product.title,
    "description": product.description,
    "offers": { "@type": "Offer", "price": product.price }
  };
  ---
  <script type="application/ld+json" set:html={JSON.stringify(schema)} />
  ```
- Ensure dynamic values (price, rating) are updated in real-time.
- Add `SameAs` links to social profiles in `Organization` schema.

### 4. Verification (Evaluate)
- Validate all implemented markup using the Rich Results Test tool.
- Monitor GSC "Enhancements" for "Valid" status and "Impressions" for rich snippets.
- Track the increase in Organic CTR for pages with rich snippets.
- Periodically audit for "Schema warnings" in the GSC console.