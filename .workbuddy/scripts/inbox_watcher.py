#!/usr/bin/env python3
# New File Inbox Watcher
# Monitors 01-收件箱/ for new files and generates intake recommend

import hashlib
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent  # 从 .workbuddy/scripts/ 向上三级
INBOX = WORKSPACE / "01-收件箱"
OUTPUT_DIR = WORKSPACE / "01-收件箱" / "待处理"

# Known tags for matching
TAG_KEYWORDS = {
    "数据分析": ["日报", "数据", "报告", "Excel", "xlsx", "csv"],
    "风控审核": ["风控", "审核", "聊天记录", "合规"],
    "制度文档": ["制度", "规则", "结算", "提成", "运营"],
    "培训资料": ["培训", "教学", "SOP", "手册"],
    "AI话术": ["话术", "AI", "聊天", "Prompt"],
    "视频教程": ["视频", "教程", "mp4"],
}

FILE_TYPE_MAP = {
    ".xlsx": "数据分析",
    ".xls": "数据分析",
    ".csv": "数据分析",
    ".docx": "文档",
    ".doc": "文档",
    ".html": "文档",
    ".pdf": "文档",
    ".md": "文档",
    ".txt": "文档",
}

# Existing entity tags
ENTITY_TAGS = ["R5+", "14W线", "结算门槛", "提成档位", "福利期", "新人扶持"]


def get_file_hash(file_path):
    """Calculate MD5 hash"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def read_file_preview(file_path, max_chars=500):
    """Read first N chars from file"""
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read(max_chars)
    except (OSError, UnicodeDecodeError):
        return ""


def match_tags(content):
    """Match content to known tags"""
    matched = []
    content_lower = content.lower()

    for tag, keywords in TAG_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in content_lower:
                matched.append(tag)
                break

    # Check for entity tags
    for entity in ENTITY_TAGS:
        if entity in content:
            matched.append(f"#{entity}")

    return list(set(matched)) if matched else ["待确认"]


def recommend_target_dir(file_type, tags):
    """Recommend target directory"""
    if "概念" in tags or "定义" in tags:
        return "05-知识沉淀/wiki/concepts/"
    if "来源" in tags or "参考" in tags:
        return "05-知识沉淀/wiki/sources/"
    if "比较" in tags or "对比" in tags:
        return "05-知识沉淀/wiki/comparisons/"
    if "AI" in tags or "模型" in tags:
        return "03-资产库/AI技能/"
    if "数据" in tags or "分析" in tags:
        return "04-输出成果/报告/"
    if "项目" in tags or "需求" in tags:
        return "07-项目文档/"

    return "01-收件箱/"


def generate_intake_report(file_path, tags):
    """Generate intake recommendation report"""
    name = file_path.name
    size = file_path.stat().st_size
    modified = datetime.fromtimestamp(file_path.stat().st_mtime)

    target_dir = recommend_target_dir(file_path.suffix, tags)
    target_path = target_dir + name

    report = f"""# 新文件入库建议

**文件名**: {name}
**大小**: {size:,} bytes
**修改时间**: {modified.strftime("%Y-%m-%d %H:%M")}
**文件类型**: {file_path.suffix}

## 标签推荐
{", ".join(tags)}

## 建议目标目录
`{target_dir}`

## 完整路径
`{target_path}`

## 操作建议
1. 确认标签是否正确
2. 确认目标目录
3. 移动文件到目标目录
4. 如需提取内容，运行 content_analyzer.py
"""
    return report


def scan_inbox():
    """Scan inbox for new files"""
    new_files = []

    if not OUTPUT_DIR.exists():
        OUTPUT_DIR.mkdir(parents=True)

    for file_path in INBOX.rglob("*"):
        if file_path.is_file() and not file_path.name.startswith("."):
            new_files.append(
                {
                    "path": str(file_path),
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "type": file_path.suffix,
                }
            )

    return new_files


def trigger_pipeline(file_path: Path):
    """触发完整处理流水线"""
    try:
        from path_setup import setup_scripts_only; setup_scripts_only()
        from auto_organizer import AutoOrganizer
        from memoryos import MemoryOS
        org = AutoOrganizer(str(WORKSPACE))
        result = org.process_and_store(file_path, dry_run=True)
        plan = result.get("plan")
        if plan:
            print(f"  -> pipeline: {plan.reasoning[:60]}")
        # 记忆记录
        mem = MemoryOS(str(WORKSPACE / ".workbuddy" / "记忆层" / "memory_data"))
        mem.add_memory(
            content=f"[watcher] 发现: {file_path.name}",
            memory_type="episodic",
            metadata={"file": str(file_path)}
        )
    except Exception as e:
        print(f"  -> pipeline error: {e}")


def main():
    print("Scanning inbox...")
    files = scan_inbox()
    print(f"Found {len(files)} files")

    for f in files[:5]:  # Process first 5
        file_path = Path(f["path"])
        content = read_file_preview(file_path)
        tags = match_tags(content)
        report = generate_intake_report(file_path, tags)
        trigger_pipeline(file_path)

        # Save report
        report_file = OUTPUT_DIR / f"{file_path.stem}-入库建议.md"
        with open(report_file, "w", encoding="utf-8") as wf:
            wf.write(report)

        print(f"Generated: {report_file.name}")


if __name__ == "__main__":
    main()
