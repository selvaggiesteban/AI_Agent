"""Quick test: MCP search_people and check references for profile URLs."""
import asyncio, json, sys
sys.path.insert(0, r'C:\Users\Esteban Selvaggi\Desktop\subagent-driven_development\scripts\social_media_manager\linkedin')

async def main():
    from linkedin_full_scraper import MCPClient

    mcp = MCPClient()
    print("[*] Connecting...")
    await mcp.connect()
    print("[OK] Connected\n")

    # Test search_people
    print("=== search_people (wordpress, Buenos Aires) ===")
    data = await mcp.call_raw("search_people", {"keywords": "wordpress", "location": "Buenos Aires"})
    if data:
        refs = data.get("references", {}).get("search_results", [])
        person_refs = [r for r in refs if r.get("kind") == "person"]
        print(f"Total references: {len(refs)}")
        print(f"Person references: {len(person_refs)}")
        for r in person_refs[:5]:
            print(f"  {r.get('text', '')} -> {r.get('url', '')}")
    else:
        print("  No data returned")

    # Test search_jobs
    print("\n=== search_jobs (wordpress) ===")
    data2 = await mcp.call_raw("search_jobs", {"keywords": "wordpress", "location": "Buenos Aires"})
    if data2:
        refs = data2.get("references", {}).get("search_results", [])
        job_refs = [r for r in refs if r.get("kind") == "job"]
        print(f"Total references: {len(refs)}")
        print(f"Job references: {len(job_refs)}")
        for r in job_refs[:5]:
            print(f"  {r.get('text', '')} -> {r.get('url', '')}")
    else:
        print("  No data returned")

    # Test get_company_employees
    print("\n=== get_company_employees (mercadolibre) ===")
    data3 = await mcp.call_raw("get_company_employees", {"company_name": "mercadolibre"})
    if data3:
        refs = data3.get("references", {})
        emp_refs = refs.get("employees", [])
        person_refs = [r for r in emp_refs if r.get("kind") == "person"]
        print(f"Employee references: {len(person_refs)}")
        for r in person_refs[:5]:
            print(f"  {r.get('text', '')} -> {r.get('url', '')}")
    else:
        print("  No data returned")

    await mcp.close()
    print("\n[DONE]")

asyncio.run(main())
