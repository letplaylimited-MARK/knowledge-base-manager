#!/usr/bin/env python3
# Weekly Maintenance Task
# 1. Update index
# 2. Clean orphan tags
# 3. Backup database
# 4. Detect changes

import subprocess
import json
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent.parent  # 从 .workbuddy/scripts/ 向上三级
BACKUP_DIR = WORKSPACE / ".workbuddy" / "backup"
TAG_FILE = WORKSPACE / ".workbuddy" / "scripts" / "knowledge_db" / "tag_ontology.json"


def update_index():
    """Run index update script"""
    print("1. Updating index...")
    update_script = WORKSPACE / ".workbuddy" / "scripts" / "update_index.py"
    subprocess.run([sys.executable, str(update_script)], check=True)
    print("   Index updated")


def clean_orphans():
    """Clean orphan tags"""
    print("2. Cleaning orphan tags...")

    if TAG_FILE.exists():
        with open(TAG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Remove tags with 0 usage
        cleaned = False
        if "tags" in data:
            original_count = len(data["tags"])
            data["tags"] = [t for t in data["tags"] if t.get("usage_count", 0) > 0]
            cleaned = len(data["tags"]) < original_count

        if cleaned:
            with open(TAG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"   Cleaned {original_count - len(data['tags'])} orphan tags")
        else:
            print("   No orphans found")
    else:
        print("   Tag file not found")


def backup():
    """Backup knowledge database"""
    print("3. Creating backup...")

    if not BACKUP_DIR.exists():
        BACKUP_DIR.mkdir(parents=True)

    timestamp = datetime.now().strftime("%Y%m%d")
    backup_file = BACKUP_DIR / f"knowledge_backup_{timestamp}.json"

    # Collect data
    backup_data = {"timestamp": timestamp, "files": [], "entities": [], "relations": []}

    # Scan key files
    key_files = ["AGENTS.md", ".workbuddy/AI协作体系/AI协作/知识图谱.md", ".workbuddy/AI协作体系/AI协作/工作流程.md"]

    for f in key_files:
        file_path = WORKSPACE / f
        if file_path.exists():
            backup_data["files"].append(
                {
                    "file": f,
                    "modified": datetime.fromtimestamp(
                        file_path.stat().st_mtime
                    ).isoformat(),
                }
            )

    # Save backup
    with open(backup_file, "w", encoding="utf-8") as f:
        json.dump(backup_data, f, ensure_ascii=False, indent=2)

    print(f"   Backup: {backup_file.name}")

    # Keep only last 5 backups
    backups = sorted(BACKUP_DIR.glob("knowledge_backup_*.json"))
    for old in backups[:-5]:
        old.unlink()
        print(f"   Deleted old: {old.name}")


def detect_changes():
    """Detect file changes"""
    print("4. Detecting changes...")

    entity_file = WORKSPACE / "05-知识沉淀" / "wiki" / "index.md"
    if entity_file.exists():
        modified = datetime.fromtimestamp(entity_file.stat().st_mtime)
        days_ago = (datetime.now() - modified).days

        if days_ago <= 7:
            print(f"   entity file modified {days_ago} days ago - may need update")
        else:
            print(f"   entity file stable ({days_ago} days ago)")


def main():
    """Run all maintenance tasks"""
    print(f"Starting maintenance at {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    try:
        update_index()
        clean_orphans()
        backup()
        detect_changes()

        # 新增: 记忆 checkpoint + 向量索引重建
        try:
            from path_setup import setup_scripts_only; setup_scripts_only()
            from memoryos import MemoryOS
            mem = MemoryOS(str(WORKSPACE / ".workbuddy" / "记忆层" / "memory_data"))
            mem.save_checkpoint()
        except Exception as e:
            print(f"  memory: {e}")

        try:
            from vector_search import rebuild_index, build_faiss_index, HAS_VECTOR
            count = rebuild_index()
            if HAS_VECTOR:
                vec_count = build_faiss_index()
                print(f"  向量索引: {vec_count} 条")
            else:
                print(f"  关键词索引: {count} 个文件")
        except Exception as e:
            print(f"  index: {e}")

        print("=" * 50)
        print("Maintenance complete!")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
