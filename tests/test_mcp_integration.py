import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path

import pytest

WORKSPACE = Path(__file__).resolve().parent.parent
MCP_SERVER = WORKSPACE / "mcp_server.py"


async def _start_server():
    """Start MCP server subprocess, return (proc, tool_call, close, call)."""
    env = {**os.environ, "PYTHONUNBUFFERED": "1"}
    proc = await asyncio.create_subprocess_exec(
        sys.executable, str(MCP_SERVER),
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=str(WORKSPACE), env=env,
    )

    next_rid = 1

    async def _read(timeout=10):
        return (await asyncio.wait_for(proc.stdout.readline(), timeout)).decode().strip()

    async def _send(msg):
        data = json.dumps(msg, ensure_ascii=False) + "\n"
        proc.stdin.write(data.encode())
        await proc.stdin.drain()

    async def _call(method, params=None, read_timeout=10):
        nonlocal next_rid
        rid = next_rid
        next_rid += 1
        msg = {"jsonrpc": "2.0", "id": rid, "method": method}
        if params:
            msg["params"] = params
        await _send(msg)
        for _ in range(60):
            line = await _read(timeout=read_timeout)
            try:
                j = json.loads(line)
            except json.JSONDecodeError:
                continue
            if j.get("id") == rid:
                return j
        raise TimeoutError(f"No response for method={method}")

    async def _tool_call(name, args=None, read_timeout=10):
        resp = await _call("tools/call", {"name": name, "arguments": args or {}}, read_timeout=read_timeout)
        text = resp["result"]["content"][0]["text"]
        return json.loads(text)

    async def _close():
        proc.stdin.close()
        try:
            await asyncio.wait_for(proc.wait(), timeout=3)
        except asyncio.TimeoutError:
            proc.kill()

    # initialize (longer timeout — server runs healthcheck at startup)
    resp = await _call("initialize", {
        "protocolVersion": "2024-11-05", "capabilities": {},
        "clientInfo": {"name": "test", "version": "1.0"},
    }, read_timeout=60)
    assert resp["result"]["serverInfo"]["name"] == "db-knowledge"
    await _send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    return proc, _tool_call, _close, _call


@pytest.mark.asyncio
async def test_mcp_tools_list():
    proc, tool_call, close, call = await _start_server()
    try:
        resp = await call("tools/list")
        assert len(resp["result"]["tools"]) == 20
    finally:
        await close()


@pytest.mark.asyncio
async def test_mcp_quick_tools():
    proc, tool_call, close, _ = await _start_server()
    try:
        r = await tool_call("get_status")
        assert r["server"] == "db-knowledge"

        r = await tool_call("watch_inbox")
        assert "files" in r

        r = await tool_call("enhanced_scan_inbox")
        assert "files" in r

        r = await tool_call("get_graph")
        assert isinstance(r, dict)

        r = await tool_call("get_content_stats")
        assert isinstance(r, dict)

        # run_maintenance/run_backup skipped — they take minutes on real workspace
    finally:
        await close()


@pytest.mark.asyncio
async def test_mcp_search_tools():
    proc, tool_call, close, _ = await _start_server()
    try:
        r = await tool_call("vector_search", {"query": "test"})
        assert isinstance(r, (list, dict))

        r = await tool_call("search_memory", {"query": "test"})
        assert isinstance(r, (list, dict))

        r = await tool_call("keyword_search", {"keywords": ["test"]})
        assert isinstance(r, dict)

        r = await tool_call("search_all", {"query": "test"})
        assert "content_matches" in r
        assert "vector_matches" in r
    finally:
        await close()


@pytest.mark.asyncio
async def test_mcp_content_tools():
    proc, tool_call, close, _ = await _start_server()
    try:
        r = await tool_call("route_content", {"path": "some sample content text"})
        assert "primary_layer" in r
        assert "confidence" in r

        r = await tool_call("analyze_project_relationships")
        assert isinstance(r, dict)
    finally:
        await close()


@pytest.mark.asyncio
async def test_mcp_error_paths():
    proc, tool_call, close, _ = await _start_server()
    try:
        r = await tool_call("extract_docx_text", {"path": "/nonexistent/file.docx"})
        assert "Error" in r.get("text", ""), f"unexpected result: {r}"

        # analyze_content/process_file are resilient — may return valid result even for bad path
        r = await tool_call("analyze_content", {"path": "/nonexistent/file.md"})
        assert isinstance(r, dict)

        r = await tool_call("process_file", {"path": "/nonexistent/file.md"})
        assert isinstance(r, dict), f"unexpected: {r}"

        r = await tool_call("run_file_pipeline", {"path": "/nonexistent/file.md"})
        assert isinstance(r, dict), f"unexpected: {r}"

        r = await tool_call("project_decision_workflow", {"path": "/nonexistent/file.md"})
        assert isinstance(r, dict), f"unexpected: {r}"

        r = await tool_call("run_workflow", {"name": "nonexistent"})
        assert "error" in r

        r = await tool_call("keyword_search", {"keywords": []})
        assert isinstance(r, dict)
    finally:
        await close()


@pytest.mark.asyncio
async def test_mcp_workflows():
    proc, tool_call, close, _ = await _start_server()
    try:
        r = await tool_call("run_workflow", {"name": "multi_search"})
        assert "workflow" in r, f"unexpected: {r}"

        r = await tool_call("run_workflow", {"name": "search_and_analyze"})
        assert "workflow" in r, f"unexpected: {r}"
    finally:
        await close()


@pytest.mark.asyncio
async def test_mcp_rebuild_index():
    proc, tool_call, close, _ = await _start_server()
    try:
        r = await tool_call("rebuild_index", read_timeout=60)
        assert "indexed_files" in r
    finally:
        await close()
