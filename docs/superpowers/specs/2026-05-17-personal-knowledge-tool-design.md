# 个人知识管理工具 — 设计规格 (Phase B)

> **版本**: 1.0  
> **创建**: 2026-05-17  
> **状态**: 已批准  
> **全局路线**: Phase B (个人工具) → Phase C (AI后端) → Phase A (通用交付)

---

## 一、目标

将当前通用知识库框架从"15个独立可导入但未串联的脚本"改造成一个**真正可用的个人知识管理工具**。

### 核心能力

| 能力 | 当前 | 目标 |
|------|------|------|
| 启动方式 | 15个独立 CLI 入口 | 一条命令启动全部服务 |
| 搜索 | 关键词 grep | 关键词 + 向量语义混合搜索 |
| Web 界面 | 无 | 浏览器可用的管理界面 |
| 记忆系统 | 完整但零调用 | 每个文件操作自动写入记忆 |
| 内容分析 | 领域硬编码 | 可配置通用分析 |
| 文件旅程 | 断裂的 | inbox → 分析 → wiki/memory 全自动 |

---

## 二、系统架构

```
┌──────────────────────────────────────────────────────────────┐
│                    app.py (统一守护进程)                       │
│  Flask Web Server :5000                                      │
│  ├─ Web UI (浏览器)                                          │
│  ├─ REST API                                                │
│  └─ CLI 命令行                                               │
├──────────────────────────────────────────────────────────────┤
          │                │               │
          ▼                ▼               ▼
┌─────────────────┐ ┌──────────────┐ ┌──────────────┐
│  vector_search   │ │  wiki/       │ │  MemoryOS    │
│  FAISS + BGE     │ │  知识图谱     │ │  三层记忆     │
│  embeddings      │ │  SQLite 索引  │ │  JSONL 持久化 │
└─────────────────┘ └──────────────┘ └──────────────┘
          │                │               │
          └────────────────┴───────────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │  文件系统        │
                  │  00-99 目录结构  │
                  │  .workbuddy/   │
                  └────────────────┘
```

---

## 三、组件明细

### 3.1 app.py (新建)

Flask Web 服务器，统一入口。

**启动方式：**
```bash
python app.py                    # 启动 Web 服务 + 后台 watcher（默认）
python app.py --daemon           # 后台守护进程模式（无控制台输出）
python app.py --cli search "关键词"  # 直接搜索并退出（--cli 后的参数转发给 search_content.py）
```

**路由：**
| 路由 | 方法 | 功能 |
|------|------|------|
| `/` | GET | Web UI 首页 — 搜索+仪表盘 |
| `/search` | GET/POST | 全文+向量混合搜索 |
| `/ingest` | POST | 接收文件，触发处理流水线 |
| `/memory` | GET | 查看/管理记忆系统 |
| `/browse/*` | GET | 浏览 wiki 知识图谱 |
| `/maintain` | POST | 触发维护任务 |
| `/api/search` | GET | REST API 搜索接口 |
| `/api/ingest` | POST | REST API 文件摄入 |

### 3.2 vector_search.py (新建)

语义检索引擎。

**依赖：** `sentence-transformers`, `faiss-cpu`, `numpy`

**数据结构：**
```python
# SQLite 表结构
CREATE TABLE documents (
    id TEXT PRIMARY KEY,
    path TEXT UNIQUE,
    title TEXT,
    content TEXT,
    file_type TEXT,
    tags TEXT,        -- JSON array
    created_at TEXT,
    modified_at TEXT
);

CREATE TABLE embeddings (
    doc_id TEXT PRIMARY KEY REFERENCES documents(id),
    vector BLOB,      -- numpy array as binary
    model_name TEXT
);
```

**接口：**
```python
class VectorSearch:
    def search(query: str, top_k: int = 10) -> List[Dict]
        # 1. query → embedding
        # 2. FAISS 检索 top_k
        # 3. 混合关键词结果
        # 4. 返回 {path, title, snippet, score, type}

    def index_file(file_path: Path) -> bool
        # 读取内容 → embedding → 存入 FAISS + SQLite

    def rebuild_index() -> int
        # 全量重建
```

### 3.3 MemoryOS 激活 (修改 memoryos.py)

**目标：** 让所有脚本都能调用记忆系统。

**新增接口：**
```python
class MemoryOS:
    def save_checkpoint()            # 持久化当前状态
    def search_memory(query, top_k)  # 搜索所有三层记忆
    def get_status() -> Dict         # 返回记忆统计
```

**集成点：**
- `auto_organizer.py` 分析文件后 → `memory.add_memory("处理了文件X", "episodic")`
- `maintenance_task.py` → `memory.save_checkpoint()`
- `app.py` → `memory.search_memory()` 作为搜索结果补充

### 3.4 SmartRouter 修复 (修改 smart_router.py)

**修复的内容：**
| 当前路径 | 要改为 | 说明 |
|-----------|--------|------|
| `.workbuddy/memory/MEMORY.md` | `.workbuddy/记忆层/MEMORY.md` | 记忆路径 |
| `.workbuddy/graph/entity_graph.json` | `05-知识沉淀/wiki/graph.json` | 图谱存储 |
| `.workbuddy/worklog/...` | `02-对话记录/...` | 工作日志 |
| `.workbuddy/index/` | （移除，改用 SQLite + vector_search） | 搜索索引 |

### 3.5 ContentAnalyzer 去领域化 (修改 content_analyzer.py)

**当前问题：** 硬编码了 `主播`, `师傅`, `风控`, `R5`, `14W线` 等业务关键词于 8 个位置。

**方案：** 将领域特定关键词抽取到可配置 JSON 文件：

```json
{
  "entity_patterns": [],
  "concept_keywords": [],
  "topic_indicators": {}
}
```

默认空数组/空对象。用户可按需添加。
移除所有主播/师傅/风控等业务关键词。如果无配置，回退到通用规则（标题提取、H1标签、文件命名分析）。

### 3.6 Pipeline 串联 (修改 auto_organizer.py)

**当前：** 独立运行，只是分析并生成报告。

**目标：**
```python
def process_and_store(file_path: Path) -> Dict:
    # 1. content_analyzer 分析
    insight = content_analyzer.analyze_file(file_path)

    # 2. smart_router 决定去向
    route = smart_router.route(insight)

    # 3. 移动文件到目标目录
    target = execute_move(file_path, route.suggested_path)

    # 4. 写入记忆
    memory.add_memory(f"存入文件: {target}", "episodic")

    # 5. 更新向量索引
    vector_search.index_file(target)

    # 6. 更新 wiki 索引（如果目标在 wiki/ 下）
    if "wiki" in route.suggested_path:
        update_wiki_index(route.suggested_path)
```

---

## 四、数据流（完整文件旅程）

```
用户拖入文件 → 01-收件箱/
    │
    ▼
[inbox_watcher 自动检测]
    │
    ▼
[content_analyzer] 提取: 主题/实体/类型/质量
    │
    ▼
[smart_router] 决策: → wiki/concepts/ 或 03-资产库/ 或 04-输出成果/
    │
    ▼
[auto_organizer] 执行: 移动 + 重命名
    │
    ▼
[memoryos.py] 记录: 短期记忆(episodic)
    │
    ▼
[vector_search] 索引: embedding → FAISS + SQLite
    │
    ▼
用户搜索 → app.py → vector_search(query) → 混合结果页面
                     └─ memory.search_memory(query)
```

---

## 五、目录/文件变更清单

### 新建文件
| 文件 | 行数(估) | 职责 |
|------|---------|------|
| `app.py` | ~200 | Flask 服务器 + 路由 |
| `vector_search.py` | ~250 | 语义搜索 + FAISS + SQLite |
| `.workbuddy/templates/index.html` | ~80 | Web UI 首页 |
| `.workbuddy/templates/search.html` | ~60 | 搜索结果页 |
| `.workbuddy/templates/browse.html` | ~50 | 知识图谱浏览 |
| `.workbuddy/config/domain_keywords.json` | ~20 | 领域关键词配置（默认空） |

### 修改文件
| 文件 | 改动量 | 改动内容 |
|------|--------|----------|
| `memoryos.py` | +40行 | 新增 `search_memory`, `save_checkpoint` |
| `smart_router.py` | +30行 | 修复断裂路径，生成缺失目录 |
| `content_analyzer.py` | -20/+30行 | 移除硬编码关键词，改为 JSON 配置 |
| `auto_organizer.py` | +60行 | 串联 pipeline，调用 memory + vector |
| `search_content.py` | +20行 | 向量搜索回退 |
| `maintenance_task.py` | +30行 | memory 清理 + 索引重建 |
| `update_index.py` | +30行 | 扩大扫描范围，写入 SQLite |
| `inbox_watcher.py` | +15行 | 触发 pipeline 而非仅报告 |
| `enhanced_inbox_watcher.py` | +15行 | 同上 |

### 新建目录
| 目录 | 用途 |
|------|------|
| `.workbuddy/templates/` | Flask HTML 模板 |
| `.workbuddy/config/` | 可配置 JSON 规则文件 |
| `.workbuddy/index/` | FAISS 向量索引文件 |

---

## 六、依赖变更

```txt
# requirements.txt 追加
flask>=3.0
sentence-transformers>=3.0
faiss-cpu>=1.8
numpy>=1.26
```

---

## 七、非目标（明确不做）

- ❌ 不做用户认证/多用户 — Phase A 再考虑
- ❌ 不做 Docker 部署 — Phase A
- ❌ 不做 LLM API 调用 — Phase C
- ❌ 不做实时协作 — 个人工具不需要
- ❌ 不做手机端适配 — 仅桌面浏览器 + CLI
