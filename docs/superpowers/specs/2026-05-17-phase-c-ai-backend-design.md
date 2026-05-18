# Phase C: AI Agent 后端 — 设计文档

> **版本**: V1.0
> **创建时间**: 2026-05-17
> **状态**: 已批准
> **前置**: Phase B（个人知识管理工具）已完成

---

## 1. 目标

将数据库管理项目从「可用15个脚本 + Flask Web UI的知识管理工具」升级为：
1. **MCP Server** — OpenCode/Cursor 可通过 MCP 协议直接调用知识库能力
2. **ModelAdapter** — 统一接入 4 个 LLM（OpenAI/Claude/智谱/Yi）
3. **Agent Runtime** — 读取 `.workbuddy/AI协作体系/` 的文档配置，变成可执行 Agent
4. **OpenCode 集成** — 通过 `.opencode/` 注册技能和 Agent

## 2. 整体架构

```
                    +---------------------------+
                    |   OpenCode / Cursor       |
                    |   (MCP Client)            |
                    +-----------┬---------------+
                                | MCP 协议 (stdio)
                    +----------─▼───────────────+
                    |   mcp_server.py           |  <- P1 新增
                    |   (MCP Server)            |
                    |   15+ Tools               |
                    +----------┬---------------+
                               |
              +----------------+---------------+----------------+
              |                |               |                |
     +--------▼-----+  +------▼--------+  +---▼-----------+  |
     | 搜索/索引     |  | 内容分析/路由  |  | 流水线/记忆   |  |
     |vector_search  |  |content_analy  |  |auto_organizer |  |
     |memoryos.py    |  |smart_router   |  |memoryos.py    |  |
     +---------------+  +---------------+  +---------------+  |
                                                              |
                    +---------------------------+              |
                    |   AgentOrchestrator       |  <- P2 新增  |
                    |   + ModelAdapter          |             |
                    +-----------┬---------------+             |
                                |
              +----------------+----------------+
              |                |                |
     +--------▼-----+  +------▼--------+  +---▼-----------+
     | OpenAI       |  | Claude        |  | 智谱 / Yi     |
     | gpt-4        |  | claude-3      |  | glm4/yi      |
     +--------------+  +---------------+  +--------------+
```

## 3. 文件变更

### 新增文件
| 文件 | 估计行数 | 阶段 | 说明 |
|------|---------|------|------|
| mcp_server.py | ~280 | P1 | MCP Server |
| .workbuddy/scripts/model_adapter.py | ~200 | P2-1 | 统一 LLM 接口 |
| .workbuddy/scripts/agent_orchestrator.py | ~300 | P2-2 | Agent 运行时 |
| .workbuddy/scripts/workflow_engine.py | ~150 | P2-3 | 工作流引擎 |
| .opencode/mcp_servers.jsonc | ~10 | P3 | MCP 注册 |
| .opencode/skills/knowledge-mgt/SKILL.md | ~50 | P3 | 知识管理技能 |
| .opencode/skills/pipeline/SKILL.md | ~50 | P3 | 流水线技能 |
| .opencode/agents/orchestrator.jsonc | ~20 | P3 | 编排 Agent |
| .opencode/agents/content-analyzer.jsonc | ~20 | P3 | 内容分析 Agent |

### 修改文件
| 文件 | 修改 | 阶段 |
|------|------|------|
| maintenance_task.py | os.system -> subprocess.run | P0 |
| app.py | 0.0.0.0 -> 127.0.0.1 | P0 |
| auto_organizer.py | copy2 -> move | P0 |
| update_index.py | bare except -> specific | P0 |
| search_content.py | bare except -> specific | P0 |
| requirements.txt | 追加 mcp, openai, anthropic | 最终 |

## 4. MCP Server 设计

### 传输方式
- stdio 传输（无端口占用，零配置）

### Tools（15+）

**搜索组：**
- search_all(query, limit=5): 全文+向量+记忆 三联搜索
- vector_search(query, limit=5): FAISS 语义搜索
- search_memory(query, context=None): MemoryOS 记忆搜索
- keyword_search(keywords): 关键词搜索

**内容组：**
- analyze_content(path): 内容分析（标签+实体+摘要）
- route_content(path): 自动路由
- get_content_stats(): 内容统计

**流水线组：**
- process_file(path): 完整流水线（分析->路由->索引->记忆）
- watch_inbox(): 扫描收件箱
- run_maintenance(): 维护任务

**系统组：**
- get_status(): 系统状态
- run_backup(): 备份
- rebuild_index(): 重建索引
- get_graph(): 知识图谱

## 5. ModelAdapter 设计

```python
class ModelAdapter:
    def __init__(self, config_dir: Path):
        # 扫描 模型配置/ 下所有 *.yaml
        # 按 provider 分组，懒加载

    def chat(self, model_key: str, messages: list, stream=False):
        # 自动路由到对应 provider

    def embed(self, text: str) -> list[float]:
        # 仅对 supports_embedding=true 的模型

    def list_models() -> dict[str, dict]:
        # 返回所有可用模型
```

### 支持的 model_key
| key | Provider | API Key |
|-----|----------|---------|
| gpt4, gpt4o, gpt4-turbo | OpenAI | OPENAI_API_KEY |
| claude-opus, claude-sonnet, claude-haiku | Anthropic | ANTHROPIC_API_KEY |
| zhipu-glm4, zhipu-glm4v | 智谱 | ZHIPUAI_API_KEY |
| yi-plus, yi-vision | 零一万物 | YI_API_KEY |

## 6. AgentOrchestrator 设计

```python
class AgentOrchestrator:
    def load_agent(self, name) -> Agent
        # 读取 智能体定义.md

    def assign_role(self, agent, task) -> str
        # 从 角色库/ 加载对应角色 prompt

    async def execute(self, agent, task) -> str
        # 角色 prompt + 任务 -> chat + 可选 MCP tool

    def save_state(self, agent, result)
        # 存入 MemoryOS
```

### WorkflowEngine
```python
class WorkflowEngine:
    def define(steps)
    async def run(workflow, context) -> dict
        # 顺序执行 steps，步骤间传递上下文
```

## 7. MCP Server 注册

```json
"mcpServers": {
  "db-knowledge": {
    "command": "python",
    "args": ["mcp_server.py"],
    "transport": "stdio",
    "description": "知识库 MCP 服务"
  }
}
```

## 8. 执行顺序

严格串行：P0 -> P1 -> P2-1 -> P2-2 -> P2-3 -> P3

### P0: 安全修复 (30min)
1. maintenance_task.py: os.system -> subprocess.run
2. app.py: 0.0.0.0 -> 127.0.0.1
3. auto_organizer.py: copy2 -> move
4. update_index.py + search_content.py: bare except -> specific

### P1: MCP Server (2-3h)
1. 创建 mcp_server.py
2. 实现 15+ MCP tools
3. 验证启动

### P2: Agent Runtime (4-6h)
1. model_adapter.py
2. agent_orchestrator.py
3. workflow_engine.py

### P3: OpenCode 集成 (2-3h)
1. mcp_servers.jsonc
2. 2个 SKILL.md
3. 2个 Agent 定义
4. requirements.txt

---

*本文档对应 Phase B 完成后的 AI 能力接入阶段*
