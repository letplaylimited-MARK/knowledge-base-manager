"""Synchronous tests for MCP server definitions — no asyncio import conflict."""


class TestToolDefinitions:
    def test_all_tool_names_match_handlers(self):
        from mcp_server import TOOL_DEFINITIONS, HANDLERS
        tool_names = {t.name for t in TOOL_DEFINITIONS}
        handler_names = set(HANDLERS.keys())
        assert tool_names == handler_names

    def test_every_tool_has_input_schema(self):
        from mcp_server import TOOL_DEFINITIONS
        for t in TOOL_DEFINITIONS:
            assert "type" in t.inputSchema

    def test_required_params_have_default_in_handler_or_required_schema(self):
        from mcp_server import TOOL_DEFINITIONS, HANDLERS
        import inspect
        for t in TOOL_DEFINITIONS:
            handler = HANDLERS[t.name]
            sig = inspect.signature(handler)
            if "required" in t.inputSchema:
                for req in t.inputSchema["required"]:
                    assert req in sig.parameters, f"{t.name}: required param '{req}' not in handler"

    def test_healthcheck_passes(self):
        from mcp_server import _startup_healthcheck
        _startup_healthcheck()
