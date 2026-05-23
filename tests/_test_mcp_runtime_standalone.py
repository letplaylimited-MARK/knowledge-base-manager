import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
MCP_SERVER = WORKSPACE / "mcp_server.py"


async def test_server_lifecycle():
    env = {**os.environ, "PYTHONUNBUFFERED": "1"}
    proc = await asyncio.create_subprocess_exec(
        sys.executable, str(MCP_SERVER),
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        cwd=str(WORKSPACE), env=env,
    )
    results = {}

    async def _read(timeout=15):
        line = await asyncio.wait_for(proc.stdout.readline(), timeout=timeout)
        return line.decode().strip()

    async def _send(msg):
        data = json.dumps(msg, ensure_ascii=False) + "\n"
        proc.stdin.write(data.encode())
        await proc.stdin.drain()

    async def _call(method, params=None, rid=1):
        msg = {"jsonrpc": "2.0", "id": rid, "method": method}
        if params:
            msg["params"] = params
        await _send(msg)
        for _ in range(15):
            line = await _read(timeout=15)
            try:
                j = json.loads(line)
            except json.JSONDecodeError:
                results.setdefault("bad_lines", []).append(line[:100])
                continue
            if j.get("id") == rid:
                return j
            results.setdefault("extra", []).append(j)
        raise TimeoutError(f"No response for method={method}")

    # Drain startup messages
    for _ in range(3):
        try:
            line = await asyncio.wait_for(proc.stdout.readline(), timeout=1)
            j = json.loads(line.decode().strip())
            results.setdefault("startup_messages", []).append(j)
        except (asyncio.TimeoutError, json.JSONDecodeError):
            break

    # Initialize
    resp = await _call("initialize", {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test", "version": "1.0"},
    }, rid=1)
    results["server_name"] = resp["result"]["serverInfo"]["name"]

    await _send({"jsonrpc": "2.0", "method": "notifications/initialized"})

    # List tools
    resp = await _call("tools/list", rid=2)
    tools = resp["result"]["tools"]
    results["tool_count"] = len(tools)
    results["tool_names"] = sorted(t["name"] for t in tools)

    # Call tools
    calls = {}
    for idx, (tname, targs) in enumerate([
        ("get_status", {}),
        ("get_content_stats", {}),
        ("get_graph", {}),
        ("run_workflow", {"name": "multi_search", "context": json.dumps({"query": "test", "keywords": ["test"]})}),
    ], 3):
        resp = await _call("tools/call", {"name": tname, "arguments": targs}, rid=idx)
        text = resp["result"]["content"][0]["text"]
        try:
            p = json.loads(text)
            ok = not (isinstance(p, dict) and "error" in p)
        except json.JSONDecodeError:
            ok = True
        calls[tname] = "OK" if ok else f"ISSUE: {text[:150]}"
    results["calls"] = calls

    proc.stdin.close()
    try:
        await asyncio.wait_for(proc.wait(), timeout=3)
    except asyncio.TimeoutError:
        proc.kill()

    return results


async def main():
    r = await test_server_lifecycle()
    print(json.dumps(r, ensure_ascii=False, indent=2, default=str))


asyncio.run(main())
