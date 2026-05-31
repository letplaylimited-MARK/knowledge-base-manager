# API文档

> 版本：V2.0 | 更新：2026-05-23

---

## 脚本入口

### update_index.py

```bash
python .workbuddy/scripts/update_index.py
```

扫描 `01-收件箱/`、`02-对话记录/`、`03-资产库/`、`04-输出成果/`、`05-知识沉淀/`、`06-参考资料/`、`07-项目文档/`，更新 `AGENTS.md` 时间戳，并重建 SQLite/FAISS 搜索索引（FAISS 依赖可选）。

### search_content.py

```bash
python .workbuddy/scripts/search_content.py "关键词"
```

在项目工作区内做文件名和文件内容关键词搜索。当前 CLI 只接受一个关键词参数；高级过滤可直接调用 `search_content.search_content(query, max_results=...)` 和 `search_content.search_filename(query)`。

### extract_docx.py

```bash
python .workbuddy/scripts/extract_docx.py
```

当前脚本入口用于批量处理脚本内登记的 DOCX 清单。通用文件抽取请在 Python 中调用 `extract_docx.extract_docx(path)`，或通过 MCP 工具 `extract_docx_text` 暴露给 AI 客户端。

### backup.py

```bash
python .workbuddy/scripts/backup.py
```

按脚本默认规则执行备份。自定义备份路径/压缩策略尚未做成命令行参数。

### batch_import.py

```bash
python batch_import.py <目录路径>
```

批量读取目录下文件，调用 `AutoOrganizer.process_and_store()` 执行分析、路由、移动、索引和记忆记录。该入口会产生文件移动和索引写入副作用，正式导入前建议先在副本目录验证。

---

## Web / REST API

```bash
python app.py
```

| 路径 | 方法 | 说明 |
|---|---|---|
| `/` | GET | Web 首页 |
| `/search?q=关键词` | GET | Web 搜索页 |
| `/browse/` | GET | 浏览 `05-知识沉淀/wiki/` |
| `/memory` | GET | MemoryOS 摘要 |
| `/api/search?q=关键词` | GET | JSON 搜索接口 |
| `/api/index` | POST | 重建搜索索引 |
| `/ingest` | POST | 导入指定文件路径 |
| `/maintain` | POST | 执行维护任务 |

## MCP API

```bash
python mcp_server.py
```

MCP server 通过 stdio 暴露 20 个工具，覆盖搜索、记忆、内容分析、文件管道、索引、备份、收件箱扫描和工作流执行。工具清单以 `mcp_server.py` 的 `TOOL_DEFINITIONS` 与 `HANDLERS` 为准。

---

## 知识库文件 API

### 读取知识

```python
from pathlib import Path

def read_knowledge(entity_name):
    path = Path(f"05-知识沉淀/wiki/entities/{entity_name}.md")
    return path.read_text()
```

### 写入知识

```python
def write_knowledge(entity_name, content):
    path = Path(f"05-知识沉淀/wiki/entities/{entity_name}.md")
    path.write_text(content)
```

### 搜索

```python
def search(query):
    results = []
    for p in Path("05-知识沉淀/wiki/").rglob("*.md"):
        if query in p.read_text():
            results.append(p)
    return results
```

---

*更多API请参考源码注释*
