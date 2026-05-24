#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识数据库 - 关联发现引擎
发现文件间的隐性关联，构建知识图谱
"""

import os
import json
import re
import logging
from pathlib import Path
from typing import List, Dict
from collections import defaultdict
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class RelationDiscovery:
    """关联发现引擎"""
    
    def __init__(self, base_path: str, ontology_path: str):
        self.base_path = Path(base_path)
        self.ontology = self._load_ontology(ontology_path)
        self.metadata_cache = {}
        
    def _load_ontology(self, path: str) -> Dict:
        """加载本体库"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"加载本体库失败: {e}")
            return {}
    
    def _load_file_metadata(self, file_path: Path) -> Dict:
        """加载文件元数据"""
        if file_path in self.metadata_cache:
            return self.metadata_cache[file_path]
        
        # 尝试加载对应的元数据文件
        meta_path = file_path.with_suffix(file_path.suffix + '.meta.json')
        if meta_path.exists():
            with open(meta_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                self.metadata_cache[file_path] = metadata
                return metadata
        
        # 如果没有元数据文件，返回基础信息
        return {
            'path': str(file_path),
            'filename': file_path.name,
            'entities': [],
            'tags': []
        }
    
    def _extract_entities_from_content(self, content: str) -> List[Dict]:
        """从内容中提取实体"""
        entities = []
        
        # 主播名
        anchor_pattern = r'主播\s*([A-Za-z\u4e00-\u9fa5]+)'
        for match in re.finditer(anchor_pattern, content):
            entities.append({
                'name': match.group(1),
                'type': 'PERSON',
                'context': match.group(0)
            })
        
        # 指标
        metric_patterns = [
            (r'(\d{3,})\s*钻石', '钻石'),
            (r'(\d+)\s*W', '万钻'),
            (r'R5\+?\s*收入?', 'R5收入'),
            (r'14W\s*线?', '14W线'),
        ]
        for pattern, name in metric_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                entities.append({
                    'name': name,
                    'type': 'METRIC',
                    'value': match.group(1) if match.groups() else None
                })
        
        return entities
    
    def _calculate_entity_overlap(self, entities_a: List[Dict], entities_b: List[Dict]) -> float:
        """计算实体重叠度"""
        names_a = {e['name'].lower() for e in entities_a}
        names_b = {e['name'].lower() for e in entities_b}
        
        if not names_a or not names_b:
            return 0.0
        
        intersection = names_a & names_b
        union = names_a | names_b
        
        return len(intersection) / len(union)
    
    def _calculate_tag_overlap(self, tags_a: List[str], tags_b: List[str]) -> float:
        """计算标签重叠度"""
        set_a = set(tags_a)
        set_b = set(tags_b)
        
        if not set_a or not set_b:
            return 0.0
        
        intersection = set_a & set_b
        union = set_a | set_b
        
        return len(intersection) / len(union)
    
    def _calculate_content_similarity(self, content_a: str, content_b: str) -> float:
        """计算内容相似度（简化版）"""
        # 使用SequenceMatcher计算相似度
        return SequenceMatcher(None, content_a[:1000], content_b[:1000]).ratio()
    
    def discover_relations(self, target_file: Path, candidate_files: List[Path]) -> List[Dict]:
        """
        为目标文件发现关联
        
        Args:
            target_file: 目标文件
            candidate_files: 候选文件列表
            
        Returns:
            关联列表，按权重排序
        """
        relations = []
        
        # 加载目标文件元数据
        target_meta = self._load_file_metadata(target_file)
        target_entities = target_meta.get('entities', [])
        target_tags = target_meta.get('tags', [])
        
        # 尝试读取目标文件内容
        target_content = ""
        try:
            if target_file.suffix in ['.txt', '.md']:
                with open(target_file, 'r', encoding='utf-8', errors='ignore') as f:
                    target_content = f.read(2000)
        except Exception as e:
            logger.warning(f"读取目标文件失败: {e}")
        
        for candidate in candidate_files:
            if candidate == target_file:
                continue
            
            # 加载候选文件元数据
            candidate_meta = self._load_file_metadata(candidate)
            candidate_entities = candidate_meta.get('entities', [])
            candidate_tags = candidate_meta.get('tags', [])
            
            # 计算各项相似度
            entity_score = self._calculate_entity_overlap(target_entities, candidate_entities)
            tag_score = self._calculate_tag_overlap(target_tags, candidate_tags)
            
            # 内容相似度
            content_score = 0.0
            try:
                if candidate.suffix in ['.txt', '.md']:
                    with open(candidate, 'r', encoding='utf-8', errors='ignore') as f:
                        candidate_content = f.read(2000)
                    content_score = self._calculate_content_similarity(target_content, candidate_content)
            except Exception as e:
                logger.warning(f"读取候选文件失败: {e}")
            
            # 综合关联度
            relation_score = entity_score * 0.4 + tag_score * 0.3 + content_score * 0.3
            
            if relation_score > 0.3:  # 阈值
                # 确定关联类型
                relation_type = self._determine_relation_type(
                    target_file, candidate, 
                    entity_score, tag_score, content_score
                )
                
                relations.append({
                    'source': str(target_file),
                    'target': str(candidate),
                    'relation_type': relation_type,
                    'weight': round(relation_score, 3),
                    'details': {
                        'entity_overlap': round(entity_score, 3),
                        'tag_overlap': round(tag_score, 3),
                        'content_similarity': round(content_score, 3)
                    },
                    'common_entities': list(
                        {e['name'] for e in target_entities} & 
                        {e['name'] for e in candidate_entities}
                    )
                })
        
        # 按权重排序
        relations.sort(key=lambda x: x['weight'], reverse=True)
        return relations
    
    def _determine_relation_type(self, file_a: Path, file_b: Path, 
                                  entity_score: float, tag_score: float, 
                                  content_score: float) -> str:
        """确定关联类型"""
        # 版本关系
        name_a = file_a.stem.lower()
        name_b = file_b.stem.lower()
        
        if self._is_version_relation(name_a, name_b):
            return "VERSION_OF"
        
        # 依赖关系（文件名包含关系）
        if file_a.name in name_b or file_b.name in name_a:
            return "DEPENDS_ON"
        
        # 包含关系（目录关系）
        if file_a.parent == file_b.parent:
            return "PART_OF_GROUP"
        
        # 实体强关联
        if entity_score > 0.5:
            return "SHARES_ENTITIES"
        
        # 标签强关联
        if tag_score > 0.5:
            return "SHARES_CONTEXT"
        
        # 默认语义关联
        return "SEMANTIC_SIMILAR"
    
    def _is_version_relation(self, name_a: str, name_b: str) -> bool:
        """判断是否为版本关系"""
        # 简单的版本号检测（通过正则直接匹配，不需要预编译patterns列表）
        base_a = re.sub(r'v?\d+\.?\d*', '', name_a).strip('_- ')
        base_b = re.sub(r'v?\d+\.?\d*', '', name_b).strip('_- ')
        
        return base_a == base_b and base_a != ""
    
    def build_knowledge_graph(self, files: List[Path]) -> Dict:
        """构建知识图谱"""
        graph = {
            'nodes': [],
            'edges': [],
            'stats': {
                'total_files': len(files),
                'total_relations': 0,
                'relation_types': defaultdict(int)
            }
        }
        
        # 添加节点
        for file in files:
            meta = self._load_file_metadata(file)
            graph['nodes'].append({
                'id': str(file),
                'name': file.name,
                'type': file.suffix,
                'entities': [e['name'] for e in meta.get('entities', [])],
                'tags': meta.get('tags', [])
            })
        
        # 发现所有关联
        for i, file in enumerate(files):
            logger.info(f"处理文件 {i+1}/{len(files)}: {file.name}")
            relations = self.discover_relations(file, files)
            
            for rel in relations:
                graph['edges'].append(rel)
                graph['stats']['relation_types'][rel['relation_type']] += 1
            
            graph['stats']['total_relations'] += len(relations)
        
        return graph
    
    def find_related_files(self, query_file: Path, top_k: int = 5) -> List[Dict]:
        """查找与查询文件最相关的文件"""
        # 获取所有候选文件
        all_files = []
        for ext in ['.txt', '.md', '.docx', '.json']:
            all_files.extend(self.base_path.rglob(f'*{ext}'))
        
        # 过滤掉在收件箱的文件
        all_files = [f for f in all_files if '01-收件箱' not in str(f)]
        
        # 发现关联
        relations = self.discover_relations(query_file, all_files)
        
        return relations[:top_k]


def main():
    """主函数"""
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # 脚本在 knowledge_db/，向上四级到根目录
    ontology_path = os.path.join(base_path, ".workbuddy", "scripts", "knowledge_db", "tag_ontology.json")
    
    discovery = RelationDiscovery(base_path, ontology_path)
    
    # 示例：查找相关文件
    example_file = Path(base_path) / "05-知识沉淀" / "wiki" / "sources" / "示例知识来源.md"
    
    if example_file.exists():
        logger.info(f"查找与 '{example_file.name}' 相关的文件...")
        related = discovery.find_related_files(example_file, top_k=10)
        
        logger.info("相关文件:")
        for i, rel in enumerate(related, 1):
            target_name = Path(rel['target']).name
            logger.info(f"{i}. {target_name}")
            logger.info(f"   关联类型: {rel['relation_type']}")
            logger.info(f"   关联度: {rel['weight']:.2f}")
            if rel['common_entities']:
                logger.info(f"   共同实体: {', '.join(rel['common_entities'])}")
    else:
        logger.warning(f"示例文件不存在: {example_file}")


if __name__ == "__main__":
    main()
