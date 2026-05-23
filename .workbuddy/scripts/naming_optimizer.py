#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命名优化器 - 基于内容实质智能推荐新名称
"""

from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class NamingSuggestion:
    """命名建议"""
    original_name: str
    suggested_name: str
    reason: str
    confidence: float
    alternatives: List[str]

class NamingOptimizer:
    """智能命名优化器"""

    def __init__(self):
        self.naming_patterns = self._load_patterns()

    def _load_patterns(self) -> Dict:
        """加载命名模式库"""
        return {
            'quality_markers': {
                '终极版': 5, '已验证': 5, 'V2.0': 4, 'V3.0': 4,
                'final': 5, 'verified': 5, 'stable': 4,
                '草稿': 1, 'draft': 1, '测试': 2, 'test': 2,
                '临时': 1, 'temp': 1, 'backup': 1
            },
            'content_types': {
                '系统提示词': 5, 'Prompt': 5, '提示词': 5,
                '会议纪要': 5, '会议记录': 5,
                '诊断报告': 5, '分析报告': 4,
                '制度文档': 5, '规则': 4,
                '方法论': 5, 'SOP': 5,
                '数据': 3, '报告': 3, '文档': 2
            },
            'separators': ['·', '-', '_', ' ', '—'],
            'max_length': 80,
            'optimal_parts': 3
        }

    def analyze_and_suggest(self, file_path: Path, content_analysis: Dict) -> NamingSuggestion:
        """
        分析并建议新命名

        Args:
            file_path: 原文件路径
            content_analysis: 内容分析结果

        Returns:
            NamingSuggestion: 命名建议
        """
        original_name = file_path.stem
        extension = file_path.suffix

        # 分析原命名问题
        issues = self._analyze_naming_issues(original_name, content_analysis)

        # 生成建议命名
        suggested_name = self._generate_optimal_name(
            original_name, content_analysis, issues
        )

        # 生成备选命名
        alternatives = self._generate_alternatives(
            original_name, content_analysis, suggested_name
        )

        # 计算置信度
        confidence = self._calculate_confidence(
            original_name, suggested_name, content_analysis, issues
        )

        # 生成理由
        reason = self._generate_reason(issues, suggested_name)

        return NamingSuggestion(
            original_name=original_name + extension,
            suggested_name=suggested_name + extension,
            reason=reason,
            confidence=confidence,
            alternatives=[a + extension for a in alternatives]
        )

    def _analyze_naming_issues(self, name: str, analysis: Dict) -> List[Dict]:
        """分析命名存在的问题"""
        issues = []

        # 问题1: 过于简单
        if len(name) < 10:
            issues.append({
                'type': 'too_simple',
                'severity': 'high',
                'description': f'命名过于简单（{len(name)}字符），无法体现内容'
            })

        # 问题2: 通用命名
        generic_names = ['新建文本文档', '文档', 'file', 'document', 'temp', '临时']
        if any(generic in name for generic in generic_names):
            issues.append({
                'type': 'generic',
                'severity': 'high',
                'description': '使用通用命名，建议改为描述性命名'
            })

        # 问题3: 缺少质量标记
        has_quality = any(marker in name for marker in self.naming_patterns['quality_markers'])
        if not has_quality and analysis.get('quality_level') == '已验证精品':
            issues.append({
                'type': 'missing_quality',
                'severity': 'medium',
                'description': '内容质量高但命名缺少质量标记（如"终极版"）'
            })

        # 问题4: 缺少内容类型
        has_type = any(t in name for t in self.naming_patterns['content_types'])
        if not has_type:
            issues.append({
                'type': 'missing_type',
                'severity': 'medium',
                'description': '命名缺少内容类型标识'
            })

        # 问题5: 格式混乱
        separators_count = sum(1 for sep in self.naming_patterns['separators'] if sep in name)
        if separators_count > 2:
            issues.append({
                'type': 'format_chaos',
                'severity': 'low',
                'description': '命名格式混乱，分隔符过多'
            })

        # 问题6: 过长
        if len(name) > self.naming_patterns['max_length']:
            issues.append({
                'type': 'too_long',
                'severity': 'medium',
                'description': f'命名过长（{len(name)}字符），建议精简'
            })

        return issues

    def _generate_optimal_name(self, original: str, analysis: Dict, issues: List[Dict]) -> str:
        """生成最优命名"""
        parts = []

        # 1. 质量/状态（如果有）
        quality = analysis.get('quality_level', '')
        if quality == '已验证精品':
            parts.append('终极版')
        elif quality == '草稿测试':
            parts.append('测试版')
        elif any(i['type'] == 'missing_quality' for i in issues):
            # 内容好但命名没体现
            parts.append('已验证')

        # 2. 核心主题
        core_topic = analysis.get('core_topic', '')
        if core_topic and core_topic != '综合内容':
            parts.append(core_topic)

        # 3. 内容类型
        content_type = analysis.get('content_type', '')
        if content_type and content_type != '通用文档':
            parts.append(content_type)

        # 4. 关键实体（如果空间允许）
        entities = analysis.get('key_entities', [])
        anchors = [e for e in entities if e['type'] == 'ANCHOR']
        if anchors and len(parts) < self.naming_patterns['optimal_parts']:
            parts.append(f"{anchors[0]['name']}案例")

        # 组合
        if not parts:
            return original

        # 使用统一分隔符
        name = '·'.join(parts[:3])  # 最多3部分

        # 清理
        name = self._clean_name(name)

        return name

    def _generate_alternatives(self, original: str, analysis: Dict, primary: str) -> List[str]:
        """生成备选命名"""
        alternatives = []

        # 备选1: 简化版（去掉质量标记）
        parts = primary.split('·')
        if len(parts) > 1 and parts[0] in ['终极版', '已验证', '测试版']:
            simplified = '·'.join(parts[1:])
            if simplified != primary:
                alternatives.append(simplified)

        # 备选2: 加日期
        from datetime import datetime
        date_str = datetime.now().strftime("%Y%m%d")
        dated = f"{date_str}·{primary}"
        alternatives.append(dated)

        # 备选3: 英文版（如果原命名是中文）
        content_type = analysis.get('content_type', '')
        if 'Prompt' in content_type:
            topic = analysis.get('core_topic', '')
            if topic:
                english_name = self._translate_to_english(topic)
                if english_name:
                    alternatives.append(f"{english_name}-Prompt")

        return alternatives[:2]  # 最多2个备选

    def _clean_name(self, name: str) -> str:
        """清理命名"""
        # 统一分隔符
        for sep in ['-', '_', ' ', '—']:
            name = name.replace(sep, '·')

        # 去除重复分隔符
        while '··' in name:
            name = name.replace('··', '·')

        # 去除首尾分隔符
        name = name.strip('·')

        # 限制长度
        if len(name) > self.naming_patterns['max_length']:
            name = name[:self.naming_patterns['max_length']].rsplit('·', 1)[0]

        return name

    def _translate_to_english(self, chinese: str) -> str:
        """简单中译英（实际可用翻译API）"""
        translations = {
            '风控审核': 'RiskControl',
            '数据分析': 'DataAnalysis',
            '师傅运营': 'MentorOperation',
            '主播结算': 'AnchorSettlement',
        }
        return translations.get(chinese, '')

    def _calculate_confidence(self, original: str, suggested: str, analysis: Dict, issues: List[Dict]) -> float:
        """计算建议置信度"""
        score = 0.5

        # 原命名问题越多，改进信心越高
        high_severity = sum(1 for i in issues if i['severity'] == 'high')
        score += high_severity * 0.1

        # 内容分析质量
        if analysis.get('confidence', 0) > 0.7:
            score += 0.1

        # 建议命名包含更多信息
        if len(suggested) > len(original):
            score += 0.1

        # 建议命名包含关键元素
        if any(marker in suggested for marker in self.naming_patterns['quality_markers']):
            score += 0.1

        return min(score, 1.0)

    def _generate_reason(self, issues: List[Dict], suggested: str) -> str:
        """生成推荐理由"""
        if not issues:
            return "原命名已较好，建议保持"

        # 按严重程度排序
        issues.sort(key=lambda x: {'high': 0, 'medium': 1, 'low': 2}[x['severity']])

        main_issue = issues[0]

        reasons = {
            'too_simple': "原命名过于简单，建议改为描述性命名",
            'generic': "原命名过于通用，建议体现具体内容",
            'missing_quality': "内容质量高但命名未体现，建议添加质量标记",
            'missing_type': "命名缺少内容类型标识",
            'format_chaos': "命名格式不统一，建议标准化",
            'too_long': "原命名过长，建议精简",
        }

        return reasons.get(main_issue['type'], "建议优化命名以更准确反映内容")

    def should_rename(self, suggestion: NamingSuggestion, threshold: float = 0.7) -> bool:
        """判断是否建议重命名"""
        # 置信度足够高
        if suggestion.confidence < threshold:
            return False

        # 命名有实质性改进
        if suggestion.original_name == suggestion.suggested_name:
            return False

        # 改进幅度足够
        original_parts = suggestion.original_name.replace('.', '·').split('·')
        suggested_parts = suggestion.suggested_name.replace('.', '·').split('·')

        if len(suggested_parts) <= len(original_parts):
            return False

        return True

    def generate_rename_report(self, file_path: Path, suggestion: NamingSuggestion) -> str:
        """生成重命名报告"""
        report = []
        report.append("# 命名优化建议")
        report.append("")
        report.append(f"**原文件名**: `{suggestion.original_name}`")
        report.append(f"**建议命名**: `{suggestion.suggested_name}`")
        report.append(f"**置信度**: {suggestion.confidence:.0%}")
        report.append(f"**理由**: {suggestion.reason}")
        report.append("")

        if suggestion.alternatives:
            report.append("**备选命名**:")
            for i, alt in enumerate(suggestion.alternatives, 1):
                report.append(f"{i}. `{alt}`")
            report.append("")

        if self.should_rename(suggestion):
            report.append("✅ **建议执行重命名**")
        else:
            report.append("⚠️ **建议保持原命名**（改进不明显或置信度不足）")

        return '\n'.join(report)


def demo():
    """演示命名优化"""
    optimizer = NamingOptimizer()

    test_cases = [
        {
            'name': '新建文本文档.txt',
            'analysis': {
                'core_topic': '主播Sasa诊断',
                'content_type': '诊断报告',
                'quality_level': '标准',
                'key_entities': [{'name': 'Sasa', 'type': 'ANCHOR'}],
                'confidence': 0.85
            }
        },
        {
            'name': '文档.md',
            'analysis': {
                'core_topic': '风控审核',
                'content_type': '系统提示词',
                'quality_level': '已验证精品',
                'key_entities': [],
                'confidence': 0.9
            }
        },
        {
            'name': '终极版·风控审核.md',
            'analysis': {
                'core_topic': '风控审核',
                'content_type': '系统提示词',
                'quality_level': '已验证精品',
                'key_entities': [],
                'confidence': 0.9
            }
        }
    ]

    for test in test_cases:
        print(f"\n{'='*60}")
        print(f"分析: {test['name']}")
        print('='*60)

        from pathlib import Path
        temp_path = Path(test['name'])

        suggestion = optimizer.analyze_and_suggest(temp_path, test['analysis'])
        report = optimizer.generate_rename_report(temp_path, suggestion)
        print(report)


if __name__ == "__main__":
    demo()
