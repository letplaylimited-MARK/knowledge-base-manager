# Phase B Implementation Plan — 个人知识管理工具

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 15 个独立脚本串联为可用的个人知识管理工具，包含 Web UI、向量搜索、记忆系统激活

**Architecture:** Flask Web 服务器统一入口，下层 6 个子系统（向量搜索/知识图谱/记忆系统/智能路由/内容分析/文件流水线）通过内存或 SQLite 共享状态

**Tech Stack:** Python 3.14, Flask 3.0, sentence-transformers 3.0, FAISS, SQLite3

---

## 文件变更总览

### 新建
| 文件 | 职责 |
|------|------|
| `app.py` | Flask 统一入口 + Web UI 路由 |
| `vector_search.py` | FAISS 语义搜索 + SQLite 索引 |
| `.workbuddy/templates/index.html` | 搜索首页 |
| `.workbuddy/templates/search.html` | 搜索结果页 |
| `.workbuddy/templates/browse.html` | 知识图谱浏览 |
| `.workbuddy/config/domain_keywords.json` | 领域关键词配置 |

### 修改
| 文件 | 改动 |
|------|------|
| `requirements.txt` | 追加 flask, sentence-transformers, faiss-cpu, numpy |
| `memoryos.py` | 新增 search_memory(), save_checkpoint() |
| `smart_router.py` | 修复断裂路径 |
| `content_analyzer.py` | 移除硬编码业务关键词 |
| `auto_organizer.py` | 串联 pipeline, 调 memory + vector_search |
| `search_content.py` | 向量搜索回退 |
| `maintenance_task.py` | 增加 memory 清理 + 索引重建 |
| `inbox_watcher.py` | 触发 pipeline |
| `enhanced_inbox_watcher.py` | 触发 pipeline |
| `update_index.py` | 扩大扫描范围 |

### 新建目录
| 目录 | 用途 |
|------|------|
| `.workbuddy/templates/` | Flask 模板 |
| `.workbuddy/config/` | 配置 JSON |
| `.workbuddy/index/` | FAISS + SQLite 索引文件 |

---

### Task 1: 创建目录 + 更新依赖 + 创建 config

**Files:**
- Create: `.workbuddy/templates/`
- Create: `.workbuddy/config/`
- Create: `.workbuddy/index/`
- Create: `.workbuddy/config/domain_keywords.json`
- Create: `.workbuddy/reports/`
- Create: `.workbuddy/metadata/`
- Modify: `requirements.txt`

- [ ] **Step 1: 创建缺失目录**

Run:
```powershell
$dirs = @(
    ".workbuddy\templates",
    ".workbuddy\config",
    ".workbuddy\index",
    ".workbuddy\reports",
    ".workbuddy\metadata"
)
foreach ($d in $dirs) {
    if (!(Test-Path -LiteralPath $d)) { New-Item -ItemType Directory -Path $d }
}
```
Expected: 5 directories created

- [ ] **Step 2: 更新 requirements.txt**

Replace `requirements.txt` content:
```txt
# 通用知识库框架 V2.0 — Phase B
flask>=3.0
sentence-transformers>=3.0
faiss-cpu>=1.8
numpy>=1.26
pyyaml>=6.0
python-docx>=1.1.0
openpyxl>=3.1.0
markdown>=3.5
beautifulsoup4>=4.12
pathlib2>=2.3
watchdog>=3.0
pytest>=7.0
pytest-cov>=4.0
```

- [ ] **Step 3: 创建 domain_keywords.json**

Write `.workbuddy/config/domain_keywords.json`:
```json
{
  "version": "1.0",
  "description": "领域关键词配置 — 按需添加你的业务关键词",
  "entity_patterns": [],
  "concept_keywords": [],
  "topic_indicators": {},
  "metric_patterns": []
}
```

- [ ] **Step 4: 验证**

Run: `python -c "import json; json.load(open('.workbuddy/config/domain_keywords.json'))"`
Expected: 无错误

---

### Task 2: 创建 vector_search.py

**Files:**
- Create: `vector_search.py`

- [ ] **Step 1: 创建 vector_search.py**

Write `.workbuddy/scripts/vector_search.py`:
```text
#!/usr/bin/env python3
"""
向量语义搜索引擎 — FAISS + sentence-transformers + SQLite
"""

import json
import sqlite3
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional

WORKSPACE = Path(__file__).resolve().parent.parent.parent
INDEX_DIR = WORKSPACE / ".workbuddy" / "index"
DB_PATH = INDEX_DIR / "search_index.db"
FAISS_PATH = INDEX_DIR / "vectors.faiss"

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    HAS_VECTOR = True
except ImportError:
    HAS_VECTOR = False


def _get_db():
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            path TEXT UNIQUE,
            title TEXT,
            content_preview TEXT,
            file_type TEXT,
            tags TEXT DEFAULT '[]',
            created_at TEXT,
            modified_at TEXT
        )
    """)
    return conn


def index_file(file_path: Path) -> bool:
    """索引单个文件到 SQLite + FAISS"""
    if not file_path.exists() or file_path.is_dir():
        return False

    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False

    rel_path = str(file_path.relative_to(WORKSPACE))
    title = file_path.stem
    preview = content[:500]

    conn = _get_db()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO documents (id, path, title, content_preview, file_type, modified_at) VALUES (?, ?, ?, ?, ?, ?)",
            (rel_path, rel_path, title, preview, file_path.suffix, str(file_path.stat().st_mtime)),
        )
        conn.commit()
    finally:
        conn.close()

    return True


def rebuild_index(scan_dirs: List[Path] = None) -> int:
    """全量重建索引"""
    if scan_dirs is None:
        scan_dirs = [
            WORKSPACE / "01-收件箱",
            WORKSPACE / "03-资产库",
            WORKSPACE / "05-知识沉淀",
            WORKSPACE / "07-项目文档",
        ]

    conn = _get_db()
    conn.execute("DELETE FROM documents")
    conn.commit()
    conn.close()

    # Remove old FAISS index
    if FAISS_PATH.exists():
        FAISS_PATH.unlink()

    count = 0
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for f in scan_dir.rglob("*"):
            if f.is_file() and f.suffix in {".md", ".txt", ".json", ".py", ".yaml", ".yml"}:
                if index_file(f):
                    count += 1

    return count


def search_keyword(query: str, top_k: int = 20) -> List[Dict]:
    """关键词搜索（回退方案）"""
    query_lower = query.lower()
    results = []
    conn = _get_db()
    try:
        rows = conn.execute("SELECT path, title, content_preview, file_type FROM documents").fetchall()
        for path, title, preview, file_type in rows:
            if query_lower in (title + preview).lower():
                results.append({
                    "path": path, "title": title,
                    "snippet": preview[:200], "type": file_type,
                    "score": 0.5,
                })
    finally:
        conn.close()
    return results[:top_k]


def search(query: str, top_k: int = 10) -> List[Dict]:
    """混合搜索：向量优先，关键词回退"""
    if not HAS_VECTOR or not FAISS_PATH.exists():
        return search_keyword(query, top_k)

    try:
        model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
        index = faiss.read_index(str(FAISS_PATH))
        query_vec = model.encode([query])
        distances, indices = index.search(np.array(query_vec).astype("float32"), top_k)

        conn = _get_db()
        results = []
        rows = conn.execute("SELECT path, title, content_preview, file_type FROM documents").fetchall()
        conn.close()

        for i, idx in enumerate(indices[0]):
            if idx >= 0 and idx < len(rows):
                path, title, preview, file_type = rows[idx]
                results.append({
                    "path": path, "title": title,
                    "snippet": preview[:200], "type": file_type,
                    "score": float(distances[0][i]),
                })
        return results
    except Exception:
        return search_keyword(query, top_k)


def build_faiss_index() -> int:
    """从 SQLite 构建 FAISS 向量索引"""
    if not HAS_VECTOR:
        return 0

    model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
    conn = _get_db()
    rows = conn.execute("SELECT id, content_preview FROM documents").fetchall()
    conn.close()

    if not rows:
        return 0

    texts = [r[1] for r in rows]
    embeddings = model.encode(texts, show_progress_bar=False)
    dim = embeddings.shape[1]

    index = faiss.IndexFlatL2(dim)
    index.add(np.array(embeddings).astype("float32"))
    faiss.write_index(index, str(FAISS_PATH))

    return len(rows)


if __name__ == "__main__":
    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "rebuild"

    if cmd == "rebuild":
        count = rebuild_index()
        print(f"索引了 {count} 个文件")
        if HAS_VECTOR:
            vec_count = build_faiss_index()
            print(f"向量索引构建完成: {vec_count} 条")
        else:
            print("提示: 安装 sentence-transformers + faiss-cpu 可启用语义搜索")

    elif cmd == "search":
        query = sys.argv[2] if len(sys.argv) > 2 else ""
        if not query:
            print("用法: python vector_search.py search '关键词'")
            sys.exit(1)
        results = search(query)
        for r in results[:10]:
            print(f"  [{r['score']:.2f}] {r['path']}")
            print(f"      {r['snippet'][:80]}...")
```

- [ ] **Step 2: 验证可导入**

Run: `python -c "import sys; sys.path.insert(0, '.workbuddy/scripts'); from vector_search import rebuild_index, search; print('import OK')"`

Expected: `import OK`

- [ ] **Step 3: 验证索引构建**

Run: `python .workbuddy/scripts/vector_search.py rebuild`
Expected: `索引了 N 个文件` (N >= 0)

---

### Task 3: 修复 SmartRouter 断裂路径

**Files:**
- Modify: `.workbuddy/scripts/smart_router.py`

- [ ] **Step 1: 修复路径映射**

In `smart_router.py`, modify `_generate_path` method to replace all broken paths:

```text
    def _generate_path(self, layer: KnowledgeLayer, features: Dict, context: Dict) -> str:
        from datetime import datetime

        if layer == KnowledgeLayer.RAW_FILES:
            if 'prompt' in str(features.get('keywords', [])).lower() or 'ai技能' in str(features.get('keywords', [])).lower():
                return "03-资产库/"
            elif any(k in str(features.get('keywords', [])) for k in ['知识', '概念', '规则']):
                return "05-知识沉淀/wiki/concepts/"
            else:
                return "01-收件箱/"

        elif layer == KnowledgeLayer.FILE_INDEX:
            return "05-知识沉淀/wiki/"

        elif layer == KnowledgeLayer.WORK_LOGS:
            today = datetime.now().strftime("%Y-%m-%d")
            return f"02-对话记录/{today}.md"

        elif layer == KnowledgeLayer.LONG_TERM_MEMORY:
            return ".workbuddy/记忆层/MEMORY.md"

        elif layer == KnowledgeLayer.KNOWLEDGE_GRAPH:
            return "05-知识沉淀/wiki/index.md"

        elif layer == KnowledgeLayer.KNOWLEDGE_CRYSTALS:
            crystal_name = self._extract_crystal_name(features, context)
            return f"05-知识沉淀/wiki/concepts/{crystal_name}.md"

        return "01-收件箱/"
```

Also add auto-creation of missing parent directories in the `route` method:

```text
    def route(self, content: str, context: Dict = None) -> Dict:
        analysis = self.analyze_content(content, context)
        suggested = analysis['suggested_path']
        full_path = self.workbuddy_path.parent / suggested
        full_path.parent.mkdir(parents=True, exist_ok=True)
        ...
```

Also fix the demo `base_path` line 275 from `str(Path(__file__).resolve().parent.parent.parent)` — it already uses dynamic path, so leave it.

- [ ] **Step 2: 验证**

Run: `python -c "import sys; sys.path.insert(0, '.workbuddy/scripts'); from smart_router import SmartRouter, KnowledgeLayer; r = SmartRouter(str('.')); result = r.route('测试知识概念定义'); print(result['suggested_path'])"`
Expected: path like `05-知识沉淀/wiki/concepts/...`

---

### Task 4: ContentAnalyzer 去领域化

**Files:**
- Modify: `.workbuddy/scripts/content_analyzer.py`

- [ ] **Step 1: 移除硬编码业务关键词**

In `content_analyzer.py`:
- In `_extract_entities` (lines 96-153): Remove all anchor_patterns (主播名), system_patterns that reference specific business (风控/审核), metric_patterns with R5/14W/SF. Replace with domain_keywords.json patterns if available.
- In `_extract_concepts` (lines 155-178): Remove `identity_confirmed`, `agen_gen`, `风控审核`, `数据分析`, `三阶段` etc. Make concept_keywords read from config.
- In `_identify_core_topic` (lines 233-257): Remove business-specific topic detection (风控审核系统/三阶段运营模型/师傅运营体系/主播结算制度). Use generic fallback: title from H1, or "综合内容".
- In `_determine_content_type` (lines 180-209): Remove business-specific types (风控审核Prompt/诊断报告/制度文档).

Add config loading at top of file:
```text
CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / ".workbuddy" / "config" / "domain_keywords.json"
def _load_config():
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except Exception:
        return {"entity_patterns": [], "concept_keywords": [], "topic_indicators": {}, "metric_patterns": []}
```

Remove lines 96-153 entirely and replace with:
```text
    def _extract_entities(self, content: str) -> List[Dict]:
        entities = []
        for pattern in self.ontology.get("entity_patterns", []):
            for match in re.finditer(pattern.get("regex", ""), content):
                entities.append({"name": match.group(1), "type": pattern.get("type", "ENTITY"), "confidence": 0.7})
        return entities[:10]
```

Remove lines 155-178 entirely and replace with:
```text
    def _extract_concepts(self, content: str) -> List[str]:
        from . import vector_search
        words = set(re.findall(r'[\u4e00-\u9fa5]{2,}', content))
        keywords = set(self.ontology.get("concept_keywords", []))
        return list(words & keywords)[:10]
```

Remove lines 233-257 and replace with:
```text
    def _identify_core_topic(self, content: str, entities: List[Dict], concepts: List[str]) -> str:
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip()[:50]
        if concepts:
            return concepts[0]
        if entities:
            return entities[0]["name"]
        return "综合内容"
```

- [ ] **Step 2: 验证导入**

Run: `python -c "import sys; sys.path.insert(0, '.workbuddy/scripts'); from content_analyzer import ContentAnalyzer; a = ContentAnalyzer(); print('import OK')"`
Expected: `import OK`

- [ ] **Step 3: 验证通用分析**

Run: `python -c "import sys; sys.path.insert(0, '.workbuddy/scripts'); from content_analyzer import ContentAnalyzer; a = ContentAnalyzer(); from pathlib import Path; i = a.analyze_file(Path('test.md'), '# Hello World\nThis is a test.'); print(i.core_topic, i.content_type)"`
Expected: `Hello World 通用文档`

---

### Task 5: MemoryOS 激活 — 新增 API 方法

**Files:**
- Modify: `.workbuddy/记忆层/memoryos.py`

- [ ] **Step 1: 新增 search_memory 方法**

Add after `get_memory_summary` (~line 435):
```text
    def search_memory(self, query: str, top_k: int = 5) -> List[Dict]:
        """在所有三层记忆中搜索"""
        results = []
        query_lower = query.lower()

        for entry in self.short_term.get_all():
            if query_lower in entry.content.lower():
                results.append({"layer": "short_term", "content": entry.content[:200], "time": entry.timestamp, "score": 1.0})

        for entry in self.mid_term._memory:
            if query_lower in entry.content.lower():
                results.append({"layer": "mid_term", "content": entry.content[:200], "time": entry.timestamp, "score": entry.heat / 5.0})

        for item in self.long_term.knowledge:
            content = item.get("content", "")
            if query_lower in content.lower():
                results.append({"layer": "long_term", "content": content[:200], "time": item.get("added_at", ""), "score": 0.8})

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def save_checkpoint(self):
        """持久化所有层"""
        self.mid_term._save_all()
        print(f"[MemoryOS] Checkpoint saved — ST:{len(self.short_term.get_all())} MT:{len(self.mid_term._memory)} LT:{len(self.long_term.knowledge)}")
```

- [ ] **Step 2: 验证**

Run: `python -c "import sys; sys.path.insert(0, '.workbuddy/记忆层'); from memoryos import MemoryOS; m = MemoryOS('./memory_data'); m.add_memory('test entry', 'episodic'); r = m.search_memory('test'); print(f'Found {len(r)} results'); m.save_checkpoint()"`
Expected: Found 1 results, checkpoint saved

---

### Task 6: Pipeline 串联 — 修改 auto_organizer.py

**Files:**
- Modify: `.workbuddy/scripts/auto_organizer.py`

- [ ] **Step 1: 添加 post_processing 方法**

Add import at top:
```text
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from vector_search import index_file
```

Add method after `execute_plan` (~line 296):
```text
    def post_process(self, plan: OrganizationPlan) -> Dict:
        """处理后操作：索引 + 记忆"""
        from memoryos import MemoryOS
        from datetime import datetime

        target = self.base_path / plan.target_directory / plan.target_name

        # 1. 向量索引
        indexed = index_file(target)

        # 2. 记忆记录
        try:
            mem = MemoryOS(str(self.base_path / ".workbuddy" / "记忆层" / "memory_data"))
            mem.add_memory(
                content=f"[{datetime.now().strftime('%H:%M')}] 处理: {target.name} → {plan.target_directory} [{plan.content_insight.content_type}]",
                memory_type="episodic",
                metadata={"file": str(target), "type": plan.content_insight.content_type}
            )
        except Exception as e:
            print(f"  [memory] skipped: {e}")

        return {"indexed": indexed, "memory_recorded": True}

    def process_and_store(self, file_path: Path, dry_run: bool = False) -> Dict:
        """完整流水线：分析 → 路由 → 移动 → 索引 → 记忆"""
        plan = self.analyze_file(file_path)
        success = self.execute_plan(plan, dry_run=dry_run)

        if success and not dry_run:
            post = self.post_process(plan)
            return {"plan": plan, "executed": True, **post}

        return {"plan": plan, "executed": False}
```

- [ ] **Step 2: 验证导入**

Run: `python -c "import sys; sys.path.insert(0, '.workbuddy/scripts'); from auto_organizer import AutoOrganizer; o = AutoOrganizer('.'); print('import OK')"`
Expected: `import OK`

- [ ] **Step 3: 验证连接**

Run: `python -c "import sys; sys.path.insert(0, '.workbuddy/scripts'); from auto_organizer import AutoOrganizer; from pathlib import Path; o = AutoOrganizer('.'); r = o.process_and_store(Path('01-收件箱/test.md'), dry_run=True); print(r['plan'].reasoning[:50])"`
Expected: 输出推理内容（文件不存在不影响）

---

### Task 7: 创建 Web UI (app.py + 模板)

**Files:**
- Create: `app.py`
- Create: `.workbuddy/templates/index.html`
- Create: `.workbuddy/templates/search.html`
- Create: `.workbuddy/templates/browse.html`

- [ ] **Step 1: 创建 app.py**

Write `app.py`:
```text
#!/usr/bin/env python3
"""
统一入口 — Web UI / REST API / CLI
"""

import sys
import os
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent
sys.path.insert(0, str(WORKSPACE / ".workbuddy" / "scripts"))

from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder=str(WORKSPACE / ".workbuddy" / "templates"))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/search")
def search():
    q = request.args.get("q", "")
    if not q:
        return render_template("search.html", query="", results=[])

    from vector_search import search as vs_search
    results = vs_search(q, top_k=30)
    return render_template("search.html", query=q, results=results)


@app.route("/browse/")
@app.route("/browse/<path:subpath>")
def browse(subpath=""):
    base = WORKSPACE / "05-知识沉淀" / "wiki"
    current = (base / subpath).resolve()

    if not str(current).startswith(str(base)):
        return "Forbidden", 403

    if current.is_file():
        content = current.read_text(encoding="utf-8")
        return render_template("browse.html", path=subpath, content=content, is_file=True)

    items = []
    for child in sorted(current.iterdir()):
        rel = child.relative_to(base)
        items.append({"name": child.name, "path": str(rel), "is_dir": child.is_dir()})
    return render_template("browse.html", path=subpath, items=items, is_file=False)


@app.route("/ingest", methods=["POST"])
def ingest():
    file_path = request.form.get("path", "")
    if not file_path:
        return jsonify({"error": "no path"}), 400

    from auto_organizer import AutoOrganizer
    org = AutoOrganizer(str(WORKSPACE))
    result = org.process_and_store(Path(file_path), dry_run=False)
    return jsonify({"status": "ok", "target": result.get("plan").target_directory if result.get("plan") else None})


@app.route("/memory")
def memory_view():
    from memoryos import MemoryOS
    mem = MemoryOS(str(WORKSPACE / ".workbuddy" / "记忆层" / "memory_data"))
    summary = mem.get_memory_summary()
    return jsonify(summary)


@app.route("/maintain", methods=["POST"])
def maintain():
    from maintenance_task import main as run_maintenance
    run_maintenance()
    return jsonify({"status": "done"})


@app.route("/api/search")
def api_search():
    q = request.args.get("q", "")
    if not q:
        return jsonify({"results": []})
    from vector_search import search as vs_search
    results = vs_search(q, top_k=10)
    return jsonify({"query": q, "results": results})


@app.route("/api/index", methods=["POST"])
def api_rebuild():
    from vector_search import rebuild_index, build_faiss_index, HAS_VECTOR
    count = rebuild_index()
    vec_count = build_faiss_index() if HAS_VECTOR else 0
    return jsonify({"indexed": count, "vectorized": vec_count})


def main():
    import argparse
    parser = argparse.ArgumentParser(description="知识管理工具")
    parser.add_argument("--cli", nargs="+", help="CLI 模式: search '关键词'")
    parser.add_argument("--port", type=int, default=5000, help="Web 端口 (默认 5000)")
    parser.add_argument("--daemon", action="store_true", help="守护进程模式")
    args = parser.parse_args()

    if args.cli:
        cmd = args.cli[0]
        if cmd == "search" and len(args.cli) > 1:
            from vector_search import search as vs_search
            results = vs_search(" ".join(args.cli[1:]))
            for r in results[:10]:
                print(f"[{r['score']:.2f}] {r['path']}")
                print(f"    {r['snippet'][:80]}...")
        return

    print(f"🌐 启动知识管理工具 → http://localhost:{args.port}")
    app.run(host="0.0.0.0", port=args.port, debug=not args.daemon)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 创建 index.html**

Write `.workbuddy/templates/index.html`:
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>知识管理工具</title>
<style>
body { font-family: -apple-system, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; background: #f5f5f5; }
h1 { color: #333; }
.search-box { display: flex; gap: 8px; margin: 20px 0; }
.search-box input { flex: 1; padding: 12px; font-size: 16px; border: 1px solid #ddd; border-radius: 6px; }
.search-box button { padding: 12px 24px; background: #4a90d9; color: #fff; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; margin-top: 30px; }
.card { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.card h3 { margin: 0 0 8px 0; font-size: 16px; }
.card a { color: #4a90d9; text-decoration: none; }
.card a:hover { text-decoration: underline; }
.actions { margin-top: 30px; display: flex; gap: 12px; }
.actions a { padding: 10px 20px; background: #fff; border-radius: 6px; text-decoration: none; color: #333; border: 1px solid #ddd; }
</style>
</head>
<body>
<h1>📚 知识管理工具</h1>

<form class="search-box" action="/search" method="get">
  <input type="text" name="q" placeholder="搜索知识库..." autofocus>
  <button type="submit">搜索</button>
</form>

<div class="cards">
  <div class="card">
    <h3><a href="/browse/">📖 知识图谱</a></h3>
    <p>浏览 wiki 概念、实体、来源</p>
  </div>
  <div class="card">
    <h3><a href="/memory">🧠 记忆系统</a></h3>
    <p>查看记忆状态（JSON）</p>
  </div>
  <div class="card">
    <h3>📥 收件箱</h3>
    <p>路径: <code>01-收件箱/</code></p>
  </div>
  <div class="card">
    <h3>⚡ 维护</h3>
    <p>重建索引 / 清理记忆</p>
  </div>
</div>

<div class="actions">
  <a href="/browse/">浏览 wiki</a>
  <a href="/memory">查看记忆</a>
  <form action="/maintain" method="post" style="display:inline">
    <button type="submit" style="padding:10px 20px;background:#fff;border:1px solid #ddd;border-radius:6px;cursor:pointer;">运行维护</button>
  </form>
</div>
</body>
</html>
```

- [ ] **Step 3: 创建 search.html**

Write `.workbuddy/templates/search.html`:
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>搜索: {{ query }} — 知识管理工具</title>
<style>
body { font-family: -apple-system, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; background: #f5f5f5; }
h1 a { color: #333; text-decoration: none; }
.search-box { display: flex; gap: 8px; margin: 20px 0; }
.search-box input { flex: 1; padding: 12px; font-size: 16px; border: 1px solid #ddd; border-radius: 6px; }
.search-box button { padding: 12px 24px; background: #4a90d9; color: #fff; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; }
.result { background: #fff; padding: 16px; margin: 8px 0; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.result .path { font-size: 12px; color: #888; }
.result .title { font-size: 16px; font-weight: 600; margin: 4px 0; }
.result .title a { color: #1a0dab; text-decoration: none; }
.result .snippet { font-size: 14px; color: #555; }
.result .score { font-size: 12px; color: #999; }
</style>
</head>
<body>
<h1><a href="/">📚</a> 搜索: {{ query }}</h1>

<form class="search-box" action="/search" method="get">
  <input type="text" name="q" value="{{ query }}">
  <button type="submit">搜索</button>
</form>

{% if results %}
<p>找到 {{ results|length }} 个结果</p>
{% for r in results %}
<div class="result">
  <div class="path">{{ r.path }}</div>
  <div class="title"><a href="/browse/{{ r.path }}">{{ r.title }}</a></div>
  <div class="snippet">{{ r.snippet }}</div>
  <div class="score">得分: {{ "%.2f"|format(r.score) }} | {{ r.type }}</div>
</div>
{% endfor %}
{% elif query %}
<p>未找到匹配 "{{ query }}" 的结果</p>
{% endif %}
</body>
</html>
```

- [ ] **Step 4: 创建 browse.html**

Write `.workbuddy/templates/browse.html`:
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{{ path or "wiki" }} — 知识管理工具</title>
<style>
body { font-family: -apple-system, sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; background: #f5f5f5; }
h1 a { color: #333; text-decoration: none; }
.breadcrumb { font-size: 14px; color: #888; margin: 10px 0; }
.breadcrumb a { color: #4a90d9; }
.items { margin: 20px 0; }
.item { padding: 8px 12px; background: #fff; margin: 4px 0; border-radius: 4px; }
.item a { color: #1a0dab; text-decoration: none; }
.item.dir a { font-weight: 600; }
.content { background: #fff; padding: 20px; border-radius: 6px; white-space: pre-wrap; font-size: 14px; line-height: 1.6; overflow-x: auto; }
</style>
</head>
<body>
<h1><a href="/">📚</a> / {{ path or "wiki" }}</h1>

{% if is_file %}
<div class="breadcrumb"><a href="/browse/">wiki</a> / {{ path }}</div>
<div class="content">{{ content }}</div>
{% else %}
<div class="breadcrumb"><a href="/browse/">wiki</a>{% if path %} / {{ path }}{% endif %}</div>
<div class="items">
{% for item in items %}
  <div class="item{% if item.is_dir %} dir{% endif %}">
    <a href="/browse/{{ item.path }}">{{ "📁" if item.is_dir else "📄" }} {{ item.name }}</a>
  </div>
{% endfor %}
</div>
{% endif %}
</body>
</html>
```

- [ ] **Step 5: 验证启动**

Run: `python app.py &`
Expected: `🌐 启动知识管理工具 → http://localhost:5000`

Then test: `python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:5000').status)"`
Expected: `200`

Then stop server: kill the flask process.

---

### Task 8: Inbox Watcher 触发 Pipeline

**Files:**
- Modify: `.workbuddy/scripts/inbox_watcher.py`
- Modify: `.workbuddy/scripts/enhanced_inbox_watcher.py`

- [ ] **Step 1: 修改 inbox_watcher.py**

Add after `generate_intake_report` (before `main`):
```text
def trigger_pipeline(file_path: Path):
    """触发完整处理流水线"""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from auto_organizer import AutoOrganizer
        org = AutoOrganizer(str(WORKSPACE))
        result = org.process_and_store(file_path, dry_run=True)
        print(f"  → pipeline: {result['plan'].reasoning[:60] if result.get('plan') else 'no plan'}")
    except Exception as e:
        print(f"  → pipeline error: {e}")
```

And in `main()`, after `generate_intake_report`, add:
```text
        trigger_pipeline(file_path)
```

Same for `enhanced_inbox_watcher.py`.

- [ ] **Step 2: 验证**

Run: `python -c "import sys; sys.path.insert(0, '.workbuddy/scripts'); from inbox_watcher import trigger_pipeline; from pathlib import Path; trigger_pipeline(Path('.workbuddy/config/domain_keywords.json')); print('trigger OK')"`
Expected: `trigger OK` (pipeline may print info)

---

### Task 9: 更新 Maintenance 和 Update Index

**Files:**
- Modify: `.workbuddy/scripts/maintenance_task.py`
- Modify: `.workbuddy/scripts/update_index.py`

- [ ] **Step 1: 在 maintenance_task.py 中增加 memory 清理 + 索引重建**

In `main()` add after existing steps:
```text
    from memoryos import MemoryOS
    mem = MemoryOS(str(WORKSPACE / ".workbuddy" / "记忆层" / "memory_data"))
    mem.save_checkpoint()

    from vector_search import rebuild_index, build_faiss_index, HAS_VECTOR
    count = rebuild_index()
    if HAS_VECTOR:
        vec_count = build_faiss_index()
        print(f"  向量索引: {vec_count} 条")
```

- [ ] **Step 2: 扩展 update_index.py 的扫描范围**

In `update_index.py`, change `SCAN_DIRS` to include more dirs:
```text
SCAN_DIRS = [
    WORKSPACE / "01-收件箱",
    WORKSPACE / "02-对话记录",
    WORKSPACE / "03-资产库",
    WORKSPACE / "04-输出成果",
    WORKSPACE / "05-知识沉淀",
    WORKSPACE / "06-参考资料",
    WORKSPACE / "07-项目文档",
]
```

Also add vector_search index rebuild at end of `update_index()`:
```text
    try:
        from vector_search import rebuild_index, build_faiss_index, HAS_VECTOR
        count = rebuild_index(SCAN_DIRS)
        if HAS_VECTOR:
            v = build_faiss_index()
            print(f"  向量索引已更新: {v} 条")
    except Exception as e:
        print(f"  向量索引失败: {e}")
```

- [ ] **Step 3: 验证**

Run: `python .workbuddy/scripts/update_index.py`
Expected: Scans all directories, updates AGENTS.md timestamps

---

### Task 10: 集成验证

- [ ] **Step 1: 验证所有脚本导入**

Run:
```powershell
$scripts = @(
    "search_content", "update_index", "maintenance_task", "inbox_watcher",
    "enhanced_inbox_watcher", "extract_docx", "content_analyzer",
    "naming_optimizer", "auto_organizer", "smart_router",
    "file_processing_pipeline", "project_relationship_manager",
    "project_decision_workflow", "vector_search"
)
foreach ($s in $scripts) {
    python -c "import sys; sys.path.insert(0, '.workbuddy/scripts'); import $s; print('OK: $s')"
}
```
Expected: 15 OK

- [ ] **Step 2: 验证索引构建**

Run: `python .workbuddy/scripts/vector_search.py rebuild`
Expected: `索引了 N 个文件`

- [ ] **Step 3: 验证搜索**

Run: `python .workbuddy/scripts/vector_search.py search "知识"`
Expected: 搜索结果列表

- [ ] **Step 4: 验证 Web 启动**

Run: `python app.py` (briefly, then Ctrl+C)
Expected: `🌐 启动知识管理工具 → http://localhost:5000`

---

## 执行总结

| Task | 内容 | 文件数 | 代码量(估) |
|------|------|--------|-----------|
| 1 | 目录 + 依赖 + config | 3 dirs + 2 files | ~20 行 |
| 2 | vector_search.py | 1 new file | ~250 行 |
| 3 | SmartRouter 修复 | 1 modified | ~30 行 |
| 4 | ContentAnalyzer 去领域化 | 1 modified | ~20 行 |
| 5 | MemoryOS 激活 | 1 modified | ~40 行 |
| 6 | Pipeline 串联 | 1 modified | ~60 行 |
| 7 | Web UI | 1 + 3 new files | ~200 行 |
| 8 | Watcher 触发 | 2 modified | ~30 行 |
| 9 | Maintenance 扩展 | 2 modified | ~30 行 |
| 10 | 集成验证 | — | — |
| **总计** | | **~17 文件** | **~680 行** |

---

**Plan complete and saved. Two execution options:**

1. **Subagent-Driven (recommended)** — 逐任务分配子代理，快速迭代，每步验证
2. **Inline Execution** — 在当前会话中批量执行

Which approach?
