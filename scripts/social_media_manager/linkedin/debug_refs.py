"""Debug: call MCP search_people via HTTP transport and check for profile URLs."""
import asyncio
import httpx
import json

async def main():
    # Start MCP server with HTTP transport
    import subprocess, time
    proc = subprocess.Popen(
        ["uv", "tool", "run", "--from", "mcp-server-linkedin", "mcp-server-linkedin",
         "--transport", "streamable-http", "--port", "31416", "--no-headless"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    time.sleep(8)

    async with httpx.AsyncClient() as client:
        base = "http://127.0.0.1:31416/mcp"

        # Initialize
        init_resp = await client.post(base, json={
            "jsonrpc": "2.0", "method": "initialize", "id": 1,
            "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                       "clientInfo": {"name": "debug", "version": "1.0"}}
        })
        print("Init:", init_resp.status_code, init_resp.text[:200])

        # List tools
        tools_resp = await client.post(base, json={
            "jsonrpc": "2.0", "method": "tools/list", "id": 2, "params": {}
        })
        data = tools_resp.json()
        tool_names = [t["name"] for t in data.get("result", {}).get("tools", [])]
        print(f"Tools: {tool_names}")

        # Call search_people
        call_resp = await client.post(base, json={
            "jsonrpc": "2.0", "method": "tools/call", "id": 3,
            "params": {"name": "search_people", "arguments": {"keywords": "wordpress", "location": "Buenos Aires"}}
        })
        call_data = call_resp.json()
        print(f"\nsearch_people status: {call_resp.status_code}")
        print(f"Result keys: {list(call_data.get('result', {}).keys()) if 'result' in call_data else 'error'}")

        # Extract content
        result = call_data.get("result", {})
        for item in result.get("content", []):
            if item.get("type") == "text":
                text = item["text"]
                print(f"\nText length: {len(text)}")
                # Check for references
                if '"references"' in text:
                    print(">>> FOUND 'references' key!")
                if '"kind"' in text:
                    print(">>> FOUND 'kind' (Reference type)!")
                if '/in/' in text:
                    print(">>> FOUND '/in/' profile URLs!")
                print(f"\nFirst 5000 chars:\n{text[:5000]}")

        # Call get_company_employees
        emp_resp = await client.post(base, json={
            "jsonrpc": "2.0", "method": "tools/call", "id": 4,
            "params": {"name": "get_company_employees", "arguments": {"company_name": "mercadolibre"}}
        })
        emp_data = emp_resp.json()
        print(f"\n\nget_company_employees status: {emp_resp.status_code}")
        for item in emp_data.get("result", {}).get("content", []):
            if item.get("type") == "text":
                text = item["text"]
                print(f"Text length: {len(text)}")
                if '"references"' in text:
                    print(">>> FOUND 'references' key!")
                if '/in/' in text:
                    print(">>> FOUND '/in/' profile URLs!")
                print(f"\nFirst 5000 chars:\n{text[:5000]}")

    proc.terminate()

asyncio.run(main())
