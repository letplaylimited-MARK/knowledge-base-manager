#!/usr/bin/env python3
"""
统一入口 — Web UI / REST API / CLI
"""

import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent
sys.path.insert(0, str(WORKSPACE / ".workbuddy" / "scripts"))
sys.path.insert(0, str(WORKSPACE / ".workbuddy" / "记忆层"))

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
    parser.add_argument("--no-bootstrap", action="store_true", help="跳过开箱即用引导")
    parser.add_argument("--bootstrap-force", action="store_true", help="强制重建引导数据")
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

    # 开箱即用引导：自动创建 demo 数据 + 构建搜索索引
    if not args.no_bootstrap:
        try:
            from bootstrap import bootstrap, print_bootstrap_report
            print("\n[开箱即用引导] 检查环境...")
            result = bootstrap(force=args.bootstrap_force)
            print_bootstrap_report(result)
        except ImportError:
            print("\n[开箱即用引导] 跳过（bootstrap 模块未找到）")
        except Exception as e:
            print(f"\n[开箱即用引导] 警告: {e}")

    print(f"启动知识管理工具 -> http://localhost:{args.port}")
    app.run(host="127.0.0.1", port=args.port, debug=not args.daemon)


if __name__ == "__main__":
    main()
