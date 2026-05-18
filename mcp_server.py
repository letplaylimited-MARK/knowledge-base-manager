import sys
import json
import asyncio
from pathlib import Path

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent, ListToolsResult, CallToolResult
import mcp.server.stdio

WORKSPACE = Path(__file__).resolve().parent
MEMORY_DIR = WORKSPACE / ".workbuddy" / "记忆层"
sys.path.insert(0, str(WORKSPACE / ".workbuddy" / "scripts"))
sys.path.insert(1, str(MEMORY_DIR))

server = Server("db-knowledge")

_imports = {}

def _get_module(name: str):
    if name not in _imports:
        _imports[name] = __import__(name)
    return _imports[name]


async def handle_search_all(query: str, limit: int = 5) -> str:
    try:
        sc = _get_module("search_content")
        vs = _get_module("vector_search")
        content_results = sc.search_content(query, max_results=limit)
        filename_results = sc.search_filename(query)
        vec_results = vs.search(query, top_k=limit)
        return json.dumps({
            "content_matches": content_results[:limit],
            "filename_matches": filename_results[:limit],
            "vector_matches": vec_results[:limit],
            "total_content": len(content_results),
            "total_filename": len(filename_results),
            "total_vector": len(vec_results),
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_vector_search(query: str, limit: int = 5) -> str:
    try:
        vs = _get_module("vector_search")
        results = vs.search(query, top_k=limit)
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_search_memory(query: str, context: str = None) -> str:
    try:
        mem_mod = _get_module("memoryos")
        mem = mem_mod.MemoryOS(str(MEMORY_DIR / "memory_data"))
        results = mem.search_memory(query)
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_keyword_search(keywords: list) -> str:
    try:
        sc = _get_module("search_content")
        all_results = {}
        for kw in keywords:
            results = sc.search_content(kw, max_results=20)
            all_results[kw] = results[:20]
        return json.dumps(all_results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_analyze_content(path: str) -> str:
    try:
        ca = _get_module("content_analyzer")
        analyzer = ca.ContentAnalyzer()
        file_path = Path(path)
        if not file_path.is_absolute():
            file_path = WORKSPACE / file_path
        insight = analyzer.analyze_file(file_path)
        report = analyzer.generate_report(file_path, insight)
        return json.dumps({
            "core_topic": insight.core_topic,
            "key_entities": insight.key_entities,
            "concepts": insight.concepts,
            "content_type": insight.content_type,
            "quality_level": insight.quality_level,
            "suggested_name": insight.suggested_name,
            "rename_reason": insight.rename_reason,
            "confidence": insight.confidence,
            "report": report,
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_route_content(path: str) -> str:
    try:
        sr = _get_module("smart_router")
        router = sr.SmartRouter(str(WORKSPACE))
        file_path = Path(path)
        if not file_path.is_absolute():
            file_path = WORKSPACE / file_path
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            context = {"is_file": True, "extension": file_path.suffix}
        else:
            content = path
            context = {}
        result = router.route(content, context)
        return json.dumps({
            "primary_layer": str(result["primary_layer"].name) if hasattr(result["primary_layer"], "name") else str(result["primary_layer"]),
            "secondary_layers": [str(l.name) if hasattr(l, "name") else str(l) for l in result["secondary_layers"]],
            "confidence": result["confidence"],
            "reasoning": result["reasoning"],
            "suggested_path": result["suggested_path"],
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_process_file(path: str) -> str:
    try:
        ao = _get_module("auto_organizer")
        org = ao.AutoOrganizer(str(WORKSPACE))
        file_path = Path(path)
        if not file_path.is_absolute():
            file_path = WORKSPACE / file_path
        result = org.process_and_store(file_path)
        plan = result.get("plan")
        if plan:
            return json.dumps({
                "file": str(plan.file_path),
                "suggested_name": plan.target_name,
                "target_directory": plan.target_directory,
                "should_rename": plan.should_rename,
                "should_move": plan.should_move,
                "confidence": plan.confidence,
                "reasoning": plan.reasoning,
                "executed": result.get("executed", False),
            }, ensure_ascii=False)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_get_status() -> str:
    try:
        vs = _get_module("vector_search")
        index_dir = vs.INDEX_DIR
        db_path = vs.DB_PATH
        faiss_path = vs.FAISS_PATH
        import sqlite3
        doc_count = 0
        if db_path.exists():
            try:
                conn = sqlite3.connect(str(db_path))
                doc_count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
                conn.close()
            except Exception:
                pass
        return json.dumps({
            "server": "db-knowledge",
            "workspace": str(WORKSPACE),
            "index_db_exists": db_path.exists(),
            "faiss_index_exists": faiss_path.exists(),
            "documents_indexed": doc_count,
            "has_vector_capability": vs.HAS_VECTOR,
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_rebuild_index() -> str:
    try:
        ui = _get_module("update_index")
        files = ui.update_index()
        return json.dumps({"indexed_files": len(files)}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_run_maintenance() -> str:
    try:
        mt = _get_module("maintenance_task")
        mt.main()
        return json.dumps({"status": "maintenance completed"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_run_backup() -> str:
    try:
        mt = _get_module("maintenance_task")
        mt.backup()
        return json.dumps({"status": "backup completed"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_get_graph() -> str:
    try:
        mem_mod = _get_module("memoryos")
        mem = mem_mod.MemoryOS(str(MEMORY_DIR / "memory_data"))
        summary = mem.get_memory_summary()
        return json.dumps(summary, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_watch_inbox() -> str:
    try:
        iw = _get_module("inbox_watcher")
        files = iw.scan_inbox()
        return json.dumps({"files": files, "count": len(files)}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_get_content_stats() -> str:
    try:
        import sqlite3
        vs = _get_module("vector_search")
        mem_mod = _get_module("memoryos")
        mem = mem_mod.MemoryOS(str(MEMORY_DIR / "memory_data"))
        stats = {}
        if vs.DB_PATH.exists():
            conn = sqlite3.connect(str(vs.DB_PATH))
            doc_count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
            type_counts = conn.execute("SELECT file_type, COUNT(*) FROM documents GROUP BY file_type").fetchall()
            conn.close()
            stats["indexed_documents"] = doc_count
            stats["file_type_distribution"] = dict(type_counts)
        mem_summary = mem.get_memory_summary()
        stats["memory"] = {
            "short_term": mem_summary.get("short_term_count", 0),
            "mid_term": mem_summary.get("mid_term_count", 0),
            "long_term_knowledge": mem_summary.get("long_term_knowledge", 0),
        }
        import glob
        md_files = glob.glob(str(WORKSPACE / "**" / "*.md"), recursive=True)
        py_files = glob.glob(str(WORKSPACE / "**" / "*.py"), recursive=True)
        stats["total_markdown"] = len(md_files)
        stats["total_python"] = len(py_files)
        return json.dumps(stats, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


HANDLERS = {
    "search_all": handle_search_all,
    "vector_search": handle_vector_search,
    "search_memory": handle_search_memory,
    "keyword_search": handle_keyword_search,
    "analyze_content": handle_analyze_content,
    "route_content": handle_route_content,
    "process_file": handle_process_file,
    "get_status": handle_get_status,
    "rebuild_index": handle_rebuild_index,
    "run_maintenance": handle_run_maintenance,
    "run_backup": handle_run_backup,
    "get_graph": handle_get_graph,
    "watch_inbox": handle_watch_inbox,
    "get_content_stats": handle_get_content_stats,
}


TOOL_DEFINITIONS = [
    Tool(
        name="search_all",
        description="Combined search across content, filenames, and vectors",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {"type": "integer", "description": "Max results per category", "default": 5},
            },
            "required": ["query"],
        },
    ),
        Tool(
            name="vector_search",
            description="FAISS vector semantic search",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Max results", "default": 5},
                },
                "required": ["query"],
            },
        ),
    Tool(
        name="search_memory",
        description="Search MemoryOS memory system",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "context": {"type": "string", "description": "Optional context"},
            },
            "required": ["query"],
        },
    ),
    Tool(
        name="keyword_search",
        description="Grep keyword search across workspace files",
        inputSchema={
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Keywords to search for",
                },
            },
            "required": ["keywords"],
        },
    ),
    Tool(
        name="analyze_content",
        description="Deep content analysis of a file",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path (absolute or relative to workspace)"},
            },
            "required": ["path"],
        },
    ),
    Tool(
        name="route_content",
        description="Auto-route content to appropriate knowledge layer",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path or content text"},
            },
            "required": ["path"],
        },
    ),
    Tool(
        name="process_file",
        description="Full pipeline: analyze, route, move, index",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to process"},
            },
            "required": ["path"],
        },
    ),
    Tool(
        name="get_status",
        description="Get MCP server and index system status",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="rebuild_index",
        description="Rebuild full search index",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="run_maintenance",
        description="Run complete maintenance: index, cleanup, backup",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="run_backup",
        description="Run knowledge database backup",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="get_graph",
        description="Get memory/knowledge graph status",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="watch_inbox",
        description="Scan inbox for new files",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="get_content_stats",
        description="Get workspace content statistics",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
]


@server.list_tools()
async def list_tools() -> ListToolsResult:
    return ListToolsResult(tools=TOOL_DEFINITIONS)


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    handler = HANDLERS.get(name)
    if not handler:
        return CallToolResult(content=[TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}))])
    result = await handler(**arguments)
    return CallToolResult(content=[TextContent(type="text", text=result)])


async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream,
            InitializationOptions(
                server_name="db-knowledge",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
