#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能路由引擎 - 自动判断内容应该存放在哪个知识层级
"""

import re
from pathlib import Path
from datetime import datetime
from typing import Dict
from enum import Enum

class KnowledgeLayer(Enum):
    """知识分层枚举"""
    RAW_FILES = 1      # 原始文件
    FILE_INDEX = 2     # 文件搜索索引
    WORK_LOGS = 3      # 工作记录
    LONG_TERM_MEMORY = 4  # 长期记忆
    KNOWLEDGE_GRAPH = 5   # 知识图谱
    KNOWLEDGE_CRYSTALS = 6  # 知识结晶

class SmartRouter:
    """智能路由引擎"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.workbuddy_path = self.base_path / ".workbuddy"

    def analyze_content(self, content: str, context: Dict = None) -> Dict:
        """
        分析内容特征，判断应该路由到哪个层级

        Returns:
            {
                'primary_layer': KnowledgeLayer,
                'secondary_layers': List[KnowledgeLayer],
                'confidence': float,
                'reasoning': str,
                'suggested_path': str,
                'metadata': Dict
            }
        """
        context = context or {}

        # 特征提取
        features = self._extract_features(content, context)

        # 分层判断
        layer_scores = self._score_layers(features)

        # 选择主要层级
        primary_layer = max(layer_scores, key=layer_scores.get)

        # 选择次要层级（分数>0.5的）
        secondary_layers = [
            layer for layer, score in layer_scores.items()
            if layer != primary_layer and score > 0.5
        ]

        # 生成建议路径
        suggested_path = self._generate_path(primary_layer, features, context)

        return {
            'primary_layer': primary_layer,
            'secondary_layers': secondary_layers,
            'confidence': layer_scores[primary_layer],
            'reasoning': self._generate_reasoning(primary_layer, features),
            'suggested_path': suggested_path,
            'metadata': features,
            'all_scores': layer_scores
        }

    def _extract_features(self, content: str, context: Dict) -> Dict:
        """提取内容特征"""
        features = {
            'content_type': None,
            'has_explicit_preference': False,
            'has_abstraction_keywords': False,
            'has_entity_mentions': False,
            'has_temporal_markers': False,
            'is_file_reference': False,
            'is_session_log': False,
            'is_methodology': False,
            'entities': [],
            'keywords': [],
            'file_extensions': [],
        }

        content_lower = content.lower()

        # 判断内容类型
        if context.get('is_file'):
            features['content_type'] = 'file'
            features['is_file_reference'] = True
            features['file_extensions'] = [context.get('extension', '')]
        elif '会话' in content or 'session' in content_lower:
            features['content_type'] = 'session_log'
            features['is_session_log'] = True
        elif '模式' in content or '方法论' in content or '原则' in content:
            features['content_type'] = 'methodology'
            features['is_methodology'] = True

        # 检测明确偏好
        preference_patterns = [
            r'我喜欢', r'我偏好', r'我认为', r'我要', r'我希望',
            r'I prefer', r'I like', r'I want'
        ]
        for pattern in preference_patterns:
            if re.search(pattern, content):
                features['has_explicit_preference'] = True
                break

        # 检测抽象关键词
        abstraction_keywords = ['模式', '方法论', '原则', '框架', '模型', '理论',
                               'pattern', 'methodology', 'principle', 'framework']
        for keyword in abstraction_keywords:
            if keyword in content_lower:
                features['has_abstraction_keywords'] = True
                features['keywords'].append(keyword)

        # 提取实体（简化版）
        entity_patterns = [
            (r'主播\s*([A-Za-z\u4e00-\u9fa5]+)', 'PERSON'),
            (r'([A-Za-z]+)\s*系统', 'SYSTEM'),
            (r'#([\w\u4e00-\u9fa5]+)', 'TAG'),
        ]
        for pattern, entity_type in entity_patterns:
            for match in re.finditer(pattern, content):
                features['entities'].append({
                    'name': match.group(1),
                    'type': entity_type
                })

        if features['entities']:
            features['has_entity_mentions'] = True

        # 检测时间标记
        temporal_patterns = [r'\d{4}-\d{2}-\d{2}', r'\d{4}年', r'今天', r'昨天']
        for pattern in temporal_patterns:
            if re.search(pattern, content):
                features['has_temporal_markers'] = True
                break

        return features

    def _score_layers(self, features: Dict) -> Dict[KnowledgeLayer, float]:
        """为每个层级打分"""
        scores = {layer: 0.0 for layer in KnowledgeLayer}

        # Layer 1: 原始文件
        if features['is_file_reference']:
            scores[KnowledgeLayer.RAW_FILES] = 0.9

        # Layer 2: 文件搜索索引
        if features['is_file_reference'] or features['has_entity_mentions']:
            scores[KnowledgeLayer.FILE_INDEX] = 0.7

        # Layer 3: 工作记录
        if features['is_session_log'] or features['has_temporal_markers']:
            scores[KnowledgeLayer.WORK_LOGS] = 0.8

        # Layer 4: 长期记忆
        if features['has_explicit_preference']:
            scores[KnowledgeLayer.LONG_TERM_MEMORY] = 0.9

        # Layer 5: 知识图谱
        if features['has_entity_mentions'] and len(features['entities']) >= 2:
            scores[KnowledgeLayer.KNOWLEDGE_GRAPH] = 0.75

        # Layer 6: 知识结晶
        if features['is_methodology'] or features['has_abstraction_keywords']:
            scores[KnowledgeLayer.KNOWLEDGE_CRYSTALS] = 0.85

        return scores

    def _generate_path(self, layer: KnowledgeLayer, features: Dict, context: Dict) -> str:
        """生成建议存储路径"""
        if layer == KnowledgeLayer.RAW_FILES:
            if 'prompt' in str(features.get('keywords', [])).lower() or 'ai技能' in str(features.get('keywords', [])).lower():
                return "03-资产库/"
            elif any(k in str(features.get('keywords', [])) for k in ['知识', '概念', '规则']):
                return "05-知识沉淀/wiki/concepts/"
            else:
                return "01-收件箱/"

        elif layer == KnowledgeLayer.FILE_INDEX:
            return "05-知识沉淀/wiki/"

        elif layer == KnowledgeLayer.WORK_LOGS:
            today = datetime.now().strftime("%Y-%m-%d")
            return f"02-对话记录/{today}.md"

        elif layer == KnowledgeLayer.LONG_TERM_MEMORY:
            return ".workbuddy/记忆层/MEMORY.md"

        elif layer == KnowledgeLayer.KNOWLEDGE_GRAPH:
            return "05-知识沉淀/wiki/index.md"

        elif layer == KnowledgeLayer.KNOWLEDGE_CRYSTALS:
            crystal_name = self._extract_crystal_name(features, context)
            return f"05-知识沉淀/wiki/concepts/{crystal_name}.md"

        return "01-收件箱/"

    def _extract_crystal_name(self, features: Dict, context: Dict) -> str:
        """提取知识结晶名称"""
        # 从内容中提取方法论名称
        content = context.get('content', '')

        # 寻找"XX方法论"、"XX原则"等模式
        patterns = [
            r'([\w\u4e00-\u9fa5]+)方法论',
            r'([\w\u4e00-\u9fa5]+)原则',
            r'([\w\u4e00-\u9fa5]+)模式',
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1)

        return "未命名结晶"

    def _generate_reasoning(self, layer: KnowledgeLayer, features: Dict) -> str:
        """生成路由决策理由"""

        reasons = {
            KnowledgeLayer.RAW_FILES: "检测到文件引用，应存储为原始文件",
            KnowledgeLayer.FILE_INDEX: "需要建立索引以支持快速检索",
            KnowledgeLayer.WORK_LOGS: "包含时间标记或会话记录，应记录工作轨迹",
            KnowledgeLayer.LONG_TERM_MEMORY: "检测到明确偏好表达，应凝练为长期记忆",
            KnowledgeLayer.KNOWLEDGE_GRAPH: "包含多个实体提及，应构建知识图谱",
            KnowledgeLayer.KNOWLEDGE_CRYSTALS: "包含方法论或抽象概念，应形成知识结晶",
        }

        return reasons.get(layer, "基于内容特征自动判断")

    def route(self, content: str, context: Dict = None) -> Dict:
        """
        主路由函数 - 分析内容并返回路由建议

        示例:
            router = SmartRouter("C:/.../AI-聊天工作专项整理")
            result = router.route("我喜欢用Markdown存储文件")
            # result['primary_layer'] = KnowledgeLayer.LONG_TERM_MEMORY
        """
        analysis = self.analyze_content(content, context)

        # 自动创建父目录
        full_path = self.base_path / analysis['suggested_path']
        if not analysis['suggested_path'].endswith('/'):
            full_path.parent.mkdir(parents=True, exist_ok=True)

        # 打印路由决策
        print("[路由决策]")
        print(f"   主要层级: {analysis['primary_layer'].name}")
        print(f"   置信度: {analysis['confidence']:.0%}")
        print(f"   理由: {analysis['reasoning']}")
        print(f"   建议路径: {analysis['suggested_path']}")

        if analysis['secondary_layers']:
            layers_str = ', '.join([ly.name for ly in analysis['secondary_layers']])
            print(f"   次要层级: {layers_str}")

        return analysis


def demo():
    """演示路由功能"""
    base_path = str(Path(__file__).resolve().parent.parent.parent)
    router = SmartRouter(base_path)

    test_cases = [
        {
            'name': '文件引用',
            'content': '处理文件: 风控审核-标准版.md',
            'context': {'is_file': True, 'extension': '.md'}
        },
        {
            'name': '会话记录',
            'content': '2026-04-10 会话记录: 处理22MB大文件...',
            'context': {'is_session': True}
        },
        {
            'name': '用户偏好',
            'content': '我喜欢用Markdown格式存储知识，不喜欢SQLite',
            'context': {}
        },
        {
            'name': '方法论',
            'content': '渐进式整理方法论: 先丢后理，深度分析...',
            'context': {}
        },
        {
            'name': '实体提及',
            'content': '主播Sasa在会议中被提及，她的诊断报告显示...',
            'context': {}
        },
    ]

    for case in test_cases:
        print(f"\n{'='*60}")
        print(f"测试: {case['name']}")
        print(f"内容: {case['content'][:50]}...")
        print('-'*60)
        router.route(case['content'], case['context'])


if __name__ == "__main__":
    demo()
