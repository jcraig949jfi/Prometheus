"""PAN-44 conformance: the official MCP Python SDK client (mcp==2.3.0) against Pan's stdio server, every tool once
plus a refused escalation. NOT a pytest test: the SDK is deliberately absent from Pan's venv. Run it from any venv
that has mcp==2.3.0:  <venv>/python -I pan/tests/mcp_sdk_conformance.py  (prints one JSON receipt line)."""
import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

WT = r"D:\Prometheus-worktrees\pan-base-role-adopt-2026-10-09"
PY = r"C:\Prometheus-data\pan\venv\Scripts\python.exe"


async def main():
    params = StdioServerParameters(command=PY, args=["-m", "pan.mcpserve"], cwd=WT,
                                   env={"PAN_CLEARANCE": "generator", "EW_DB_HOST": "192.168.1.202",
                                        "SYSTEMROOT": r"C:\WINDOWS", "PATH": r"C:\WINDOWS\system32"})
    out = {}
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            init = await s.initialize()
            out["protocolVersion"] = init.protocol_version
            out["server"] = init.server_info.name
            tools = await s.list_tools()
            out["tools"] = [t.name for t in tools.tools]
            calls = {"pan_search": {"query": "pgvector HNSW recall", "k": 3},
                     "pan_pivot": {"path": "roles/base-role/MONITORS.md", "k": 2},
                     "pan_refs": {"path": "roles/base-role/MONITORS.md", "k": 2},
                     "atlas_lookup": {"table": "blind_spot", "text": "organism", "k": 2}}
            for name, args in calls.items():
                res = await s.call_tool(name, args)
                sc = res.structured_content or json.loads(res.content[0].text)
                recs = sc["result"].get("records", [])
                out[name] = dict(isError=res.is_error, n=len(recs), clearance=sc["clearance"],
                                 provenance_on_all=all("provenance" in x for x in recs))
            from mcp.shared.exceptions import MCPError
            try:
                bad = await s.call_tool("pan_search", {"query": "x", "clearance": "evaluator"})
                out["escalation_refused"] = bool(bad.is_error)
                out["escalation_text"] = (bad.content[0].text if bad.content else "")[:120]
            except MCPError as e:
                out["escalation_refused"] = True
                out["escalation_text"] = "MCPError: " + str(e)[:120]
    print(json.dumps(out))


asyncio.run(main())
