#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量文件导入处理器 CLI 入口
从 01-收件箱/批量导入处理器.md 提取的实现
"""

import os
import sys
from pathlib import Path

# 自举路径
SCRIPTS_DIR = Path(__file__).resolve().parent / ".workbuddy" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from path_setup import setup  # noqa: E402
setup()

from auto_organizer import AutoOrganizer  # noqa: E402
from content_analyzer import ContentAnalyzer  # noqa: E402


class BatchImporter:
    """批量文件导入器"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.organizer = AutoOrganizer(self.base_path)
        self.analyzer = ContentAnalyzer()
        self.stats = {"total": 0, "success": 0, "skipped": 0, "failed": 0}

    def import_directory(self, source_dir: str) -> dict:
        """导入整个目录的文件"""
        files = list(Path(source_dir).glob("*"))
        self.stats["total"] = len(files)

        for file_path in files:
            if not file_path.is_file():
                continue
            try:
                result = self.organizer.process_and_store(file_path, dry_run=False)
                if result.get("executed"):
                    self.stats["success"] += 1
                else:
                    self.stats["skipped"] += 1
            except Exception as e:
                self.stats["failed"] += 1
                print(f"导入失败: {file_path} - {e}")

        return self.stats

    def preview_import(self, source_dir: str) -> list:
        """预览导入计划（dry-run）"""
        plans = []
        for file_path in Path(source_dir).glob("*"):
            if file_path.is_file():
                insight = self.analyzer.analyze_file(file_path)
                plans.append({
                    "file": str(file_path),
                    "topic": insight.core_topic,
                    "type": insight.content_type,
                    "confidence": insight.confidence
                })
        return plans


def main():
    importer = BatchImporter(os.getcwd())
    if len(sys.argv) > 1:
        result = importer.import_directory(sys.argv[1])
        print(f"导入完成: {result}")
    else:
        print("用法: python batch_import.py <目录路径>")


if __name__ == "__main__":
    main()
