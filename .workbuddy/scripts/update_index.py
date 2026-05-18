#!/usr/bin/env python3
# Knowledge Base Index Auto-Update Script
# Scans Prompt directory and auto-updates AGENTS.md

import os
import re
import sys
from datetime import datetime
from pathlib import Path

# Config
WORKSPACE = Path(__file__).resolve().parent.parent.parent  # 从 .workbuddy/scripts/ 向上三级
AGENTS_FILE = WORKSPACE / "AGENTS.md"
SCAN_DIRS = [
    WORKSPACE / "01-收件箱",
    WORKSPACE / "02-对话记录",
    WORKSPACE / "03-资产库",
    WORKSPACE / "04-输出成果",
    WORKSPACE / "05-知识沉淀",
    WORKSPACE / "06-参考资料",
    WORKSPACE / "07-项目文档",
]


def extract_file_metadata(file_path):
    """Extract metadata from file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read(2000)

        tags = []
        if "ai" in content.lower() or "AI" in content:
            tags.append("ai")
        if "知识" in content or "knowledge" in content.lower():
            tags.append("knowledge")
        if "配置" in content or "config" in content.lower():
            tags.append("config")
        if "验证" in content or "test" in content.lower():
            tags.append("verification")

        return {"size": len(content), "tags": tags}
    except Exception:
        return {"size": 0, "tags": []}


def scan_directory():
    """Scan all project directories for documentation"""
    print(f"Scanning {len(SCAN_DIRS)} directories...")
    indexed_files = []
    
    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            print(f"  ⚠️  Directory not found: {scan_dir.name}")
            continue
            
        files_found = list(scan_dir.rglob("*.md")) + list(scan_dir.rglob("*.py"))
        for f in files_found:
            rel_path = str(f.relative_to(WORKSPACE))
            indexed_files.append({
                "path": rel_path,
                "name": f.stem,
                "ext": f.suffix,
                "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            })
    
    return indexed_files


def print_summary(files):
    """Print index summary"""
    md_count = sum(1 for f in files if f["ext"] == ".md")
    py_count = sum(1 for f in files if f["ext"] == ".py")
    
    print(f"\n{'='*40}")
    print(f"[索引更新报告]")
    print(f"{'='*40}")
    print(f"  总文件数: {len(files)}")
    print(f"  Markdown: {md_count}")
    print(f"  Python:   {py_count}")
    print(f"  更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*40}")
    
    from collections import defaultdict
    dirs = defaultdict(list)
    for f in files:
        parent = str(Path(f["path"]).parent)
        dirs[parent].append(f["name"])
    
    print("\n目录分布:")
    for d, names in sorted(dirs.items()):
        print(f"  {d}/ -- {len(names)} 个文件")


def update_index():
    """Main index update function"""
    print("[更新知识索引]\n")
    files = scan_directory()
    print_summary(files)
    
    if AGENTS_FILE.exists():
        with open(AGENTS_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        
        today = datetime.now().strftime('%Y-%m-%d')
        content = re.sub(r"知识索引: \d{4}-\d{2}-\d{2}", f"知识索引: {today}", content)
        content = re.sub(r"系统结构: \d{4}-\d{2}-\d{2}", f"系统结构: {today}", content)
        content = re.sub(r"AI配置: \d{4}-\d{2}-\d{2}", f"AI配置: {today}", content)
        
        with open(AGENTS_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        print("\nAGENTS.md 时间戳已更新")
    
    # 重建向量索引
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from vector_search import rebuild_index as vs_rebuild, build_faiss_index, HAS_VECTOR
        count = vs_rebuild(SCAN_DIRS)
        if HAS_VECTOR:
            v = build_faiss_index()
            print(f"  向量索引已更新: {v} 条")
    except Exception as e:
        print(f"  向量索引失败: {e}")
    
    return files


if __name__ == "__main__":
    update_index()
