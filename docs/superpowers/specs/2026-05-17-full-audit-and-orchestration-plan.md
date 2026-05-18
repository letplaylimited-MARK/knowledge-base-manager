# 全面审计与AI协同架构方案

> **审计日期**: 2026-05-17 | **审计范围**: 架构·代码·安全·MCP·插件·智能体·技能·工作流
> **审计引擎**: OpenCode 全能力栈（project-analyzer + code-review + dispatching-parallel-agents + 3路并行Agent）

---

## 一、当前状态总评

### 已实现（Phase B 完成后）

| 维度 | 状态 | 说明 |
|------|------|------|
| 搜索 | ✅ | vector_search.py (FAISS+SQLite+关键词回退) + search_content.py (grep) |
| 记忆 | ✅ | memoryos.py 三层记忆 (ST/MT/LT) 含 search_memory + save_checkpoint |
| 分析 | ✅ | content_analyzer.py 已去领域化，domain_keywords.json 可配置 |
| 路由 | ✅ | smart_router.py 6层路由体系 |
| 流水线 | ✅ | auto_organizer.py → post_process → vector_search + MemoryOS |
| Web UI | ✅ | app.py Flask 10路由 + 3模板 |
| 监控 | ✅ | inbox_watcher + enhanced_inbox_watcher 触发 pipeline |
| 维护 | ✅ | maintenance_task + update_index 含记忆 checkpoint + 向量索引重建 |

### 未实现（Phase C 目标）

| 维度 | 状态 | 说明 |
|------|------|------|
| LLM API实际调用 | ❌ | 零行HTTP客户端代码，4个YAML模型配置仅为文档 |
| 智能体运行时 | ❌ | 智能体定义.md 仅是文档，无可执行代码 |
| MCP 服务器 | ❌ | 50+ 可导出函数，零个MCP工具 |
| OpenCode 配置 | ❌ | 无 `.opencode/` 目录或配置文件 |
| 单元测试 | ❌ | pytest 在 requirements.txt 里，零个测试文件 |
| 统一日志 | ❌ | 100% 使用 print()，无 logging 框架 |
| 标准化路径 | ❌ | 10+ 脚本各自独立解析 WORKSPACE 路径 |

---

## 二、审计发现的严重问题

### 🔴 安全问题（需立即修复）

1. **`maintenance_task.py:24` os.system 注入风险** — 应使用 subprocess.run
2. **`app.py:119` 绑定 0.0.0.0** — 暴露到局域网，应改为 127.0.0.1
3. **`auto_organizer.py:270-271` copy2 代替 move** — 文件重复，原始文件残留
4. **`update_index.py:42` / `search_content.py:73` bare except** — 静默吞没异常

### 🟡 架构问题

5. **`scripts/` vs `脚本/` 双目录** — backup.py 放错位置
6. **记忆系统 3 个不同路径** — memoryos.py/config.yaml/app.py 各写各的
7. **4 个孤立脚本（共2858行）** — smart_router/project*/file_pipeline 零调用者
8. **Git worktree 悬空** — `.git` 指向不存在的 `C:/Users/z/...`

### 🟢 缺失功能

9. **AI协作体系仅为文档** — 体系.md + 模型YAML + 角色库 + 智能体池，零执行代码
10. **无 MCP 服务器** — 50+ 函数可导出为工具供 AI 代理使用
11. **无 OpenCode 配置** — 无法利用 skill/MCP/agent 体系化协作
12. **ChromaDB 声明但未实现** — config.yaml 标记 true，memoryos.py 从不导入

---

## 三、AI 全能力协同架构（推荐方案）

### 核心架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                       AI协同知识管理系统                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    Layer 1: MCP Server                       │    │
│  │  mcp_server.py (FastMCP) — 将 50+ 函数暴露为 MCP 工具       │    │
│  │                                                              │    │
│  │  │ 搜索组        │ 记忆组       │ 分析组       │ 流水线组    │    │
│  │  │ semantic_search│ memory_add   │ analyze_content│ process_file│
│  │  │ search_files  │ memory_search│ suggest_name │ organize_scan│
│  │  │ index_document│ memory_status│ route_content│ discover_rels│
│  │  └───────────────┴──────────────┴──────────────┴─────────────┘    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              │↓ MCP 协议                             │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │              Layer 2: AI Agent Orchestrator                  │    │
│  │  agent_orchestrator.py — 读取 AI协作体系/ 文档并执行         │    │
│  │                                                              │    │
│  │  │ 协调员Agent   │ 分析员Agent   │ 推荐员Agent  │ 扫描员Agent│    │
│  │  │ 拆解任务       │ 内容深度分析   │ 路由决策      │ 文件发现    │    │
│  │  │ 分配子任务     │ 实体/概念提取  │ 命名建议      │ 变更检测    │    │
│  │  │ 汇总结果       │ 质量评估      │ 分类决定      │ 新文件处理  │    │
│  │  └───────────────┴──────────────┴──────────────┴─────────────┘    │
│  │  ▼ 调用 models/ (通过 ModelAdapter)                              │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                              │↓ skill / agent 协议                   │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │            Layer 3: OpenCode 配置 (workflow)                  │    │
│  │  .opencode/  — 定义 skills / agents / MCP servers            │    │
│  │                                                              │    │
│  │  skills/       │ agents/       │ mcp_servers.jsonc           │    │
│  │  knowledge-mgt │ orchestrator  │ { "knowledge-mcp": {        │    │
│  │  project-audit │ content-ana   │     "command": "python",    │    │
│  │  file-pipeline │ memory-agent  │     "args": ["mcp_server"]  │    │
│  │  maintenance   │ search-agent  │   } }                       │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 三层协作流程

```
用户指令 "处理收件箱新文件"
  │
  ▼
OpenCode Agent (orchestrator)
  │ 加载 skill: knowledge-mgt
  │
  ▼ 通过 MCP 协议调用
Layer 1: MCP Server
  ├─ inbox_scan()          → 发现 3 个新文件
  ├─ analyze_content() ×3  → 每个文件分析主题/类型/质量
  ├─ route_content() ×3    → 决定去哪个子目录
  ├─ process_file() ×3     → 移动到目标 + 建索引 + 记记忆
  └─ memory_checkpoint()   → 持久化
  │
  ▼ 返回结果
OpenCode Agent 汇总报告给用户
  "已处理 3 个文件: 1个概念定义→wiki/concepts, 2个报告→04-输出成果"
```

---

## 四、各能力模块配合方式

### 1. MCP Server（核心桥梁）

**作用**: 将所有现有 Python 函数暴露为标准化的 MCP 工具，供任何 AI 客户端调用

**实现方式**: FastMCP Python server

```
mcp_server.py
├── `@mcp.tool()` 装饰器包装 15+ 个核心函数
├── `@mcp.resource()` 暴露搜索索引/记忆状态/项目概览
├── `@mcp.prompt()` 定义常用工作流模板
└── 无认证（本地工具），纯函数式
```

**配合关系**:
- 供 **OpenCode Agents** 通过 MCP 协议调用文件/搜索/记忆操作
- 供 **外部 AI 编辑器**（Cursor/Windsurf）通过 MCP 直接搜索知识库
- 供 **app.py** 替换现有 Flask API 路由（统一协议）

### 2. AI Agent Orchestrator（决策大脑）

**作用**: 读取 `.workbuddy/AI协作体系/` 和 `.workbuddy/七角色/` 中的文档，将其中定义的智能体/角色/工作流变成可执行代码

**实现方式**:
```
agent_orchestrator.py
├── ModelAdapter()       → 读取 YAML 模型配置，实例化 API 客户端
├── AgentPool()          → 读取 智能体定义.md，创建 Agent 实例
├── RoleEngine()         → 读取 七角色/ prompt，分配给 Agent
├── WorkflowEngine()     → 读取 工作流程.md，编排多步任务链
└── 所有 Agent 通过 MCP Client 调用底层工具
```

**配合关系**:
- 将**AI协作体系文档**变为可执行逻辑（这是 Phase C 的核心）
- Agent 之间通过 MCP 通信（不是直接函数调用）
- 每个 Agent 可通过 `model_adapter.py` 切换底层 LLM

### 3. OpenCode 配置（编排层）

**作用**: 将上述 MCP Server 和 Agent Orchestrator 注册到 OpenCode 生态

**实现方式**: `.opencode/` 目录
```
.opencode/
├── opencode.jsonc      → 主配置，注册 MCP server + agents
├── skills/             → 领域技能定义
│   ├── knowledge-mgt   → 知识管理完整工作流
│   ├── project-audit   → 项目结构审计
│   └── file-pipeline   → 文件处理流水线
├── agents/             → 专用 AI 代理
│   ├── content-agent   → 内容分析代理
│   ├── search-agent    → 搜索代理
│   └── memory-agent    → 记忆管理代理
└── mcp_servers.jsonc   → 指向 python mcp_server.py
```

**配合关系**:
- skills 定义 **工作流**（调多个 MCP 工具的步骤序列）
- agents 是 **持久的 AI 角色**（带记忆/上下文）
- MCP servers 是 **工具执行层**
- OpenCode 是 **编排运行时**

### 4. 现有 Skills 接入

从 OpenCode 已有 skill 池中选择可配合的：

| Skill | 配合方式 | 接入点 |
|-------|---------|--------|
| `code-review` | 审计知识库脚本代码质量 | `mcp_server.tools["analyze_content"]` + LLM review |
| `doc-coauthoring` | AI 辅助撰写知识文档 | `mcp_server.tools["memory_retrieve"]` 提供上下文 |
| `project-analyzer` | 分析项目结构和健康状况 | `mcp_server.resource["workspace://structure"]` |
| `webapp-testing` | 测试 Flask Web UI | `app.py` 启动后 Playwright 测试 |
| `systematic-debugging` | 调试流水线 bug | Agent orchestrator 调用 `memory_search` 回溯 |

### 5. LSP 的角色

LSP 主要用于：
- **代码编辑时**的实时诊断（Python/markdown）
- 但本项目核心是**知识管理而非软件开发**，LSP 是辅助性（非核心）
- 配合 MCP 使用：Cursor/VSCode 通过 LSP 编辑代码，通过 MCP 搜索知识库

### 6. 工作流（Workflow）体系

从现有 `.workbuddy/AI协作体系/` + `.workbuddy/流程/` 中的文档提取为可执行工作流：

| 工作流 | 文档来源 | MCP 工具序列 |
|--------|---------|-------------|
| 新文件处理 | 收件箱规则.md | inbox_scan → analyze → route → process → memory_checkpoint |
| 知识沉淀 | 工作流程.md | analyze_content → discover_relations → build_knowledge_graph |
| 日常维护 | 任务验证标准.md | maintenance_run → backup_now → memory_checkpoint |
| 项目回顾 | 交接清单.md | project_insights → project_boundaries → project_report |

---

## 五、Phase C 实施路线图

### 优先级 P0 — 安全修复（立即）

1. `maintenance_task.py:24` os.system → subprocess.run ✅
2. `app.py:119` 0.0.0.0 → 127.0.0.1 ✅
3. `auto_organizer.py:270` copy2 → move ✅
4. `update_index.py:42` / `search_content.py:73` bare except → 具体异常类型 ✅

### 优先级 P1 — MCP Server（核心桥梁，2-3天）

1. 创建 `mcp_server.py` (FastMCP)，包装15+核心函数为工具
2. 创建 `mcp_resources.py`，暴露 index/memory/project 状态资源
3. 创建 `mcp_prompts.py`，定义常用工作流模板
4. 配置 `.opencode/mcp_servers.jsonc` 注册到 OpenCode
5. 更新 `app.py` 通过 MCP Client 调用而非直接 import

### 优先级 P2 — AI Agent 运行时（决策大脑，3-5天）

1. 创建 `model_adapter.py` — 读取 YAML 配置，实例化 LLM 客户端
2. 创建 `agent_orchestrator.py` — Agent 调度、任务分解、结果聚合
3. 创建 `agent_pool.py` — 从智能体定义.md 加载 Agent 配置
4. 创建 `workflow_engine.py` — 从工作流程.md 加载可执行工作流
5. 连接 Agent → MCP 调用链（Agent 通过 MCP 使用工具）

### 优先级 P3 — OpenCode 深度集成（编排层，1-2天）

1. 创建 `.opencode/opencode.jsonc` — 主配置文件
2. 创建 `.opencode/skills/knowledge-mgt/` — 知识管理技能
3. 创建 `.opencode/skills/project-audit/` — 项目审计技能
4. 创建 `.opencode/agents/` — 专用 AI 代理定义
5. 测试全链路：OpenCode Agent → MCP → 现有脚本 → 结果返回

### 优先级 P4 — 体系清理（1-2天）

1. 统一 `scripts/` 和 `脚本/`（backup.py 移入 scripts/）
2. 统一记忆存储路径（硬编码为 `WORKSPACE / ".workbuddy" / "记忆层" / "memory_data"`）
3. 修复 Git 仓库（git init 或修复 worktree 引用）
4. 删除无用依赖（watchdog/openpyxl/markdown/beautifulsoup4 如不计划使用）
5. 集成 smart_router 到 auto_organizer 或正式弃用

### 优先级 P5 — 质量基建（持续）

1. 创建 `.workbuddy/scripts/core/` 包（`__init__.py`, `config.py`, `logging_setup.py`, `exceptions.py`）
2. 迁移所有脚本使用 core.config.WORKSPACE 统一路径
3. 为 auto_organizer + vector_search + content_analyzer + memoryos 编写 pytest 测试
4. 添加 lint/type-check 配置（ruff + mypy 或 pyright）
5. 创建 `requirements.lock` 锁定依赖版本

---

## 六、架构全景图

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         用户交互层                                        │
│  ┌─────────────┐  ┌──────────────────┐  ┌─────────────┐  ┌──────────┐   │
│  │ Web Browser │  │ OpenCode CLI     │  │ Cursor/VSC  │  │ API 调用 │   │
│  │ app.py:5000 │  │ opencode "搜索X"  │  │ MCP 集成    │  │ curl/HTTP│   │
│  └──────┬──────┘  └────────┬─────────┘  └──────┬──────┘  └────┬─────┘   │
│         │                  │                    │               │         │
│         ▼                  ▼                    ▼               ▼         │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │                     AI 编排层                                    │    │
│  │                                                                 │    │
│  │  ┌────────────────────┐  ┌────────────────────────────────┐     │    │
│  │  │ OpenCode Config    │  │ Agent Orchestrator             │     │    │
│  │  │ .opencode/         │  │ agent_orchestrator.py          │     │    │
│  │  │ ├─ skills/*        │  │ ├─ ModelAdapter → 4个LLM      │     │    │
│  │  │ ├─ agents/*        │  │ ├─ AgentPool   → 7角色         │     │    │
│  │  │ └─ mcp_servers.jsonc│ │ └─ WorkflowEngine → 4工作流    │     │    │
│  │  └────────────────────┘  └────────────┬───────────────────┘     │    │
│  │                                       │ MCP 协议                 │    │
│  └───────────────────────────────────────┼──────────────────────────┘    │
│                                          │                              │
│  ┌───────────────────────────────────────▼──────────────────────────┐    │
│  │                     MCP Server (mcp_server.py)                   │    │
│  │                                                                 │    │
│  │  ┌──────────┐ ┌───────────┐ ┌──────────┐ ┌───────────┐          │    │
│  │  │ ⚡ 搜索   │ │ 🧠 记忆   │ │ 📊 分析  │ │ 🔧 维护   │          │    │
│  │  │ Tools    │ │ Tools     │ │ Tools    │ │ Tools     │          │    │
│  │  └────┬─────┘ └─────┬─────┘ └────┬─────┘ └─────┬─────┘          │    │
│  │       │              │            │              │               │    │
│  └───────┼──────────────┼────────────┼──────────────┼───────────────┘    │
│          │              │            │              │                    │
│  ┌───────▼──────────────▼────────────▼──────────────▼───────────────┐    │
│  │                   现有 Python 脚本层 (Phase A+B)                   │    │
│  │                                                                 │    │
│  │  vector_search  memoryos  content_analyzer  auto_organizer      │    │
│  │  smart_router   maintenance  inbox_watcher  project_*           │    │
│  │  update_index  backup  extract_docx  naming_optimizer           │    │
│  │                                                                 │    │
│  │  ┌─────────────────────────────────────────────────────────┐    │    │
│  │  │                 存储层                                    │    │    │
│  │  │  01-收件箱/  02-对话记录/  03-资产库/  04-输出成果/       │    │    │
│  │  │  05-知识沉淀/  06-参考资料/  07-项目文档/                  │    │    │
│  │  │  .workbuddy/index/search_index.db  (FAISS+SQLite)        │    │    │
│  │  │  .workbuddy/记忆层/memory_data/  (JSON+JSONL)            │    │    │
│  │  └─────────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────┘
```

---

## 七、总结

| 能力 | 当前 | Phase C 目标 |
|------|------|-------------|
| 🛠 **MCP** | ❌ 无 | ✅ 15+ 工具 / 7+ 资源 / 5+ 提示 |
| 🤖 **Agents** | ❌ 仅文档 | ✅ 4+ 可执行 Agent / 带 MCP 工具访问 |
| 📋 **Skills** | ❌ 无 OpenCode 配置 | ✅ 3+ 领域技能 / 可复用 |
| 🔄 **Workflows** | ❌ 仅文档 | ✅ 4+ 可执行工作流 |
| 🧩 **Plugins** | ❌ 无 | ✅ 按约定加载 03-资产库/ 插件 |
| 🏗 **LSP** | ❌ 未使用 | ✅ mypy/ruff/pyright 配置 |
| 💬 **模型调用** | ❌ 零行代码 | ✅ ModelAdapter 连接 4 个 LLM |
| 🧪 **测试** | ❌ 零测试 | ✅ pytest 覆盖核心流水线 |

**实施顺序**: P0(安全) → P1(MCP) → P2(Agent运行时) → P3(OpenCode集成) → P4(清理) → P5(质量基建)

> **建议**: 从 P1 MCP Server 开始是最快见效的路径。MCP 本身不依赖 LLM 调用（工具只是包装现有函数），一旦 MCP 跑通，Agent 和 OpenCode 集成可以逐步叠加。
