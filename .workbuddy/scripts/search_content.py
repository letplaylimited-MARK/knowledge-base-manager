#!/usr/bin/env python3
"""
全文检索系统 - 搜索工作台内容
用法: python search.py "关键词"
"""

import os
import re
import sys
from pathlib import Path
import io

# 设置UTF-8输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 配置
WORKSPACE = Path(__file__).resolve().parent.parent.parent  # 从 .workbuddy/scripts/ 向上三级
IGNORE_DIRS = {'.git', '.workbuddy', '__pycache__', 'node_modules', '.venv'}
IGNORE_EXTS = {'.exe', '.dll', '.pak', '.map', '.png', '.jpg', '.jpeg', '.gif', '.mp4', '.zip', '.7z'}

def search_content(query, max_results=50):
    """搜索文件内容"""
    results = []
    query_lower = query.lower()
    
    for file_path in WORKSPACE.rglob('*'):
        # 跳过目录
        if file_path.is_dir():
            continue
        
        # 跳过忽略的目录
        if any(ignored in file_path.parts for ignored in IGNORE_DIRS):
            continue
        
        # 跳过忽略的扩展名
        if file_path.suffix.lower() in IGNORE_EXTS:
            continue
        
        # 跳过临时文件
        if file_path.name.startswith('~$'):
            continue
        
        try:
            # 读取文件内容
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            content_lower = content.lower()
            
            # 搜索匹配
            if query_lower in content_lower:
                # 计算出现次数
                count = content_lower.count(query_lower)
                
                # 获取上下文
                lines = content.split('\n')
                matches = []
                for i, line in enumerate(lines, 1):
                    if query_lower in line.lower():
                        # 截取上下文
                        snippet = line.strip()[:200]
                        matches.append(f"  行{i}: {snippet}")
                        if len(matches) >= 3:  # 最多3条匹配
                            break
                
                rel_path = file_path.relative_to(WORKSPACE)
                results.append({
                    'path': str(rel_path),
                    'abs_path': str(file_path),
                    'count': count,
                    'matches': matches[:3],
                    'size': file_path.stat().st_size
                })
                
        except Exception:
            pass
    
    return results

def search_filename(query):
    """搜索文件名"""
    results = []
    query_lower = query.lower()
    
    for file_path in WORKSPACE.rglob('*'):
        if file_path.is_dir():
            continue
        
        if any(ignored in file_path.parts for ignored in IGNORE_DIRS):
            continue
        
        if query_lower in file_path.name.lower():
            rel_path = file_path.relative_to(WORKSPACE)
            results.append({
                'path': str(rel_path),
                'name': file_path.name,
                'size': file_path.stat().st_size if file_path.exists() else 0
            })
    
    return results

def print_results(content_results, filename_results, query):
    """打印搜索结果"""
    print(f"\n{'='*60}")
    print(f"[搜索] {query}")
    print(f"{'='*60}")
    
    # 文件名搜索结果
    if filename_results:
        print(f"\n[文件名匹配] ({len(filename_results)} 个):")
        print("-" * 40)
        for r in filename_results[:20]:
            print(f"  * {r['path']}")
    
    # 内容搜索结果
    if content_results:
        print(f"\n[内容匹配] ({len(content_results)} 个):")
        print("-" * 40)
        for r in content_results[:20]:
            print(f"\n  {r['path']}")
            print(f"     匹配次数: {r['count']}")
            for match in r['matches']:
                print(match)
    
    if not content_results and not filename_results:
        print("\n[未找到匹配结果]")
    
    print(f"\n{'='*60}")

def main():
    if len(sys.argv) < 2:
        print("用法: python search.py \"关键词\"")
        print("示例: python search.py \"R5+\"")
        print("      python search.py \"14W线\"")
        sys.exit(1)
    
    query = sys.argv[1]
    
    # 执行搜索
    content_results = search_content(query)
    filename_results = search_filename(query)
    
    # 打印结果
    print_results(content_results, filename_results, query)

if __name__ == "__main__":
    main()
