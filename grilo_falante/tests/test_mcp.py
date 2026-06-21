"""MCP Server tests — tool registration and dispatch verification."""

import pytest
from mcp.types import ListToolsRequest, CallToolRequest
from grilo_falante.backend.mcp.server import app


pytestmark = pytest.mark.asyncio


async def test_all_tools_registered():
    """Verifies ALL MCP tools are registered via list_tools handler."""
    req = ListToolsRequest(method="tools/list")
    result = await app.request_handlers[ListToolsRequest](req)
    ltr = result.root
    tool_names = {t.name for t in ltr.tools}

    expected_categories = {
        "grilo_status": "regime",
        "grilo_load": "regime",
        "grilo_acordar": "regime",
        "grilo_vai_dormir": "regime",
        "grilo_chat_start": "chat",
        "grilo_chat_send": "chat",
        "gepeto_create_claim": "claims",
        "gepeto_validate_claim": "claims",
        "gepeto_list_gaps": "gaps",
        "grilo_pina_propose": "pina",
        "grilo_pina_decide": "pina",
        "grilo_audit": "governance",
        "grilo_lint": "governance",
        "grilo_semantic_search": "query",
        "grilo_ilhas_list": "memory",
        "grilo_automem_status": "memory",
        "grilo_graph_lint": "gepeto",
        "grilo_learning_path": "gepeto",
        "grilo_trusted_sources": "gepeto",
        "grilo_source_propose": "gepeto",
    }

    missing = [k for k in expected_categories if k not in tool_names]
    assert not missing, f"Missing MCP tools: {missing}"


async def test_tool_input_schemas():
    """Verifies that tools have valid input schemas."""
    req = ListToolsRequest(method="tools/list")
    result = await app.request_handlers[ListToolsRequest](req)
    tools = result.root.tools

    for tool in tools:
        schema = tool.inputSchema
        assert isinstance(schema, dict), f"{tool.name}: inputSchema not a dict"
        assert "type" in schema, f"{tool.name}: inputSchema missing 'type'"
        assert schema["type"] == "object", f"{tool.name}: inputSchema.type != object"
        assert isinstance(schema.get("properties", {}), dict), (
            f"{tool.name}: properties not a dict"
        )
        required = schema.get("required", [])
        assert isinstance(required, list), f"{tool.name}: required not a list"
        for req_field in required:
            assert req_field in schema["properties"], (
                f"{tool.name}: required field '{req_field}' not in properties"
            )


async def test_gepeto_tools_specific():
    """Verifies the 4 GePeTo-ported tools have correct metadata."""
    req = ListToolsRequest(method="tools/list")
    result = await app.request_handlers[ListToolsRequest](req)
    tools = {t.name: t for t in result.root.tools}

    gl = tools.get("grilo_graph_lint")
    assert gl is not None, "grilo_graph_lint not found"
    assert "GePeTo" in gl.description
    assert gl.inputSchema["properties"].get("claim_keys", {}).get("type") == "array"

    lp = tools.get("grilo_learning_path")
    assert lp is not None, "grilo_learning_path not found"
    assert "GePeTo" in lp.description
    assert "topic" in lp.inputSchema.get("required", [])

    ts = tools.get("grilo_trusted_sources")
    assert ts is not None, "grilo_trusted_sources not found"
    assert "GePeTo" in ts.description

    sp = tools.get("grilo_source_propose")
    assert sp is not None, "grilo_source_propose not found"
    assert "GePeTo" in sp.description
    assert "source_key" in sp.inputSchema.get("required", [])


async def test_call_tool_dispatch_error():
    """Verifies call_tool returns error for invalid tool name."""
    req = CallToolRequest(
        method="tools/call",
        params={"name": "nonexistent_tool", "arguments": {}},
    )
    result = await app.request_handlers[CallToolRequest](req)
    ct = result.root
    text = " ".join(c.text for c in ct.content)
    assert "error" in text.lower() or "unknown" in text.lower(), (
        f"Expected error text: {text}"
    )


async def test_call_tool_status_works_without_db():
    """grilo_status works without DB (uses in-memory state)."""
    req = CallToolRequest(
        method="tools/call",
        params={"name": "grilo_status", "arguments": {}},
    )
    result = await app.request_handlers[CallToolRequest](req)
    ct = result.root
    text = " ".join(c.text for c in ct.content)
    assert "state" in text and "active" in text, f"Expected status data: {text}"


async def test_call_tool_grilo_lint():
    """grilo_lint works (no DB needed)."""
    req = CallToolRequest(
        method="tools/call",
        params={"name": "grilo_lint", "arguments": {"text": "This is obviously correct"}},
    )
    result = await app.request_handlers[CallToolRequest](req)
    ct = result.root
    assert not ct.isError, f"grilo_lint failed: {ct.content}"
    text = " ".join(c.text for c in ct.content)
    assert "blocking" in text.lower() or "reject" in text.lower() or "issue" in text.lower()


async def test_call_tool_grilo_generate_gfid():
    """grilo_generate_gfid works without DB."""
    req = CallToolRequest(
        method="tools/call",
        params={
            "name": "grilo_generate_gfid",
            "arguments": {"content": "test content", "gmif_level": "M1"},
        },
    )
    result = await app.request_handlers[CallToolRequest](req)
    ct = result.root
    assert not ct.isError, f"grilo_generate_gfid failed: {ct.content}"
    text = " ".join(c.text for c in ct.content)
    assert "GF-" in text


async def test_call_tool_grilo_classify_gmif():
    """grilo_classify_gmif works without DB."""
    req = CallToolRequest(
        method="tools/call",
        params={
            "name": "grilo_classify_gmif",
            "arguments": {"claim_text": "The study demonstrates a clear correlation"},
        },
    )
    result = await app.request_handlers[CallToolRequest](req)
    ct = result.root
    assert not ct.isError, f"grilo_classify_gmif failed: {ct.content}"
    text = " ".join(c.text for c in ct.content)
    assert any(level in text for level in ["VERIFIED", "DERIVED", "CONCLUSION", "PRIMARY",
                                            "INTERPRETATION", "CONFLICTED"])


async def test_call_tool_missing_required_arg():
    """Verifies call_tool returns error when required arguments are missing."""
    req = CallToolRequest(
        method="tools/call",
        params={
            "name": "grilo_acordar",
            "arguments": {},
        },
    )
    result = await app.request_handlers[CallToolRequest](req)
    ct = result.root
    assert ct.isError
