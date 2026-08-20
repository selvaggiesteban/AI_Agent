"""Quick test: count results per MCP tool call."""
import asyncio, json, sys
from pathlib import Path

# Normalización de rutas para portabilidad
from core.paths import PROJECT_ROOT
sys.path.append(str(PROJECT_ROOT / "scripts" / "social_media_manager" / "linkedin"))

async def main():
    from linkedin_full_scraper import MCPClient

    mcp = MCPClient()
    print("[*] Connecting...")
    await mcp.connect()
    print("[OK] Connected\n")

    # Test search_people with one keyword
    print("=== search_people (IT Recruiter, Buenos Aires) ===")
    data = await mcp.call_raw("search_people", {"keywords": "IT Recruiter", "location": "Buenos Aires"})
    if data:
        refs = data.get("references", {}).get("search_results", [])
        persons = [r for r in refs if r.get("kind") == "person"]
        print(f"  References: {len(refs)}, Persons: {len(persons)}")
        for r in persons[:3]:
            print(f"    {r.get('text', '')} -> {r.get('url', '')}")
    else:
        print("  No data")

    # Test search_jobs with one keyword
    print("\n=== search_jobs (wordpress, Buenos Aires) ===")
    data2 = await mcp.call_raw("search_jobs", {"keywords": "wordpress", "location": "Buenos Aires"})
    if data2:
        refs = data2.get("references", {}).get("search_results", [])
        jobs = [r for r in refs if r.get("kind") == "job"]
        print(f"  References: {len(refs)}, Jobs: {len(jobs)}")
        for r in jobs[:3]:
            print(f"    {r.get('text', '')} -> {r.get('url', '')}")
    else:
        print("  No data")

    # Test get_feed
    print("\n=== get_feed ===")
    data3 = await mcp.call_raw("get_feed", {"num_posts": 50})
    if data3:
        refs = data3.get("references", {})
        all_refs = []
        for v in refs.values():
            if isinstance(v, list):
                all_refs.extend(v)
        posts = [r for r in all_refs if r.get("kind") in ("feed_post", "article")]
        persons = [r for r in all_refs if r.get("kind") == "person"]
        print(f"  Total refs: {len(all_refs)}, Posts: {len(posts)}, Authors: {len(persons)}")
    else:
        print("  No data")

    # Test get_company_employees
    print("\n=== get_company_employees (mercadolibre) ===")
    data4 = await mcp.call_raw("get_company_employees", {"company_name": "mercadolibre"})
    if data4:
        refs = data4.get("references", {})
        emp_refs = refs.get("employees", [])
        persons = [r for r in emp_refs if r.get("kind") == "person"]
        print(f"  Employee refs: {len(persons)}")
        for r in persons[:3]:
            print(f"    {r.get('text', '')} -> {r.get('url', '')}")
    else:
        print("  No data")

    await mcp.close()
    print("\n[DONE]")

asyncio.run(main())
