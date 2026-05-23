import sys
import json
import asyncio
import logging
from pathlib import Path

from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent, ListToolsResult, CallToolResult
import mcp.server.stdio

WORKSPACE = Path(__file__).resolve().parent
MEMORY_DIR = WORKSPACE / ".workbuddy" / "记忆层"
sys.path.insert(0, str(WORKSPACE / ".workbuddy" / "scripts"))
sys.path.insert(1, str(MEMORY_DIR))
import workflow_engine as _we_mod

logging.basicConfig(level=logging.INFO, format="%(name)s %(levelname)s %(message)s")
logger = logging.getLogger("mcp-server")

server = Server("db-knowledge")


async def handle_search_all(query: str, limit: int = 5) -> str:
    try:
        from search_content import search_content, search_filename
        from vector_search import search as vs_search
        content_results = search_content(query, max_results=limit)
        filename_results = search_filename(query)
        vec_results = vs_search(query, top_k=limit)
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


async def handle_vector_search(query: str, limit: int = 5, **kwargs) -> str:
    try:
        from vector_search import search as vs_search
        results = vs_search(query, top_k=limit)
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_search_memory(query: str, context: str = None) -> str:
    try:
        from memoryos import MemoryOS
        mem = MemoryOS(str(MEMORY_DIR / "memory_data"))
        results = mem.search_memory(query)
        return json.dumps(results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_keyword_search(keywords: list, **kwargs) -> str:
    try:
        from search_content import search_content
        all_results = {}
        for kw in keywords:
            results = search_content(kw, max_results=20)
            all_results[kw] = results[:20]
        return json.dumps(all_results, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_analyze_content(path: str) -> str:
    try:
        from content_analyzer import ContentAnalyzer
        analyzer = ContentAnalyzer()
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
        from smart_router import SmartRouter
        router = SmartRouter(str(WORKSPACE))
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
            "secondary_layers": [str(ly.name) if hasattr(ly, "name") else str(ly) for ly in result["secondary_layers"]],
            "confidence": result["confidence"],
            "reasoning": result["reasoning"],
            "suggested_path": result["suggested_path"],
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_process_file(path: str) -> str:
    try:
        from auto_organizer import AutoOrganizer
        org = AutoOrganizer(str(WORKSPACE))
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
        import vector_search as _vs
        import sqlite3
        doc_count = 0
        if _vs.DB_PATH.exists():
            try:
                with sqlite3.connect(str(_vs.DB_PATH)) as conn:
                    doc_count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
            except Exception:
                pass
        return json.dumps({
            "server": "db-knowledge",
            "workspace": str(WORKSPACE),
            "index_db_exists": _vs.DB_PATH.exists(),
            "faiss_index_exists": _vs.FAISS_PATH.exists(),
            "documents_indexed": doc_count,
            "has_vector_capability": _vs.HAS_VECTOR,
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_rebuild_index() -> str:
    try:
        from update_index import update_index
        files = update_index()
        return json.dumps({"indexed_files": len(files)}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_run_maintenance() -> str:
    try:
        import maintenance_task
        maintenance_task.main()
        return json.dumps({"status": "maintenance completed"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_run_backup() -> str:
    try:
        import maintenance_task
        maintenance_task.backup()
        return json.dumps({"status": "backup completed"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_get_graph() -> str:
    try:
        from memoryos import MemoryOS
        mem = MemoryOS(str(MEMORY_DIR / "memory_data"))
        summary = mem.get_memory_summary()
        return json.dumps(summary, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_watch_inbox() -> str:
    try:
        from inbox_watcher import scan_inbox
        files = scan_inbox()
        return json.dumps({"files": files, "count": len(files)}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_get_content_stats() -> str:
    try:
        import sqlite3
        import vector_search as _vs
        from memoryos import MemoryOS
        mem = MemoryOS(str(MEMORY_DIR / "memory_data"))
        stats = {}
        if _vs.DB_PATH.exists():
            with sqlite3.connect(str(_vs.DB_PATH)) as conn:
                doc_count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
                type_counts = conn.execute("SELECT file_type, COUNT(*) FROM documents GROUP BY file_type").fetchall()
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


async def handle_enhanced_scan_inbox() -> str:
    try:
        from enhanced_inbox_watcher import scan_inbox
        files = scan_inbox()
        return json.dumps({"files": files, "count": len(files)}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_extract_docx_text(path: str) -> str:
    try:
        from extract_docx import extract_docx
        file_path = Path(path)
        if not file_path.is_absolute():
            file_path = WORKSPACE / file_path
        text = extract_docx(str(file_path))
        return json.dumps({"path": str(file_path), "text": text}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_analyze_project_relationships(path: str = None) -> str:
    try:
        from project_relationship_manager import ProjectRelationshipManager
        mgr = ProjectRelationshipManager(str(WORKSPACE))
        if path:
            target_path = Path(path)
            if not target_path.is_absolute():
                target_path = WORKSPACE / target_path
            content = target_path.read_text(encoding="utf-8", errors="ignore")
            sig = mgr.analyze_file_signature(str(target_path), content)
            mgr.files[str(target_path)] = sig
        else:
            import glob
            scan_patterns = ["**/*.md", "**/*.py", "**/*.txt", "**/*.json", "**/*.yaml", "**/*.yml"]
            all_files = []
            for pat in scan_patterns:
                all_files.extend(glob.glob(str(WORKSPACE / pat), recursive=True))
            all_files = list(set(all_files))[:200]
            for fp in all_files:
                try:
                    content = Path(fp).read_text(encoding="utf-8", errors="ignore")
                    sig = mgr.analyze_file_signature(fp, content)
                    mgr.files[fp] = sig
                except Exception:
                    pass
        projects = mgr.identify_project_boundaries(list(mgr.files.values()))
        mgr.projects = {p.candidate_id: p for p in projects}
        _ = mgr.discover_cross_project_relations()
        report = mgr.generate_comprehensive_report()
        return json.dumps(report, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_run_file_pipeline(path: str) -> str:
    try:
        from file_processing_pipeline import FileProcessingPipeline
        pipeline = FileProcessingPipeline(str(WORKSPACE))
        file_path = Path(path)
        if not file_path.is_absolute():
            file_path = WORKSPACE / file_path
        result = pipeline.process_file(file_path)
        report = pipeline.generate_processing_report(result)
        return json.dumps({
            "core_topic": result.understanding.core_topic,
            "content_type": result.understanding.content_type,
            "quality_level": result.understanding.quality_level,
            "coexistence_type": result.coexistence.coexistence_type,
            "should_rename": result.naming.should_rename,
            "suggested_name": result.naming.suggested_name,
            "confidence": result.naming.confidence,
            "final_recommendation": result.final_recommendation,
            "full_report": report,
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def handle_project_decision_workflow(path: str) -> str:
    try:
        from project_decision_workflow import ProjectDecisionWorkflow
        workflow = ProjectDecisionWorkflow(str(WORKSPACE))
        file_path = Path(path)
        if not file_path.is_absolute():
            file_path = WORKSPACE / file_path
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        result = workflow.process_new_file(str(file_path), content)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


# Predefined workflow engine setup
_workflow_engine = _we_mod.WorkflowEngine()

async def _wf_vector(**kwargs):
    raw = await handle_vector_search(
        query=kwargs.get("query", ""), limit=kwargs.get("limit", 5))
    return json.loads(raw)

async def _wf_keyword(**kwargs):
    raw = await handle_keyword_search(
        keywords=kwargs.get("keywords", []))
    return json.loads(raw)

async def _wf_search(**kwargs):
    raw = await handle_search_all(
        query=kwargs.get("query", ""), limit=kwargs.get("limit", 5))
    return json.loads(raw)

_workflow_engine.define("multi_search", [
    _we_mod.Step("vector", _wf_vector),
    _we_mod.Step("keyword", _wf_keyword),
])
_workflow_engine.define("search_and_analyze", [
    _we_mod.Step("search", _wf_search),
    _we_mod.Step("keyword", _wf_keyword),
])


async def handle_run_workflow(name: str, context: str = None) -> str:
    try:
        ctx = json.loads(context) if context else {}
        result = await _workflow_engine.run(name, ctx)
        return json.dumps(result, ensure_ascii=False, default=str)
    except ValueError as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": f"Workflow execution failed: {e}"}, ensure_ascii=False)


HANDLERS = {
    "run_workflow": handle_run_workflow,
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
    "enhanced_scan_inbox": handle_enhanced_scan_inbox,
    "extract_docx_text": handle_extract_docx_text,
    "analyze_project_relationships": handle_analyze_project_relationships,
    "run_file_pipeline": handle_run_file_pipeline,
    "project_decision_workflow": handle_project_decision_workflow,
}


TOOL_DEFINITIONS = [
    Tool(
        name="run_workflow",
        description="Execute a multi-step workflow (analyze_file, search_and_summarize)",
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Workflow name"},
                "context": {"type": "string", "description": "JSON context dict"},
            },
            "required": ["name"],
        },
    ),
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
    Tool(
        name="enhanced_scan_inbox",
        description="Enhanced inbox scan with keyword classification",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    ),
    Tool(
        name="extract_docx_text",
        description="Extract text from DOCX file",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to .docx file"},
            },
            "required": ["path"],
        },
    ),
    Tool(
        name="analyze_project_relationships",
        description="Analyze project relationships and discover cross-project relations",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Specific path to analyze, or empty for workspace-wide"},
            },
        },
    ),
    Tool(
        name="run_file_pipeline",
        description="Run full file processing pipeline (read, understand, analyze, name)",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to process"},
            },
            "required": ["path"],
        },
    ),
    Tool(
        name="project_decision_workflow",
        description="Run project decision workflow for new files",
        inputSchema={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path to make decision on"},
            },
            "required": ["path"],
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

def _startup_healthcheck():
    issues = []
    MODULES_TO_CHECK = [
        "search_content", "vector_search", "memoryos", "content_analyzer",
        "smart_router", "auto_organizer", "maintenance_task", "inbox_watcher",
        "enhanced_inbox_watcher", "extract_docx", "project_relationship_manager",
        "file_processing_pipeline", "project_decision_workflow",
    ]
    for mod_name in MODULES_TO_CHECK:
        try:
            __import__(mod_name)
        except ImportError as e:
            issues.append(f"  [FAIL] {mod_name}: {e}")
    if not MEMORY_DIR.exists():
        issues.append(f"  [WARN] Memory dir not found: {MEMORY_DIR}")
    index_dir = WORKSPACE / ".workbuddy" / "index"
    if not (index_dir / "search_index.db").exists():
        issues.append("  [WARN] No search_index.db found - run rebuild_index first")
    try:
        import vector_search as _vs
        if not _vs.FAISS_PATH.exists():
            n = _vs.build_faiss_index()
            issues.append(f"  [AUTO] FAISS index missing, rebuilt: {n} vectors")
    except Exception:
        pass
    logger.info(f"Healthcheck: {len(MODULES_TO_CHECK)} modules checked")
    if issues:
        logger.warning(f"Issues ({len(issues)}):\n" + "\n".join(issues))
    else:
        logger.info("All checks passed")


if __name__ == "__main__":
    _startup_healthcheck()
    asyncio.run(main())
