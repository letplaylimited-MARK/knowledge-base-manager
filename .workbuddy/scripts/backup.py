#!/usr/bin/env python3
"""
增量备份脚本
备份工作台重要文件
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).resolve().parent.parent.parent  # 从 .workbuddy/脚本/ 向上三级到工作区根目录
BACKUP_ROOT = WORKSPACE / ".workbuddy" / "backup"

def backup_files(backup_type='daily'):
    """执行备份"""
    today = datetime.now()
    
    # 创建备份目录
    if backup_type == 'daily':
        backup_dir = BACKUP_ROOT / "daily" / today.strftime('%Y-%m-%d')
    elif backup_type == 'weekly':
        week = today.isocalendar()[1]
        backup_dir = BACKUP_ROOT / "weekly" / f"{today.year}-W{week:02d}"
    else:
        backup_dir = BACKUP_ROOT / "monthly" / today.strftime('%Y-%m')
    
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    # 需要备份的目录
    dirs_to_backup = [
        ('03-资产库', '资产库'),
        ('05-知识沉淀', '知识沉淀'),
        ('07-项目文档', '项目文档'),
        ('.workbuddy', '系统核心'),
        ('AGENTS.md', '索引配置'),
    ]
    
    print(f"开始备份到: {backup_dir}")
    
    for item, desc in dirs_to_backup:
        src = WORKSPACE / item
        if src.exists():
            dest = backup_dir / item.replace('/', '_')
            if src.is_dir():
                shutil.copytree(src, dest, dirs_exist_ok=True)
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
            print(f"  [OK] {desc}")

    print(f"备份完成! -> {backup_dir}")

if __name__ == "__main__":
    import sys
    backup_type = sys.argv[1] if len(sys.argv) > 1 else 'daily'
    backup_files(backup_type)
