---
name: Multilingual SEO Hreflang Auditor
description: Implements and validates hreflang tags to ensure the correct language version of a page is served to users and indexed by Google.
---

# Multilingual SEO Hreflang Auditor

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- Audit the site for `rel="alternate" hreflang="x"` tags in the `<head>` or HTTP headers.
- Identify "Hreflang Mismatches": Page A (EN) points to Page B (ES), but Page B (ES) does not point back to Page A (EN).
- Locate "Incorrect Language Codes" (e.g., using `en` instead of `en-us`).
- Identify "Missing x-default" tags for users with no matching language.

### 2. Analysis (Plan)
- Map the "Language Matrix": Every page must have a corresponding link to all other language versions of that same page.
- Define the "Regional Strategy" (e.g., `en-gb` for UK, `en-ca` for Canada).
- Choose the implementation method: HTML tags (easier for Astro) vs XML Sitemap (cleaner for huge sites).
- Plan the URL structure (e.g., `/en/`, `/es/` or `en.domain.com`).

### 3. Programming (Act)
- Implement a dynamic `Hreflang` component in Astro:
  ```astro
  ---
  const { locales, currentLang, slug } = Astro.props;
  ---
  {locales.map(lang => (
    <link rel="alternate" href={`/${lang}/${slug}`} hreflang={lang} />
  ))}
  <link rel="alternate" href="/en/..." hreflang="x-default" />
  ```
- Ensure the `lang` attribute in the `<html>` tag matches the hreflang value.
- Use TypeScript to validate that all linked language versions return a `200 OK` status.
- Configure Cloudflare to handle language-based routing (redirects) if necessary.

### 4. Verification (Evaluate)
- Validate implementation using a "Hreflang Checker" tool.
- Monitor GSC "International Targeting" reports (where available).
- Track "Traffic by Country" in GA4 to ensure users are landing on the correct language version.
- Check for "Duplicate Content" warnings in GSC for multilingual pages.