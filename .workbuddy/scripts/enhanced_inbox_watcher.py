#!/usr/bin/env python3
"""
增强版收件箱监控器
监控新文件 → 自动分析 → 生成处理建议
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).resolve().parent.parent.parent  # 从 .workbuddy/scripts/ 向上三级
INBOX = WORKSPACE / "01-收件箱"
TRACKING_FILE = WORKSPACE / ".workbuddy" / "inbox_tracking.json"

def get_file_hash(file_path):
    """计算文件哈希"""
    h = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            h.update(f.read())
        return h.hexdigest()
    except OSError:
        return None

def analyze_file(file_path):
    """分析文件内容，返回分类建议"""
    suggestions = []

    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')

        # 关键词匹配
        keywords = {
            '05-知识沉淀/wiki/concepts/': ['概念', '定义', '知识', '术语'],
            '05-知识沉淀/wiki/sources/': ['来源', '参考', '引用', '来源'],
            '05-知识沉淀/wiki/comparisons/': ['比较', '对比', 'vs', '异同'],
            '03-资产库/AI技能/': ['prompt', '提示词', 'ai', '模型', '技能'],
            '07-项目文档/': ['项目', '方案', '需求', '设计'],
        }

        content_lower = content.lower()
        for folder, kws in keywords.items():
            for kw in kws:
                if kw.lower() in content_lower:
                    suggestions.append(folder)
                    break

        if not suggestions:
            suggestions.append('05-知识沉淀/')

    except Exception:
        suggestions.append('待确认')

    return suggestions[:3]  # 最多3个建议

def scan_inbox():
    """扫描收件箱"""
    new_files = []

    for file_path in INBOX.rglob('*'):
        if file_path.is_dir():
            continue

        # 读取追踪记录
        tracking = {}
        if TRACKING_FILE.exists():
            with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
                tracking = json.load(f)

        file_hash = get_file_hash(file_path)
        file_key = str(file_path.relative_to(INBOX))

        # 检查是否新文件
        if file_key not in tracking or tracking[file_key]['hash'] != file_hash:
            analysis = analyze_file(file_path)
            new_files.append({
                'name': file_path.name,
                'path': str(file_path.relative_to(WORKSPACE)),
                'hash': file_hash,
                'suggested': analysis,
                'date': datetime.now().strftime('%Y-%m-%d')
            })

            # 更新追踪
            tracking[file_key] = {
                'hash': file_hash,
                'date': datetime.now().strftime('%Y-%m-%d')
            }

    # 保存追踪记录
    TRACKING_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(TRACKING_FILE, 'w', encoding='utf-8') as f:
        json.dump(tracking, f, ensure_ascii=False, indent=2)

    return new_files

def trigger_pipeline(file_path: Path):
    """触发完整处理流水线"""
    try:
        from path_setup import setup_scripts_only  # noqa: E402
        setup_scripts_only()
        from auto_organizer import AutoOrganizer
        org = AutoOrganizer(str(WORKSPACE))
        result = org.process_and_store(file_path, dry_run=True)
        plan = result.get("plan")
        if plan:
            print(f"  -> pipeline: {plan.reasoning[:60]}")
    except Exception as e:
        print(f"  -> pipeline error: {e}")

def main():
    print("=" * 50)
    print("收件箱监控报告")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    new_files = scan_inbox()

    if new_files:
        print(f"\n发现 {len(new_files)} 个文件:")
        for f in new_files:
            print(f"\n📄 {f['name']}")
            print(f"   路径: {f['path']}")
            print("   建议分类:")
            for s in f['suggested']:
                print(f"   - {s}")
            trigger_pipeline(WORKSPACE / f['path'])
    else:
        print("\n没有发现新文件")

    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
