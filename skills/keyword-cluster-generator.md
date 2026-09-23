---
name: Keyword Cluster Generator
description: Groups target keywords into semantic clusters to inform content architecture and avoid keyword cannibalization.
---

# Keyword Cluster Generator

## Workflow: Perceive-Plan-Act-Evaluate

### 1. Diagnosis (Perceive)
- Aggregate a master list of keywords from GSC, competitor analysis, and seed research.
- Extract "Search Volume" and "Keyword Difficulty" (KD) for each term.
- Identify "Cannibalization": Multiple pages ranking for the same keyword.
- Analyze "Search Intent" (Informational, Transactional, etc.) for each keyword.

### 2. Analysis (Plan)
- Perform "Semantic Grouping":
    - Group keywords with the same "Search Intent".
    - Group keywords that share the same top 3-5 SERP results (The "SERP-based" method).
- Define the "Pillar" (High volume, broad term) and "Cluster/Spoke" (Long-tail, specific terms).
- Design the internal linking map: Spoke Pages -> Pillar Page.

### 3. Programming (Act)
- Use a Python script with `scikit-learn` or `sentence-transformers` to cluster keywords by cosine similarity.
- Generate a "Content Map" (JSON/CSV) that assigns each keyword to a specific URL/Page.
- Create an Astro-based "Topic Hub" structure to implement the clusters.
- Implement "Internal Link Anchors" based on the clustered keywords.

### 4. Verification (Evaluate)
- Audit the site for "Keyword Cannibalization" using GSC (ensure only one page ranks per cluster).
- Monitor the "Average Position" for the Pillar page as Spoke pages are published.
- Track the increase in "Top 10" rankings for long-tail keywords within the cluster.
- Measure the growth in "Topical Authority" through an increase in rankings for broad industry terms.