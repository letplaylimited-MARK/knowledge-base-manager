#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容深度分析器 - 理解实质内容，智能优化命名
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ContentInsight:
    """内容洞察"""
    core_topic: str           # 核心主题
    key_entities: List[Dict]  # 关键实体
    concepts: List[str]       # 核心概念
    content_type: str         # 内容类型
    quality_level: str        # 质量等级
    suggested_name: str       # 建议命名
    rename_reason: str        # 重命名理由
    confidence: float         # 置信度

CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / ".workbuddy" / "config" / "domain_keywords.json"

def _load_domain_config():
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"entity_patterns": [], "concept_keywords": [], "topic_indicators": {}, "metric_patterns": []}

class ContentAnalyzer:
    """内容深度分析器"""

    def __init__(self, ontology_path: str = None):
        self.ontology = self._load_ontology(ontology_path) if ontology_path else {}
        self.domain_config = _load_domain_config()

    def _load_ontology(self, path: str) -> Dict:
        """加载本体库"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def analyze_file(self, file_path: Path, content: str = None) -> ContentInsight:
        """
        深度分析文件内容

        Args:
            file_path: 文件路径
            content: 文件内容（如已读取）

        Returns:
            ContentInsight: 内容洞察
        """
        # 如未提供内容，尝试读取
        if content is None:
            content = self._read_file(file_path)

        # 多维度分析
        entities = self._extract_entities(content)
        concepts = self._extract_concepts(content)
        content_type = self._determine_content_type(content, file_path)
        quality_level = self._assess_quality(content, file_path)
        core_topic = self._identify_core_topic(content, entities, concepts)

        # 生成建议命名
        suggested_name, rename_reason = self._generate_name(
            file_path, core_topic, content_type, quality_level, entities, concepts
        )

        # 计算置信度
        confidence = self._calculate_confidence(content, entities, concepts)

        return ContentInsight(
            core_topic=core_topic,
            key_entities=entities,
            concepts=concepts,
            content_type=content_type,
            quality_level=quality_level,
            suggested_name=suggested_name,
            rename_reason=rename_reason,
            confidence=confidence
        )

    def _read_file(self, file_path: Path) -> str:
        """读取文件内容"""
        try:
            if file_path.suffix in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
            elif file_path.suffix == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.dumps(json.load(f), ensure_ascii=False)
            else:
                return f"[{file_path.suffix} file]"
        except Exception as e:
            return f"[Error reading file: {e}]"

    def _extract_entities(self, content: str) -> List[Dict]:
        """提取关键实体"""
        entities = []
        for pattern in self.domain_config.get("entity_patterns", []):
            regex = pattern.get("regex", "")
            if not regex:
                continue
            for match in re.finditer(regex, content):
                entities.append({
                    "name": match.group(1) if match.groups() else match.group(0),
                    "type": pattern.get("type", "ENTITY"),
                    "confidence": pattern.get("confidence", 0.7)
                })
        seen = set()
        unique = []
        for e in entities:
            key = (e['name'], e['type'])
            if key not in seen:
                seen.add(key)
                unique.append(e)
        return unique[:10]

    def _extract_concepts(self, content: str) -> List[str]:
        """提取核心概念"""
        keywords = self.domain_config.get("concept_keywords", [])
        matched = []
        for kw in keywords:
            if kw in content:
                matched.append(kw)
        return matched[:10]

    def _determine_content_type(self, content: str, file_path: Path) -> str:
        """确定内容类型"""
        content_lower = content.lower()
        indicators = self.domain_config.get("topic_indicators", {})
        for ctype, keywords in indicators.items():
            for kw in keywords:
                if kw in content_lower:
                    return ctype
        if '方法论' in content_lower or '方法' in content_lower:
            return '方法论'
        if 'sop' in file_path.name.lower():
            return 'SOP文档'
        return '通用文档'

    def _assess_quality(self, content: str, file_path: Path) -> str:
        """评估质量等级"""
        filename = file_path.name

        # 高质量标记
        high_quality_markers = ['终极版', '已验证', 'V2.0', 'V3.0', 'final', 'verified']
        for marker in high_quality_markers:
            if marker in filename:
                return '已验证精品'

        # 草稿标记
        draft_markers = ['草稿', 'draft', '测试', 'test', '临时', 'temp']
        for marker in draft_markers:
            if marker in filename:
                return '草稿测试'

        # 内容质量判断
        if len(content) > 5000 and '示例' in content and '说明' in content:
            return '内容完整'

        return '标准'

    def _identify_core_topic(self, content: str, entities: List[Dict], concepts: List[str]) -> str:
        """识别核心主题"""
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip()[:50]
        if concepts:
            return concepts[0]
        if entities:
            return entities[0]["name"]
        return '综合内容'

    def _generate_name(self, file_path: Path, core_topic: str, content_type: str,
                       quality_level: str, entities: List[Dict], concepts: List[str]) -> Tuple[str, str]:
        """生成建议命名"""

        original_name = file_path.stem
        extension = file_path.suffix

        # 分析原命名
        rename_reason = ""
        suggested_name = original_name

        # 情况1: 原命名过于简单
        if len(original_name) < 10 or original_name in ['新建文本文档', '文档', 'file']:
            rename_reason = "原命名过于简单，无法体现内容"
            suggested_name = self._build_descriptive_name(
                core_topic, content_type, quality_level, entities, concepts
            )

        # 情况2: 原命名缺少关键信息
        elif not any(keyword in original_name for keyword in [core_topic, content_type]):
            rename_reason = "原命名缺少核心主题或内容类型标识"
            suggested_name = self._build_descriptive_name(
                core_topic, content_type, quality_level, entities, concepts
            )

        # 情况3: 命名格式不统一
        elif '·' in original_name and ' ' in original_name:
            rename_reason = "命名格式不统一，建议标准化"
            suggested_name = self._standardize_name(original_name)

        # 情况4: 命名已很好
        else:
            rename_reason = "命名已较好，建议保持"
            suggested_name = original_name

        return suggested_name + extension, rename_reason

    def _build_descriptive_name(self, core_topic: str, content_type: str,
                                quality_level: str, entities: List[Dict],
                                concepts: List[str]) -> str:
        """构建描述性命名"""
        parts = []

        # 1. 质量/状态标记
        if quality_level == '已验证精品':
            parts.append('终极版')
        elif quality_level == '草稿测试':
            parts.append('测试版')

        # 2. 核心主题
        if core_topic:
            parts.append(core_topic)

        # 3. 内容类型
        if content_type:
            parts.append(content_type)

        # 4. 关键实体（如果空间允许）
        anchor = [e for e in entities if e['type'] == 'ANCHOR']
        if anchor and len(parts) < 3:
            parts.append(f"{anchor[0]['name']}案例")

        # 组合命名
        if len(parts) >= 2:
            return '·'.join(parts[:3])  # 最多3部分
        else:
            return parts[0] if parts else '未命名文档'

    def _standardize_name(self, name: str) -> str:
        """标准化命名"""
        # 统一分隔符
        name = name.replace(' ', '·').replace('-', '·').replace('_', '·')
        # 去除多余分隔符
        while '··' in name:
            name = name.replace('··', '·')
        return name.strip('·')

    def _calculate_confidence(self, content: str, entities: List[Dict], concepts: List[str]) -> float:
        """计算分析置信度"""
        score = 0.5  # 基础分

        # 内容长度
        if len(content) > 1000:
            score += 0.1
        if len(content) > 5000:
            score += 0.1

        # 实体数量
        if len(entities) >= 3:
            score += 0.1
        if len(entities) >= 5:
            score += 0.1

        # 概念数量
        if len(concepts) >= 2:
            score += 0.05
        if len(concepts) >= 4:
            score += 0.05

        return min(score, 1.0)

    def generate_report(self, file_path: Path, insight: ContentInsight) -> str:
        """生成分析报告"""
        report = []
        report.append("# 内容深度分析报告")
        report.append(f"**文件**: {file_path.name}")
        report.append(f"**分析时间**: {datetime.now().isoformat()}")
        report.append("")

        report.append("## 内容洞察")
        report.append(f"- **核心主题**: {insight.core_topic}")
        report.append(f"- **内容类型**: {insight.content_type}")
        report.append(f"- **质量等级**: {insight.quality_level}")
        report.append(f"- **分析置信度**: {insight.confidence:.0%}")
        report.append("")

        if insight.key_entities:
            report.append("## 关键实体")
            for entity in insight.key_entities[:5]:
                report.append(f"- {entity['name']} ({entity['type']})")
            report.append("")

        if insight.concepts:
            report.append("## 核心概念")
            report.append(f"{', '.join(insight.concepts)}")
            report.append("")

        report.append("## 命名建议")
        report.append(f"- **建议命名**: `{insight.suggested_name}`")
        report.append(f"- **理由**: {insight.rename_reason}")
        report.append("")

        if insight.confidence < 0.7:
            report.append("[注意] **注意**: 分析置信度较低，建议人工确认")

        return '\n'.join(report)


def demo():
    """演示内容分析"""
    analyzer = ContentAnalyzer()

    # 测试内容
    test_contents = [
        {
            'name': '新建文本文档.txt',
            'content': '''
主播： Sasa
ID： 420202227771
钻石收入总累计：288542
视频分钟钻石效率：2.46
主播聊天存在的问题：
- 过快且过于频繁地使用"hi"
- 新主播马来语不够熟练
- 主播回复用户消息过慢
- 日常闲聊过多，缺乏往暧昧/恋爱方向的推进
'''
        },
        {
            'name': '文档.md',
            'content': '''
# 终极版·男用户-女主播聊天风控审核系统提示词

## 核心能力
批量Excel文件全量读取，6类风险判定：
1. 身份伪装 - gen、agen、代理、中介
2. 分步诱导 - 索要ID、资料、截图
3. 利益交换 - 付费换取联系方式
4. 站外引流 - 微信、WhatsApp、LINE
5. 线下邀约 - 见面、约会
6. 欺骗行为 - 虚假承诺

## 技术特性
- 零幻觉、零脑补、零伪造
- 温度=0，100%照搬原文
- 支持中文、英文、马来语
'''
        }
    ]

    for test in test_contents:
        print(f"\n{'='*60}")
        print(f"分析文件: {test['name']}")
        print('='*60)

        temp_path = Path(test['name'])

        insight = analyzer.analyze_file(temp_path, test['content'])
        report = analyzer.generate_report(temp_path, insight)
        print(report)


if __name__ == "__main__":
    demo()
