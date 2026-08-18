"""Quick run: test scraper with 2 people keywords + 1 job keyword."""
import asyncio, json, sys, os
sys.path.insert(0, r'C:\Users\Esteban Selvaggi\Desktop\subagent-driven_development\scripts\social_media_manager\linkedin')
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

async def main():
    from linkedin_full_scraper import MCPClient, _parse_people_refs, _parse_job_refs, _parse_employee_refs, _parse_post_refs, _parse_author_refs, _save_json

    mcp = MCPClient()
    print("[*] Connecting...")
    await mcp.connect()
    print("[OK] Connected\n")

    results = {"people": [], "jobs": [], "posts_feed": [], "authors": []}
    seen_profiles = set()

    # Test 2 people keywords
    for kw in ["IT Recruiter", "Talent Acquisition"]:
        print(f"[PEOPLE] {kw}")
        data = await mcp.call_raw("search_people", {"keywords": kw, "location": "Buenos Aires"})
        if data:
            people = _parse_people_refs(data, kw)
            new = 0
            for p in people:
                url = p.get("profile_url", "")
                if url and url not in seen_profiles:
                    seen_profiles.add(url)
                    results["people"].append(p)
                    new += 1
            print(f"  -> {new} new (total refs: {len(people)})")
        await asyncio.sleep(1)

    # Test 1 job keyword
    print(f"\n[jOBS] wordpress")
    data = await mcp.call_raw("search_jobs", {"keywords": "wordpress", "location": "Buenos Aires"})
    if data:
        jobs = _parse_job_refs(data, "wordpress")
        print(f"  -> {len(jobs)} jobs")
        results["jobs"] = jobs

    # Test feed
    print(f"\n[FEED]")
    data = await mcp.call_raw("get_feed", {"num_posts": 50})
    if data:
        posts = _parse_post_refs(data, "feed")
        authors = _parse_author_refs(data, "feed")
        for a in authors:
            url = a.get("profile_url", "")
            if url and url not in seen_profiles:
                seen_profiles.add(url)
                results["authors"].append(a)
        print(f"  -> {len(posts)} posts, {len(authors)} authors")

    await mcp.close()

    # Save
    outdir = os.path.join("data", "outputs", "linkedin")
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "quick_test.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n=== RESULTS ===")
    print(f"People: {len(results['people'])}")
    print(f"Jobs: {len(results['jobs'])}")
    print(f"Posts: {len(results['posts_feed'])}")
    print(f"Authors: {len(results['authors'])}")
    print(f"Unique profiles: {len(seen_profiles)}")
    print(f"Saved: {path}")

asyncio.run(main())
