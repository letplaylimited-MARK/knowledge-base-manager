#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识数据库 - 文件扫描器
自动扫描收件箱，提取元数据，推荐标签
"""

import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class FileScanner:
    """文件扫描器 - 检测新文件并提取基础元数据"""
    
    def __init__(self, base_path: str, ontology_path: str):
        self.base_path = Path(base_path)
        self.inbox_path = self.base_path / "01-收件箱"
        self.ontology = self._load_ontology(ontology_path)
        self.supported_extensions = {'.txt', '.md', '.docx', '.xlsx', '.csv', '.json', '.html', '.pdf'}
        
    def _load_ontology(self, path: str) -> Dict:
        """加载标签本体库"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载本体库失败: {e}")
            return {}
    
    def _calculate_hash(self, file_path: Path) -> str:
        """计算文件哈希（用于去重）"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _extract_content_preview(self, file_path: Path, max_chars: int = 1000) -> str:
        """提取文件内容预览"""
        try:
            if file_path.suffix == '.txt' or file_path.suffix == '.md':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read(max_chars)
            elif file_path.suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return json.dumps(data, ensure_ascii=False)[:max_chars]
            else:
                return f"[{file_path.suffix} 文件，需专用工具解析]"
        except Exception as e:
            return f"[读取失败: {e}]"
    
    def _recommend_tags(self, file_path: Path, content_preview: str) -> List[Dict]:
        """基于规则推荐标签"""
        recommendations = []
        filename_lower = file_path.name.lower()
        content_lower = content_preview.lower()
        
        rules = self.ontology.get('auto_tag_rules', [])
        
        for rule in rules:
            condition = rule['condition']
            tags = rule['tags']
            confidence = rule['confidence']
            
            # 简单的条件评估（实际可扩展为更复杂的规则引擎）
            matched = False
            
            if 'filename contains' in condition:
                keyword = condition.split("'")[1] if "'" in condition else condition.split('"')[1]
                if keyword.lower() in filename_lower:
                    matched = True
                    
            elif 'content contains' in condition:
                keyword = condition.split("'")[1] if "'" in condition else condition.split('"')[1]
                if keyword.lower() in content_lower:
                    matched = True
                    
            elif 'extension is' in condition:
                ext = condition.split("'")[1] if "'" in condition else condition.split('"')[1]
                if file_path.suffix == ext:
                    matched = True
                    
            elif 'path contains' in condition:
                path_keyword = condition.split("'")[1] if "'" in condition else condition.split('"')[1]
                if path_keyword in str(file_path):
                    matched = True
            
            if matched:
                for tag in tags:
                    recommendations.append({
                        'tag': tag,
                        'confidence': confidence,
                        'source': 'auto_rule',
                        'rule': condition
                    })
        
        # 去重，保留最高置信度
        tag_map = {}
        for rec in recommendations:
            tag = rec['tag']
            if tag not in tag_map or rec['confidence'] > tag_map[tag]['confidence']:
                tag_map[tag] = rec
        
        return list(tag_map.values())
    
    def _extract_entities(self, content: str) -> List[Dict]:
        """简单实体提取（可扩展为NER模型）"""
        entities = []
        
        # 主播名模式（如：主播Sasa、Sasa）
        import re
        anchor_pattern = r'主播\s*([A-Za-z\u4e00-\u9fa5]+)|([A-Za-z]+)(?=主播|诊断)'
        for match in re.finditer(anchor_pattern, content):
            name = match.group(1) or match.group(2)
            if name and len(name) > 1:
                entities.append({
                    'name': name,
                    'type': 'PERSON',
                    'role': '主播',
                    'context': match.group(0)
                })
        
        # 指标模式（如：288542钻石、14W、R5收入）
        metric_patterns = [
            (r'(\d{3,})\s*钻石', '钻石', '收入'),
            (r'(\d+)\s*W', '万钻', '收入'),
            (r'R5\+?\s*收入?', 'R5收入', '指标'),
            (r'14W\s*线?', '14W线', '指标'),
            (r'SF\s*系数?', 'SF系数', '指标'),
        ]
        for pattern, name, category in metric_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                entities.append({
                    'name': name,
                    'type': 'METRIC',
                    'value': match.group(1) if match.groups() else match.group(0),
                    'category': category
                })
        
        # 概念模式
        concept_patterns = [
            (r'identity[_\-]?confirmed', 'identity_confirmed', '状态'),
            (r'agen|gen\b', 'agen/gen', '风险词'),
            (r'结构闸门', '结构闸门', '规则'),
        ]
        for pattern, name, category in concept_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                entities.append({
                    'name': name,
                    'type': 'CONCEPT',
                    'category': category
                })
        
        return entities
    
    def scan_inbox(self) -> List[Dict[str, Any]]:
        """扫描收件箱，返回新文件列表"""
        new_files = []
        
        if not self.inbox_path.exists():
            print(f"收件箱不存在: {self.inbox_path}")
            return new_files
        
        for item in self.inbox_path.rglob('*'):
            if item.is_file() and item.suffix.lower() in self.supported_extensions:
                # 跳过隐藏文件
                if item.name.startswith('.'):
                    continue
                
                file_info = {
                    'id': f"file_{self._calculate_hash(item)[:12]}",
                    'filename': item.name,
                    'relative_path': str(item.relative_to(self.base_path)),
                    'file_type': item.suffix.lower(),
                    'size': item.stat().st_size,
                    'content_hash': self._calculate_hash(item),
                    'created_at': datetime.fromtimestamp(item.stat().st_ctime).isoformat(),
                    'modified_at': datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                }
                
                # 提取内容预览
                content_preview = self._extract_content_preview(item)
                file_info['content_preview'] = content_preview[:500] + "..." if len(content_preview) > 500 else content_preview
                
                # 推荐标签
                file_info['recommended_tags'] = self._recommend_tags(item, content_preview)
                
                # 提取实体
                file_info['extracted_entities'] = self._extract_entities(content_preview)
                
                new_files.append(file_info)
        
        return new_files
    
    def generate_report(self, files: List[Dict]) -> str:
        """生成扫描报告"""
        report = []
        report.append("# 收件箱扫描报告\n")
        report.append(f"**扫描时间**: {datetime.now().isoformat()}\n")
        report.append(f"**发现文件**: {len(files)} 个\n")
        report.append("---\n\n")
        
        for i, file in enumerate(files, 1):
            report.append(f"## {i}. {file['filename']}\n")
            report.append(f"- **类型**: {file['file_type']}")
            report.append(f"- **大小**: {file['size'] / 1024:.1f} KB")
            report.append(f"- **ID**: `{file['id']}`")
            report.append("")
            
            # 推荐标签
            if file['recommended_tags']:
                report.append("**推荐标签**:")
                for tag in file['recommended_tags']:
                    report.append(f"- {tag['tag']} (置信度: {tag['confidence']:.0%})")
                report.append("")
            
            # 提取实体
            if file['extracted_entities']:
                report.append("**提取实体**:")
                for entity in file['extracted_entities'][:5]:  # 最多显示5个
                    report.append(f"- {entity['name']} ({entity['type']})")
                report.append("")
            
            # 内容预览
            report.append("**内容预览**:")
            report.append(f"```\n{file['content_preview'][:300]}...\n```")
            report.append("\n---\n")
        
        return "\n".join(report)


def main():
    """主函数"""
    # 配置路径
    base_path = str(Path(__file__).resolve().parent.parent.parent.parent)
    ontology_path = os.path.join(base_path, ".workbuddy", "scripts", "knowledge_db", "tag_ontology.json")
    
    # 创建扫描器
    scanner = FileScanner(base_path, ontology_path)
    
    # 执行扫描
    print("正在扫描收件箱...")
    new_files = scanner.scan_inbox()
    
    if not new_files:
        print("收件箱为空，没有发现新文件。")
        return
    
    print(f"发现 {len(new_files)} 个新文件")
    
    # 生成报告
    report = scanner.generate_report(new_files)
    
    # 保存报告
    report_path = os.path.join(base_path, ".workbuddy", "reports", f"scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"报告已保存: {report_path}")
    
    # 同时保存JSON格式的元数据
    metadata_path = os.path.join(base_path, ".workbuddy", "metadata", f"inbox_metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
    
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(new_files, f, ensure_ascii=False, indent=2)
    
    print(f"元数据已保存: {metadata_path}")


if __name__ == "__main__":
    main()
