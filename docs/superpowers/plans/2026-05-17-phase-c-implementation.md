# Phase C: AI Agent Backend — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the existing knowledge management tool into an AI agent backend with MCP access, multi-LLM support, and OpenCode integration.

**Architecture:** Layer 1 (MCP Server) wraps all existing functions as MCP tools via stdio transport. Layer 2 (ModelAdapter + AgentOrchestrator) reads `.workbuddy/AI协作体系/` YAML+markdown configs to provide multi-LLM agent execution. Layer 3 (OpenCode configs) registers everything with OpenCode.

**Tech Stack:** MCP Python SDK, Python 3.14, asyncio, OpenAI SDK, Anthropic SDK, ZhipuAI SDK, Yi SDK

**Execution order:** Strictly sequential — P0 → P1 → P2-1 → P2-2 → P2-3 → P3

---

### Task P0: Security Fixes

**Files:**
- Modify: `.workbuddy/scripts/maintenance_task.py:24`
- Modify: `app.py:119`
- Modify: `.workbuddy/scripts/auto_organizer.py:271`
- Modify: `.workbuddy/scripts/update_index.py:42`

- [ ] **P0-1: Fix os.system → subprocess.run in maintenance_task.py**

  Current (line 24):
  ```text
  os.system(f'python "{update_script}"')
  ```

  Replace with:
  ```text
  import subprocess
  subprocess.run([sys.executable, str(update_script)], check=True)
  ```

  Also add `import subprocess` at the top.

- [ ] **P0-2: Fix 0.0.0.0 → 127.0.0.1 in app.py**

  Current (line 119):
  ```text
  app.run(host="0.0.0.0", port=args.port, debug=not args.daemon)
  ```

  Replace with:
  ```text
  app.run(host="127.0.0.1", port=args.port, debug=not args.daemon)
  ```

- [ ] **P0-3: Fix copy2 → move in auto_organizer.py**

  Current:
  ```text
  import shutil
  shutil.copy2(plan.file_path, target_path)
  ```

  Replace with:
  ```text
  import shutil
  shutil.move(str(plan.file_path), str(target_path))
  ```

- [ ] **P0-4: Fix bare except in update_index.py**

  Current (line 42):
  ```text
  except:
      return {"size": 0, "tags": []}
  ```

  Replace with:
  ```text
  except Exception:
      return {"size": 0, "tags": []}
  ```

- [ ] **P0-5: Verify all 4 fixes**

  Run:
  ```bash
  python -c "exec(open('.workbuddy/scripts/maintenance_task.py').read().replace('os.system', 'PASS')); print('maintenance_task OK')"
  python -c "import ast; ast.parse(open('app.py').read()); print('app.py OK')"
  python -c "exec(open('.workbuddy/scripts/auto_organizer.py').read().replace('shutil.copy2', 'PASS')); print('auto_organizer OK')"
  python -c "ast.parse(open('.workbuddy/scripts/update_index.py').read()); print('update_index OK')"
  ```

  Expected: All 4 print OK

---

### Task P1: MCP Server

**Files:**
- Create: `mcp_server.py`

- [ ] **P1-1: Create mcp_server.py — imports and server setup**

  ```text
  import sys
  import json
  import asyncio
  from pathlib import Path
  from typing import Any
  from mcp.server import Server, NotificationOptions
  from mcp.server.models import InitializationOptions
  from mcp.types import Tool, TextContent, ListToolsResult, CallToolResult
  import mcp.server.stdio

  WORKSPACE = Path(__file__).resolve().parent
  sys.path.insert(0, str(WORKSPACE / ".workbuddy" / "scripts"))

  server = Server("db-knowledge")
  ```

- [ ] **P1-2: Add tool definitions — 15 tools in `list_tools`**

  ```text
  TOOLS: list[Tool] = [
      Tool(name="search_all", description="Full-text + vector + memory combined search",
           inputSchema={"type": "object", "properties": {
               "query": {"type": "string", "description": "Search query"},
               "limit": {"type": "integer", "description": "Max results", "default": 5}}}),
      Tool(name="vector_search", description="FAISS semantic vector search",
           inputSchema={"type": "object", "properties": {
               "query": {"type": "string"}, "limit": {"type": "integer", "default": 5},
               "search_path": {"type": "string", "default": None}}}),
      Tool(name="search_memory", description="Search MemoryOS memory layer",
           inputSchema={"type": "object", "properties": {
               "query": {"type": "string"}, "context": {"type": "string", "default": None}}}),
      Tool(name="keyword_search", description="Search by keywords via grep",
           inputSchema={"type": "object", "properties": {
               "keywords": {"type": "array", "items": {"type": "string"}}}}),
      Tool(name="analyze_content", description="Analyze file: tags + entities + summary",
           inputSchema={"type": "object", "properties": {
               "path": {"type": "string"}}}),
      Tool(name="route_content", description="Auto-route file to category",
           inputSchema={"type": "object", "properties": {
               "path": {"type": "string"}}}),
      Tool(name="process_file", description="Full pipeline: analyze → route → index → memory",
           inputSchema={"type": "object", "properties": {
               "path": {"type": "string"}}}),
      Tool(name="get_status", description="System status overview",
           inputSchema={"type": "object", "properties": {}}),
      Tool(name="rebuild_index", description="Rebuild FAISS + SQLite index",
           inputSchema={"type": "object", "properties": {}}),
      Tool(name="run_maintenance", description="Run full maintenance: index + memory checkpoint",
           inputSchema={"type": "object", "properties": {}}),
      Tool(name="run_backup", description="Backup workspace",
           inputSchema={"type": "object", "properties": {}}),
      Tool(name="get_graph", description="Get knowledge graph index",
           inputSchema={"type": "object", "properties": {}}),
      Tool(name="watch_inbox", description="Scan inbox for new files",
           inputSchema={"type": "object", "properties": {}}),
      Tool(name="get_content_stats", description="Content statistics",
           inputSchema={"type": "object", "properties": {}}),
  ]
  ```

- [ ] **P1-3: Implement lazy imports helper**

  ```text
  _imports = {}

  def _get_module(name: str):
      if name not in _imports:
          _imports[name] = __import__(name.replace(".", " "))
      return _imports[name]
  ```

- [ ] **P1-4: Implement search tool handlers**

  ```text
  async def _handle_search_all(query: str, limit: int = 5) -> str:
      try:
          vs = _get_module("vector_search")
          results = vs.search(query, limit=limit)
          return json.dumps(results, ensure_ascii=False, indent=2)
      except Exception as e:
          return json.dumps({"error": str(e)})

  async def _handle_vector_search(query: str, limit: int = 5, search_path: str = None) -> str:
      try:
          vs = _get_module("vector_search")
          results = vs.search(query, limit=limit, search_path=search_path)
          return json.dumps(results, ensure_ascii=False, indent=2)
      except Exception as e:
          return json.dumps({"error": str(e)})

  async def _handle_search_memory(query: str, context: str = None) -> str:
      try:
          mo = _get_module("memoryos")
          results = mo.search_memory(query, context)
          return json.dumps(results, ensure_ascii=False, indent=2)
      except Exception as e:
          return json.dumps({"error": str(e)})

  async def _handle_keyword_search(keywords: list[str]) -> str:
      try:
          sc = _get_module("search_content")
          results = []
          for kw in keywords:
              results.extend(sc.search_files(kw))
          return json.dumps(results, ensure_ascii=False, indent=2)
      except Exception as e:
          return json.dumps({"error": str(e)})
  ```

- [ ] **P1-5: Implement content tool handlers**

  ```text
  async def _handle_analyze_content(path: str) -> str:
      try:
          ca = _get_module("content_analyzer")
          result = ca.analyze(Path(path))
          return json.dumps(result, ensure_ascii=False, indent=2)
      except Exception as e:
          return json.dumps({"error": str(e)})

  async def _handle_route_content(path: str) -> str:
      try:
          sr = _get_module("smart_router")
          result = sr.route(Path(path))
          return json.dumps(result, ensure_ascii=False, indent=2)
      except Exception as e:
          return json.dumps({"error": str(e)})

  async def _handle_process_file(path: str) -> str:
      try:
          ao = _get_module("auto_organizer")
          result = ao.process_and_store(Path(path))
          return json.dumps(result, ensure_ascii=False, indent=2)
      except Exception as e:
          return json.dumps({"error": str(e)})

  async def _handle_get_content_stats() -> str:
      try:
          ca = _get_module("content_analyzer")
          stats = {"total_files": 0, "categories": {}}
          return json.dumps(stats, ensure_ascii=False, indent=2)
      except Exception as e:
          return json.dumps({"error": str(e)})
  ```

- [ ] **P1-6: Implement system tool handlers**

  ```text
  async def _handle_get_status() -> str:
      info = {
          "workspace": str(WORKSPACE),
          "python": sys.version,
          "scripts": [p.name for p in (WORKSPACE / ".workbuddy/scripts").iterdir()
                      if p.suffix == ".py"],
      }
      return json.dumps(info, ensure_ascii=False, indent=2)

  async def _handle_rebuild_index() -> str:
      try:
          ui = _get_module("update_index")
          ui.update_index()
          return json.dumps({"status": "ok", "message": "Index rebuilt"})
      except Exception as e:
          return json.dumps({"error": str(e)})

  async def _handle_run_maintenance() -> str:
      try:
          mt = _get_module("maintenance_task")
          mt.run_maintenance()
          return json.dumps({"status": "ok"})
      except Exception as e:
          return json.dumps({"error": str(e)})

  async def _handle_run_backup() -> str:
      try:
          import subprocess
          bp = WORKSPACE / ".workbuddy" / "scripts" / "backup.py"
          subprocess.run([sys.executable, str(bp)], check=True)
          return json.dumps({"status": "ok", "message": "Backup complete"})
      except Exception as e:
          return json.dumps({"error": str(e)})

  async def _handle_get_graph() -> str:
      graph_path = WORKSPACE / "05-知识沉淀" / "wiki" / "index.md"
      if graph_path.exists():
          return json.dumps({"graph": graph_path.read_text(encoding="utf-8")})
      return json.dumps({"error": "Graph index not found"})

  async def _handle_watch_inbox() -> str:
      inbox = WORKSPACE / "01-收件箱"
      files = [str(p) for p in inbox.iterdir() if p.is_file()]
      return json.dumps({"files": files}, ensure_ascii=False, indent=2)
  ```

- [ ] **P1-7: Wire up handlers to `call_tool` with routing dict**

  ```text
  HANDLERS = {
      "search_all": _handle_search_all,
      "vector_search": _handle_vector_search,
      "search_memory": _handle_search_memory,
      "keyword_search": _handle_keyword_search,
      "analyze_content": _handle_analyze_content,
      "route_content": _handle_route_content,
      "process_file": _handle_process_file,
      "get_status": _handle_get_status,
      "rebuild_index": _handle_rebuild_index,
      "run_maintenance": _handle_run_maintenance,
      "run_backup": _handle_run_backup,
      "get_graph": _handle_get_graph,
      "watch_inbox": _handle_watch_inbox,
      "get_content_stats": _handle_get_content_stats,
  }

  @server.list_tools()
  async def list_tools() -> ListToolsResult:
      return ListToolsResult(tools=TOOLS)

  @server.call_tool()
  async def call_tool(name: str, arguments: dict) -> CallToolResult:
      handler = HANDLERS.get(name)
      if not handler:
          return CallToolResult(isError=True, content=[TextContent(type="text", text=f"Unknown tool: {name}")])
      try:
          result = await handler(**arguments)
          return CallToolResult(content=[TextContent(type="text", text=str(result))])
      except Exception as e:
          return CallToolResult(isError=True, content=[TextContent(type="text", text=str(e))])
  ```

- [ ] **P1-8: Add main entry point**

  ```text
  async def main():
      async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
          await server.run(
              read_stream,
              write_stream,
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
  ```

- [ ] **P1-9: Verify MCP server starts**

  Run:
  ```bash
  echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python mcp_server.py 2>&1 | Select-String -Pattern "result" -SimpleMatch
  ```

  Expected: Prints JSON with list of 14+ tools (stdio response may need proper MCP framing)

---

### Task P2-1: ModelAdapter

**Files:**
- Create: `.workbuddy/scripts/model_adapter.py`

- [ ] **P2-1-1: Create model_adapter.py — base + YAML loading**

  ```text
  import os
  import sys
  import json
  from pathlib import Path
  from typing import Any

  CONFIG_DIR = Path(__file__).resolve().parent.parent / "AI协作体系" / "模型配置"


  class ModelAdapter:
      def __init__(self, config_dir: Path = CONFIG_DIR):
          self.models: dict[str, dict] = {}
          self._clients: dict[str, Any] = {}
          self._load_configs(config_dir)

      def _load_configs(self, config_dir: Path):
          if not config_dir.exists():
              return
          import yaml
          for f in sorted(config_dir.glob("*.yaml")):
              try:
                  with open(f, encoding="utf-8") as fh:
                      cfg = yaml.safe_load(fh)
                  key = cfg.get("model_name", f.stem).lower().replace(" ", "-")
                  self.models[key] = cfg
              except Exception:
                  pass
  ```

- [ ] **P2-1-2: Add client lazy-initialization per provider**

  ```text
      def _get_client(self, model_key: str) -> Any:
          if model_key in self._clients:
              return self._clients[model_key]
          cfg = self.models.get(model_key)
          if not cfg:
              raise ValueError(f"Unknown model: {model_key}")
          provider = cfg.get("provider", "")
          api_key = os.environ.get(cfg.get("api_key", "").strip("${} "))
          if provider == "openai":
              from openai import OpenAI
              self._clients[model_key] = OpenAI(api_key=api_key)
          elif provider == "anthropic":
              from anthropic import Anthropic
              self._clients[model_key] = Anthropic(api_key=api_key)
          elif provider == "zhipu":
              from zhipuai import ZhipuAI
              self._clients[model_key] = ZhipuAI(api_key=api_key)
          elif provider == "yi":
              from openai import OpenAI
              base = cfg.get("api_base", "https://api.lingyiwanwu.com/v1")
              self._clients[model_key] = OpenAI(api_key=api_key, base_url=base)
          else:
              raise ValueError(f"Unsupported provider: {provider}")
          return self._clients[model_key]
  ```

- [ ] **P2-1-3: Add chat and embed methods**

  ```text
      def chat(self, model_key: str, messages: list, stream: bool = False,
               temperature: float = None, max_tokens: int = None) -> str:
          cfg = self.models.get(model_key)
          if not cfg:
              raise ValueError(f"Unknown model: {model_key}")
          client = self._get_client(model_key)
          provider = cfg.get("provider", "")
          model_version = cfg.get("model_version", "")

          if provider == "openai":
              resp = client.chat.completions.create(
                  model=model_version, messages=messages,
                  temperature=temperature or cfg.get("temperature", 0.7),
                  max_tokens=max_tokens or cfg.get("max_tokens", 4096),
                  stream=stream)
              return resp.choices[0].message.content if not stream else resp
          elif provider == "anthropic":
              system = None
              msgs = messages
              if messages and messages[0].get("role") == "system":
                  system = messages[0]["content"]
                  msgs = messages[1:]
              resp = client.messages.create(
                  model=model_version, messages=msgs,
                  system=system, max_tokens=max_tokens or cfg.get("max_tokens", 4096),
                  temperature=temperature or cfg.get("temperature", 0.7))
              return resp.content[0].text
          elif provider in ("zhipu", "yi"):
              resp = client.chat.completions.create(
                  model=model_version, messages=messages,
                  temperature=temperature or cfg.get("temperature", 0.7))
              return resp.choices[0].message.content
          return ""

      def embed(self, text: str, model_key: str = None) -> list[float]:
          if not model_key:
              for k, v in self.models.items():
                  if v.get("supports_embedding"):
                      model_key = k
                      break
          if not model_key:
              raise ValueError("No model supports embedding")
          cfg = self.models[model_key]
          client = self._get_client(model_key)
          provider = cfg.get("provider", "")
          model_version = cfg.get("model_version", "")
          if provider == "openai":
              resp = client.embeddings.create(model=model_version, input=text)
              return resp.data[0].embedding
          raise ValueError(f"Provider {provider} does not support embeddings via this adapter")

      def list_models(self) -> dict[str, dict]:
          return {k: {
              "provider": v.get("provider"),
              "version": v.get("model_version"),
              "supports_streaming": v.get("supports_streaming"),
              "supports_functions": v.get("supports_functions"),
              "supports_vision": v.get("supports_vision"),
              "supports_embedding": v.get("supports_embedding"),
          } for k, v in self.models.items()}
  ```

- [ ] **P2-1-4: Verify ModelAdapter loads configs**

  Run:
  ```bash
  python -c "from .workbuddy.scripts.model_adapter import ModelAdapter; m = ModelAdapter(); print(json.dumps(m.list_models(), indent=2, ensure_ascii=False))"
  ```

  Expected: Prints 4 models (claude-opus, gpt4-turbo, etc.) with capability flags

---

### Task P2-2: AgentOrchestrator

**Files:**
- Create: `.workbuddy/scripts/agent_orchestrator.py`

- [ ] **P2-2-1: Create agent_orchestrator.py — Agent class + loading**

  ```text
  import json
  import re
  from pathlib import Path
  from dataclasses import dataclass, field
  from typing import Optional

  SCRIPTS_DIR = Path(__file__).resolve().parent
  AI_DIR = SCRIPTS_DIR.parent / "AI协作体系"
  AGENT_POOL_DIR = AI_DIR / "智能体池"
  ROLE_DIR = AI_DIR / "角色库"


  @dataclass
  class Agent:
      name: str
      role: str
      model: str
      instructions: str
      system_prompt: str = ""


  class AgentLoader:
      def load(self, name: str) -> Optional[Agent]:
          md_dir = AGENT_POOL_DIR / name
          if md_dir.is_dir():
              files = list(md_dir.glob("*.md"))
          else:
              md_file = AGENT_POOL_DIR / f"{name}.md"
              files = [md_file] if md_file.exists() else []

          for f in files:
              text = f.read_text(encoding="utf-8")
              agent = self._parse_agent(text, f.stem)
              if agent:
                  return agent
          return None

      def _parse_agent(self, text: str, default_name: str) -> Optional[Agent]:
          name = self._extract(text, r"(?:名称|name)[：:]\s*(.+)") or default_name
          role = self._extract(text, r"(?:角色|role)[：:]\s*(.+)") or "assistant"
          model = self._extract(text, r"(?:模型|model)[：:]\s*(.+)") or "gpt4"
          return Agent(name=name, role=role, model=model, instructions=text)

      def _extract(self, text: str, pattern: str) -> Optional[str]:
          m = re.search(pattern, text)
          return m.group(1).strip() if m else None
  ```

- [ ] **P2-2-2: Add RoleLoader for role prompt library**

  ```text
  class RoleLoader:
      def load(self, role_name: str) -> Optional[str]:
          for ext in [".md", ".txt", ".yaml"]:
              f = ROLE_DIR / f"{role_name}{ext}"
              if f.exists():
                  return f.read_text(encoding="utf-8")
          return None
  ```

- [ ] **P2-2-3: Add AgentOrchestrator class**

  ```text
  class AgentOrchestrator:
      def __init__(self, model_adapter=None):
          self.agent_loader = AgentLoader()
          self.role_loader = RoleLoader()
          self._adapter = model_adapter

      @property
      def adapter(self):
          if self._adapter is None:
              from model_adapter import ModelAdapter
              self._adapter = ModelAdapter()
          return self._adapter

      def load_agent(self, name: str) -> Optional[Agent]:
          return self.agent_loader.load(name)

      def assign_role(self, agent: Agent, task: str) -> str:
          role_prompt = self.role_loader.load(agent.role)
          if role_prompt:
              return f"{role_prompt}\n\n---\n\n{task}"
          return task

      async def execute(self, agent: Agent, task: str) -> str:
          prompt = self.assign_role(agent, task)
          messages = [{"role": "system", "content": agent.instructions},
                       {"role": "user", "content": prompt}]
          result = self.adapter.chat(agent.model, messages)
          self.save_state(agent, result)
          return result

      def save_state(self, agent: Agent, result: str):
          try:
              from memoryos import MemoryOS
              mo = MemoryOS()
              mo.save_checkpoint()
          except Exception:
              pass
  ```

- [ ] **P2-2-4: Verify AgentOrchestrator loads agents**

  Run:
  ```bash
  python -c "import sys; sys.path.insert(0, '.workbuddy/scripts'); from agent_orchestrator import AgentOrchestrator; ao = AgentOrchestrator(); print('Orchestrator ready'); agents = list(Path('.workbuddy/AI协作体系/智能体池').glob('**/*.md')); print(f'Found {len(list(agents))} agent definitions')"
  ```

  Expected: "Orchestrator ready" and count of agent definition files

---

### Task P2-3: WorkflowEngine

**Files:**
- Create: `.workbuddy/scripts/workflow_engine.py`

- [ ] **P2-3-1: Create workflow_engine.py**

  ```text
  import asyncio
  import json
  from dataclasses import dataclass, field
  from typing import Any, Callable, Awaitable


  @dataclass
  class Step:
      name: str
      handler: Callable[..., Awaitable[Any]]
      args: dict = field(default_factory=dict)


  class WorkflowEngine:
      def __init__(self):
          self._workflows: dict[str, list[Step]] = {}

      def define(self, name: str, steps: list[Step]):
          self._workflows[name] = steps

      async def run(self, name: str, context: dict = None) -> dict:
          steps = self._workflows.get(name)
          if not steps:
              raise ValueError(f"Unknown workflow: {name}")
          ctx = context or {}
          results = {}
          for step in steps:
              result = await step.handler(**{**step.args, **ctx})
              results[step.name] = result
              ctx[step.name] = result
          return {"workflow": name, "results": results}
  ```

- [ ] **P2-3-2: Verify WorkflowEngine runs a simple workflow**

  Run:
  ```bash
  python -c "import sys; sys.path.insert(0, '.workbuddy/scripts'); from workflow_engine import WorkflowEngine, Step; import asyncio; e=WorkflowEngine(); e.define('test', [Step('hello', lambda: print('OK'))]); asyncio.run(e.run('test'))"
  ```

  Expected: Prints "OK" and returns results dict

---

### Task P3-1: MCP Server Registration

**Files:**
- Create: `.opencode/mcp_servers.jsonc`
- Create: `.opencode/opencode.jsonc`

- [ ] **P3-1-1: Create .opencode directory and mcp_servers.jsonc**

  ```jsonc
  {
    "mcpServers": {
      "db-knowledge": {
        "command": "python",
        "args": ["mcp_server.py"],
        "transport": "stdio",
        "description": "Knowledge base MCP server providing search, content analysis, pipeline, and maintenance tools"
      }
    }
  }
  ```

- [ ] **P3-1-2: Create opencode.jsonc**

  ```jsonc
  {
    "mcpServers": {
      "db-knowledge": {
        "command": "python",
        "args": ["mcp_server.py"],
        "transport": "stdio",
        "description": "Knowledge base MCP server"
      }
    }
  }
  ```

---

### Task P3-2: Skills

**Files:**
- Create: `.opencode/skills/knowledge-mgt/SKILL.md`
- Create: `.opencode/skills/pipeline/SKILL.md`

- [ ] **P3-2-1: Create knowledge management skill**

  > `.opencode/skills/knowledge-mgt/SKILL.md`

  ```markdown
  # Knowledge Management Skill

  Provides access to the knowledge base through the db-knowledge MCP server.

  ## Tools Used
  - `search_all` — Full-text + vector + memory combined search
  - `vector_search` — Semantic search via FAISS embeddings
  - `search_memory` — Memory layer search
  - `analyze_content` — Extract tags, entities, summary from content
  - `get_graph` — Knowledge graph overview
  - `get_status` — System status

  ## Workflows
  ### Search Knowledge Base
  1. Call `search_all` with the user's query
  2. Return formatted results

  ### Analyze New Content
  1. Call `analyze_content` with the file path
  2. Call `process_file` to run full pipeline
  ```

- [ ] **P3-2-2: Create pipeline skill**

  > `.opencode/skills/pipeline/SKILL.md`

  ```markdown
  # Pipeline Management Skill

  Automates content ingestion and maintenance workflows.

  ## Tools Used
  - `process_file` — Analyze → route → index → memory pipeline
  - `watch_inbox` — Scan inbox for new files
  - `rebuild_index` — Rebuild FAISS + SQLite index
  - `run_maintenance` — Full maintenance run
  - `run_backup` — Workspace backup

  ## Workflows
  ### Ingest New Content
  1. Call `watch_inbox` to find new files
  2. For each file, call `process_file`
  3. Return processing summary

  ### Run Maintenance
  1. Call `rebuild_index`
  2. Call `run_maintenance`
  3. Return status
  ```

---

### Task P3-3: Agent Definitions

**Files:**
- Create: `.opencode/agents/orchestrator.jsonc`
- Create: `.opencode/agents/content-analyzer.jsonc`

- [ ] **P3-3-1: Create orchestrator agent**

  > `.opencode/agents/orchestrator.jsonc`

  ```jsonc
  {
    "name": "knowledge-orchestrator",
    "description": "Orchestrates knowledge management tasks using MCP tools and LLM intelligence",
    "model": "gpt4",
    "instructions": "You are a knowledge management orchestrator. Use the available MCP tools to search, analyze, and manage the knowledge base. Combine search results from multiple sources for comprehensive answers.",
    "tools": ["search_all", "vector_search", "search_memory", "analyze_content", "process_file"]
  }
  ```

- [ ] **P3-3-2: Create content analyzer agent**

  > `.opencode/agents/content-analyzer.jsonc`

  ```jsonc
  {
    "name": "content-analyzer",
    "description": "Dedicated content analysis agent using vector search and memory",
    "model": "claude-opus",
    "instructions": "You are a content analysis specialist. Analyze files, extract insights, and cross-reference with existing knowledge.",
    "tools": ["analyze_content", "search_all", "get_graph"]
  }
  ```

---

### Task P3-4: Update requirements.txt

**Files:**
- Modify: `requirements.txt`

- [ ] **P3-4-1: Add MCP and LLM SDK dependencies**

  Current `requirements.txt`:
  ```
  flask>=3.0
  faiss-cpu>=1.7
  numpy>=1.24
  pandas>=2.0
  pyyaml>=6.0
  watchdog>=4.0
  markdown>=3.5
  requests>=2.31
  ```

  Append to `requirements.txt`:
  ```
  mcp>=1.0
  openai>=1.0
  anthropic>=0.30
  zhipuai>=2.0
  ```
