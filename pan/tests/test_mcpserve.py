"""PAN-44 protocol and argument handling (no database): the parts of the MCP server that decide what reaches a tool.
Live controls with the database (clearance pairs, provenance, refusals, read-only session) are `python -m pan mcp
controls` -> roles/Pan/reports/controls/MCP_<ts>.json."""
from pan import mcpserve as m


def _req(method, params=None, mid=1):
    return {"jsonrpc": "2.0", "id": mid, "method": method, "params": params or {}}


def test_initialize_negotiates_protocol_and_declares_tools_only():
    r = m.handle(_req("initialize", {"protocolVersion": "2025-06-18"}))["result"]
    assert r["protocolVersion"] == "2025-06-18" and r["serverInfo"]["name"] == "pan"
    assert set(r["capabilities"]) == {"tools"}
    assert m.handle(_req("initialize", {"protocolVersion": "1999-01-01"}))["result"]["protocolVersion"] == m.PROTOCOLS[0]


def test_tools_are_the_four_wrapped_operations_all_read_only_with_closed_schemas():
    tools = m.handle(_req("tools/list"))["result"]["tools"]
    assert [t["name"] for t in tools] == ["pan_search", "pan_pivot", "pan_refs", "atlas_lookup"]
    for t in tools:
        assert t["annotations"]["readOnlyHint"] is True and t["annotations"]["destructiveHint"] is False
        assert t["inputSchema"]["additionalProperties"] is False
        assert not {"role", "clearance", "sql"} & set(t["inputSchema"]["properties"])


def test_arguments_are_validated_before_any_tool_runs():
    def call(name, args):
        return m.handle(_req("tools/call", {"name": name, "arguments": args}))
    for name, args, why in [("pan_search", {"query": "x", "clearance": "evaluator"}, "unknown argument"),
                            ("pan_search", {}, "missing required"),
                            ("pan_search", {"query": "x" * 501}, "length"),
                            ("pan_search", {"query": "x", "k": 26}, "within"),
                            ("pan_search", {"query": "x", "k": True}, "integer"),
                            ("atlas_lookup", {"table": "harvest_run"}, "one of"),
                            ("pan_pivot", {"path": 7}, "string")]:
        e = call(name, args)["error"]
        assert e["code"] == -32602 and why in e["message"], (args, e)
    assert call("pan_write", {})["error"]["code"] == -32602


def test_jsonrpc_edges():
    assert m.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}) is None
    assert m.handle(_req("ping"))["result"] == {}
    assert m.handle(_req("resources/list"))["error"]["code"] == -32601
    assert m.handle([_req("ping")])["error"]["code"] == -32600
    assert m.handle({"id": 3, "method": "ping"})["error"]["code"] == -32600


def test_privileged_launch_is_refused_before_any_connection(monkeypatch):
    for role in ("adjudicator", "infrastructure", "postgres"):
        monkeypatch.setenv("PAN_CLEARANCE", role)
        assert "may launch only" in m.startup_checks()
