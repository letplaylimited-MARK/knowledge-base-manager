#!/usr/bin/env python3
"""
向量语义搜索引擎 — FAISS + sentence-transformers + SQLite
"""

import sqlite3
import os
import logging
import numpy as np
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)

WORKSPACE = Path(__file__).resolve().parent.parent.parent
INDEX_DIR = WORKSPACE / ".workbuddy" / "index"
DB_PATH = INDEX_DIR / "search_index.db"
_FAISS_PATH = INDEX_DIR / "vectors.faiss"
if str(_FAISS_PATH).isascii():
    FAISS_PATH = _FAISS_PATH
else:
    # faiss's C fopen() can't handle non-ASCII paths on Windows
    FAISS_PATH = Path(os.environ.get("TEMP", os.environ.get("TMPDIR", "/tmp"))) / "km_vectors.faiss"

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    HAS_VECTOR = True
except ImportError:
    HAS_VECTOR = False

_model = None

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
    return _model


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
    rel_path = os.path.relpath(str(file_path), str(WORKSPACE))
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
    try:
        conn.execute("DELETE FROM documents")
        conn.commit()
    finally:
        conn.close()
    if FAISS_PATH.exists():
        try:
            FAISS_PATH.unlink()
        except Exception:
            logger.warning(f"无法删除旧 FAISS 索引文件 {FAISS_PATH}，可能引起索引不同步")
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
    conn = _get_db()
    try:
        rows = conn.execute(
            "SELECT path, title, content_preview, file_type FROM documents WHERE title LIKE ? OR content_preview LIKE ?",
            (f"%{query}%", f"%{query}%")
        ).fetchall()
        results = []
        for path, title, preview, file_type in rows:
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
        model = _get_model()
        index = faiss.read_index(str(FAISS_PATH))
        query_vec = model.encode([query])
        distances, indices = index.search(np.array(query_vec).astype("float32"), top_k)
        conn = _get_db()
        try:
            rows = conn.execute("SELECT rowid, path, title, content_preview, file_type FROM documents").fetchall()
            row_map = {r[0]: {"path": r[1], "title": r[2], "snippet": r[3], "type": r[4]} for r in rows}
        finally:
            conn.close()
        results = []
        for i, idx in enumerate(indices[0]):
            if idx in row_map:
                entry = row_map[idx]
                results.append({
                    "path": entry["path"], "title": entry["title"],
                    "snippet": entry["snippet"][:200], "type": entry["type"],
                    "score": float(distances[0][i]),
                })
        return results
    except Exception as e:
        import sys
        print(f"[vector_search] 向量搜索失败, 回退到关键词: {e}", file=sys.stderr)
        return search_keyword(query, top_k)


def build_faiss_index() -> int:
    """从磁盘全文重建 FAISS 向量索引（使用 rowid 作为 ID）"""
    if not HAS_VECTOR:
        return 0
    model = _get_model()
    conn = _get_db()
    try:
        rows = conn.execute("SELECT rowid, path FROM documents").fetchall()
    finally:
        conn.close()
    if not rows:
        return 0
    rowids = []
    texts = []
    for rowid, path in rows:
        full_path = WORKSPACE / path
        try:
            text = full_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            text = ""
        rowids.append(rowid)
        texts.append(text)
    embeddings = model.encode(texts, show_progress_bar=False)
    dim = embeddings.shape[1]
    base_index = faiss.IndexFlatL2(dim)
    index = faiss.IndexIDMap(base_index)
    index.add_with_ids(np.array(embeddings).astype("float32"), np.array(rowids).astype("int64"))
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
