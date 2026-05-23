

class TestMCPDefinitions:
    def test_all_tools_have_handlers(self):
        from mcp_server import TOOL_DEFINITIONS, HANDLERS
        tool_names = {t.name for t in TOOL_DEFINITIONS}
        handler_names = set(HANDLERS.keys())
        assert tool_names == handler_names

    def test_every_tool_has_input_schema(self):
        from mcp_server import TOOL_DEFINITIONS
        for t in TOOL_DEFINITIONS:
            assert "type" in t.inputSchema

    def test_healthcheck_passes(self):
        from mcp_server import _startup_healthcheck
        # Should not raise
        _startup_healthcheck()
