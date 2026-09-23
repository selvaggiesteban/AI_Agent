---
name: Content Gap Analysis Engine
description: Identifies missing content opportunities by comparing site keywords against competitors and search intent.
---

# Content Gap Analysis Engine

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- Collect current keyword rankings and organic landing pages from GSC/GA4.
- Identify top 3-5 direct competitors in the same niche.
- Extract competitor keyword profiles using SEO tools (Ahrefs, Semrush, or GSC-based proxies).
- Map existing content to target "Search Intent" (Informational, Navigational, Transactional, Commercial).

### 2. Analysis (Plan)
- Perform a "Gap Analysis": (Competitor Keywords) MINUS (Own Keywords).
- Cluster the gaps into "Content Hubs" or "Topic Clusters".
- Evaluate the "Difficulty vs. Opportunity" score for each gap.
- Plan the content structure (e.g., Long-form guides, comparison pages, Listicles).

### 3. Programming (Act)
- Create a Content Roadmap in Markdown/JSON.
- Implement "Content Hub" architecture in Astro using dynamic routing (`[...slug].astro`).
- Use Python/Node.js to generate suggested outlines based on Top 10 SERP results.
- Optimize internal linking from existing high-authority pages to new gap-filling content.

### 4. Verification (Evaluate)
- Track new keyword entries in GSC.
- Monitor the growth of "Impressions" for the newly created topic clusters.
- Analyze "Average Position" movement for target gap keywords.
- Measure the increase in organic traffic to the new content assets.