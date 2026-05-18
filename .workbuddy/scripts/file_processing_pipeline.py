#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件处理流水线 - 深度理解 → 智能归纳 → 版本管理 → 命名决策
"""

import os
import json
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from difflib import SequenceMatcher

@dataclass
class FileUnderstanding:
    """文件理解结果"""
    file_path: Path
    content_hash: str
    content_preview: str
    full_content: str
    core_topic: str
    content_type: str
    quality_level: str
    key_entities: List[Dict]
    core_concepts: List[str]
    technical_features: List[str]
    version_info: Dict
    is_duplicate: bool = False
    duplicate_of: Optional[Path] = None
    similar_files: List[Dict] = field(default_factory=list)

@dataclass
class CoexistenceDecision:
    """共存决策"""
    should_coexist: bool
    coexistence_type: str  # 'version', 'variant', 'duplicate', 'distinct'
    reason: str
    suggested_action: str
    related_files: List[Path]

@dataclass
class NamingDecision:
    """命名决策"""
    should_rename: bool
    original_name: str
    suggested_name: str
    alternatives: List[str]
    reason: str
    confidence: float

@dataclass
class ProcessingResult:
    """处理结果"""
    understanding: FileUnderstanding
    coexistence: CoexistenceDecision
    naming: NamingDecision
    final_recommendation: str
    action_plan: Dict


class ContentReader:
    """内容读取器 - 真正读取文件内容"""
    
    def read_file(self, file_path: Path) -> Tuple[str, str]:
        """
        深度读取文件内容
        
        Returns:
            (full_content, preview)
        """
        try:
            suffix = file_path.suffix.lower()
            
            if suffix in ['.txt', '.md', '.py', '.js', '.json']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    preview = content[:2000] + "..." if len(content) > 2000 else content
                    return content, preview
            
            elif suffix == '.docx':
                return self._read_docx(file_path)
            
            elif suffix == '.pdf':
                return self._read_pdf(file_path)
            
            elif suffix in ['.xlsx', '.xls', '.csv']:
                return self._read_spreadsheet(file_path)
            
            else:
                return f"[Binary file: {suffix}]", f"[Binary: {suffix}]"
                
        except Exception as e:
            return f"[Error: {e}]", f"[Error: {e}]"
    
    def _read_docx(self, file_path: Path) -> Tuple[str, str]:
        """读取docx内容"""
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            
            with zipfile.ZipFile(file_path, 'r') as z:
                xml_content = z.read('word/document.xml')
                tree = ET.fromstring(xml_content)
                
                # 提取文本
                texts = []
                for elem in tree.iter():
                    if elem.text:
                        texts.append(elem.text)
                
                content = '\n'.join(texts)
                preview = content[:2000] + "..." if len(content) > 2000 else content
                return content, preview
        except:
            return "[DOCX content extraction failed]", "[DOCX failed]"
    
    def _read_pdf(self, file_path: Path) -> Tuple[str, str]:
        """读取PDF内容"""
        # 简化处理，实际可用PyPDF2或pdfplumber
        return "[PDF content - extraction pending]", "[PDF pending]"
    
    def _read_spreadsheet(self, file_path: Path) -> Tuple[str, str]:
        """读取表格内容"""
        try:
            if file_path.suffix == '.csv':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    preview = content[:2000] + "..." if len(content) > 2000 else content
                    return content, preview
            else:
                return "[Excel content - extraction pending]", "[Excel pending]"
        except:
            return "[Spreadsheet read failed]", "[Spreadsheet failed]"


class ContentUnderstander:
    """内容理解器 - 深度理解文件实质"""
    
    def understand(self, file_path: Path, content: str, preview: str) -> FileUnderstanding:
        """深度理解文件内容"""
        
        # 计算内容哈希
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # 提取核心信息
        core_topic = self._extract_core_topic(content)
        content_type = self._determine_content_type(content, file_path)
        quality_level = self._assess_quality(content, file_path)
        entities = self._extract_entities(content)
        concepts = self._extract_concepts(content)
        tech_features = self._extract_technical_features(content)
        version_info = self._extract_version_info(content, file_path)
        
        return FileUnderstanding(
            file_path=file_path,
            content_hash=content_hash,
            content_preview=preview,
            full_content=content,
            core_topic=core_topic,
            content_type=content_type,
            quality_level=quality_level,
            key_entities=entities,
            core_concepts=concepts,
            technical_features=tech_features,
            version_info=version_info
        )
    
    def _extract_core_topic(self, content: str) -> str:
        """提取核心主题"""
        # 从标题提取
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip()[:50]
        
        # 从关键词推断
        if '风控' in content and '审核' in content:
            return '风控审核系统'
        elif '数据分析' in content:
            return '数据分析系统'
        elif '主播' in content and '诊断' in content:
            return '主播诊断分析'
        elif '师傅' in content and '运营' in content:
            return '师傅运营体系'
        
        return '综合内容'
    
    def _determine_content_type(self, content: str, file_path: Path) -> str:
        """确定内容类型"""
        filename = file_path.name.lower()
        content_lower = content.lower()
        
        # Prompt相关
        if 'prompt' in content_lower or '提示词' in content or 'system prompt' in content_lower:
            if '风控' in content:
                return '风控审核Prompt'
            elif '数据' in content:
                return '数据分析Prompt'
            else:
                return '系统提示词'
        
        # 会议记录
        if '会议' in filename or '纪要' in filename:
            return '会议纪要'
        
        # 诊断报告
        if '诊断' in filename or '分析' in filename:
            return '诊断报告'
        
        # 制度文档
        if '制度' in content or '规则' in content:
            return '制度文档'
        
        return '通用文档'
    
    def _assess_quality(self, content: str, file_path: Path) -> str:
        """评估质量等级"""
        filename = file_path.name
        
        # 高质量标记
        if any(m in filename for m in ['终极版', '已验证', 'V2', 'V3', 'final']):
            return '已验证精品'
        
        # 内容质量判断
        has_examples = '示例' in content or 'example' in content.lower()
        has_structure = content.count('#') >= 3
        has_detail = len(content) > 3000
        
        if has_examples and has_structure and has_detail:
            return '内容完整'
        
        return '标准'
    
    def _extract_entities(self, content: str) -> List[Dict]:
        """提取关键实体"""
        entities = []
        
        # 主播名
        for match in re.finditer(r'主播[：:]?\s*([A-Za-z\u4e00-\u9fa5]{2,20})', content):
            entities.append({'name': match.group(1), 'type': 'ANCHOR'})
        
        # 指标
        for match in re.finditer(r'(\d{3,})\s*钻石', content):
            entities.append({'name': '钻石收入', 'type': 'METRIC', 'value': match.group(1)})
        
        return entities[:5]
    
    def _extract_concepts(self, content: str) -> List[str]:
        """提取核心概念"""
        concepts = []
        content_lower = content.lower()
        
        concept_patterns = {
            'identity_confirmed': [r'identity[_\-]?confirmed', r'确认达标'],
            'agen_gen': [r'\bagen\b', r'\bgen\b'],
            '零幻觉': [r'零幻觉', r'无幻觉'],
            '跨AI兼容': [r'跨AI', r'兼容'],
        }
        
        for concept, patterns in concept_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    concepts.append(concept)
                    break
        
        return concepts
    
    def _extract_technical_features(self, content: str) -> List[str]:
        """提取技术特性"""
        features = []
        
        if '批量' in content and 'Excel' in content:
            features.append('批量Excel处理')
        if '零幻觉' in content:
            features.append('零幻觉输出')
        if '跨AI' in content:
            features.append('跨AI兼容')
        if 'HTML' in content:
            features.append('HTML可视化')
        
        return features
    
    def _extract_version_info(self, content: str, file_path: Path) -> Dict:
        """提取版本信息"""
        filename = file_path.name
        
        version_patterns = [
            r'V(\d+\.?\d*)',
            r'(\d+\.?\d*)版',
            r'version[_\-]?(\d+)',
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                return {
                    'version': match.group(1),
                    'is_versioned': True,
                    'base_name': re.sub(pattern, '', filename, flags=re.IGNORECASE).strip('._- ')
                }
        
        return {'version': None, 'is_versioned': False, 'base_name': filename}


class CoexistenceAnalyzer:
    """共存分析器 - 判断文件如何共存"""
    
    def __init__(self, existing_files: List[Path] = None):
        self.existing_files = existing_files or []
        self.content_cache = {}
    
    def analyze_coexistence(self, new_understanding: FileUnderstanding) -> CoexistenceDecision:
        """
        分析新文件与现有文件的共存关系
        
        Returns:
            CoexistenceDecision: 共存决策
        """
        # 1. 检查完全重复
        duplicate = self._check_duplicate(new_understanding)
        if duplicate:
            return CoexistenceDecision(
                should_coexist=False,
                coexistence_type='duplicate',
                reason=f"与现有文件内容完全相同: {duplicate.name}",
                suggested_action='跳过或替换',
                related_files=[duplicate]
            )
        
        # 2. 检查版本关系
        version_rel = self._check_version_relationship(new_understanding)
        if version_rel:
            return CoexistenceDecision(
                should_coexist=True,
                coexistence_type='version',
                reason=f"检测到版本关系: {version_rel['reason']}",
                suggested_action='共存，建立版本关联',
                related_files=version_rel['files']
            )
        
        # 3. 检查变体关系
        variant_rel = self._check_variant_relationship(new_understanding)
        if variant_rel:
            return CoexistenceDecision(
                should_coexist=True,
                coexistence_type='variant',
                reason=f"检测到变体关系: {variant_rel['reason']}",
                suggested_action='共存，建立变体关联',
                related_files=variant_rel['files']
            )
        
        # 4. 检查相似文件
        similar = self._find_similar_files(new_understanding)
        if similar:
            return CoexistenceDecision(
                should_coexist=True,
                coexistence_type='distinct',
                reason=f"内容独特，但与{len(similar)}个文件有相似性",
                suggested_action='独立存储，建立相似关联',
                related_files=[s['file'] for s in similar]
            )
        
        # 5. 完全独立
        return CoexistenceDecision(
            should_coexist=True,
            coexistence_type='distinct',
            reason="内容独特，无相关文件",
            suggested_action='独立存储',
            related_files=[]
        )
    
    def _check_duplicate(self, new_understanding: FileUnderstanding) -> Optional[Path]:
        """检查是否完全重复"""
        for existing in self.existing_files:
            if existing.name == new_understanding.file_path.name:
                continue
            
            existing_hash = self._get_file_hash(existing)
            if existing_hash == new_understanding.content_hash:
                return existing
        
        return None
    
    def _check_version_relationship(self, new_understanding: FileUnderstanding) -> Optional[Dict]:
        """检查版本关系"""
        version_info = new_understanding.version_info
        
        if not version_info['is_versioned']:
            return None
        
        base_name = version_info['base_name']
        related = []
        
        for existing in self.existing_files:
            if base_name in existing.name or existing.stem in base_name:
                related.append(existing)
        
        if related:
            return {
                'reason': f"基于命名相似性检测到版本关系",
                'files': related
            }
        
        return None
    
    def _check_variant_relationship(self, new_understanding: FileUnderstanding) -> Optional[Dict]:
        """检查变体关系（如标准版vs高风险版）"""
        topic = new_understanding.core_topic
        content_type = new_understanding.content_type
        
        related = []
        for existing in self.existing_files:
            existing_content = self._get_cached_content(existing)
            
            # 检查主题相同但类型不同
            if topic in existing_content and content_type in existing_content:
                similarity = self._calculate_similarity(
                    new_understanding.full_content[:1000],
                    existing_content[:1000]
                )
                
                if 0.6 < similarity < 0.95:  # 相似但不相同
                    related.append(existing)
        
        if related:
            return {
                'reason': f"主题相同但实现不同（相似度60-95%）",
                'files': related
            }
        
        return None
    
    def _find_similar_files(self, new_understanding: FileUnderstanding) -> List[Dict]:
        """查找相似文件"""
        similar = []
        
        for existing in self.existing_files:
            existing_content = self._get_cached_content(existing)
            
            similarity = self._calculate_similarity(
                new_understanding.full_content[:2000],
                existing_content[:2000]
            )
            
            if similarity > 0.5:
                similar.append({
                    'file': existing,
                    'similarity': similarity
                })
        
        # 按相似度排序
        similar.sort(key=lambda x: x['similarity'], reverse=True)
        return similar[:3]
    
    def _get_file_hash(self, file_path: Path) -> str:
        """获取文件哈希"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""
    
    def _get_cached_content(self, file_path: Path) -> str:
        """获取缓存的内容"""
        if file_path not in self.content_cache:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    self.content_cache[file_path] = f.read()
            except:
                self.content_cache[file_path] = ""
        
        return self.content_cache[file_path]
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        return SequenceMatcher(None, text1, text2).ratio()


class NamingAdvisor:
    """命名顾问 - 基于深度理解建议命名"""
    
    def advise(self, understanding: FileUnderstanding, 
               coexistence: CoexistenceDecision) -> NamingDecision:
        """提供命名建议"""
        
        original_name = understanding.file_path.name
        
        # 基于共存决策调整命名策略
        if coexistence.coexistence_type == 'version':
            suggested_name = self._name_for_version(understanding, coexistence)
        elif coexistence.coexistence_type == 'variant':
            suggested_name = self._name_for_variant(understanding, coexistence)
        else:
            suggested_name = self._name_for_new(understanding)
        
        # 判断是否需要重命名
        should_rename = self._should_rename(original_name, suggested_name, understanding)
        
        # 生成理由
        reason = self._generate_reason(original_name, suggested_name, understanding, coexistence)
        
        # 计算置信度
        confidence = self._calculate_confidence(understanding, coexistence)
        
        # 生成备选
        alternatives = self._generate_alternatives(understanding, suggested_name)
        
        return NamingDecision(
            should_rename=should_rename,
            original_name=original_name,
            suggested_name=suggested_name,
            alternatives=alternatives,
            reason=reason,
            confidence=confidence
        )
    
    def _name_for_version(self, understanding: FileUnderstanding, 
                         coexistence: CoexistenceDecision) -> str:
        """为版本文件命名"""
        version = understanding.version_info.get('version', 'V1')
        base_name = understanding.version_info.get('base_name', understanding.core_topic)
        
        return f"{base_name}-{version}"
    
    def _name_for_variant(self, understanding: FileUnderstanding,
                         coexistence: CoexistenceDecision) -> str:
        """为变体文件命名"""
        topic = understanding.core_topic
        variant_type = self._identify_variant_type(understanding)
        content_type = understanding.content_type
        
        return f"{topic}-{variant_type}-{content_type}"
    
    def _name_for_new(self, understanding: FileUnderstanding) -> str:
        """为新文件命名"""
        parts = []
        
        # 质量标记
        if understanding.quality_level == '已验证精品':
            parts.append('终极版')
        
        # 核心主题
        parts.append(understanding.core_topic)
        
        # 内容类型
        parts.append(understanding.content_type)
        
        # 技术特性（如果有空间）
        if understanding.technical_features and len(parts) < 3:
            parts.append(understanding.technical_features[0])
        
        return '·'.join(parts[:3])
    
    def _identify_variant_type(self, understanding: FileUnderstanding) -> str:
        """识别变体类型"""
        content = understanding.full_content.lower()
        
        if '高风险' in content or '聚焦' in content:
            return '高风险聚焦版'
        elif '标准' in content:
            return '标准版'
        elif '完整' in content or '全面' in content:
            return '完整版'
        elif '简化' in content or '精简' in content:
            return '精简版'
        
        return '变体'
    
    def _should_rename(self, original: str, suggested: str, 
                      understanding: FileUnderstanding) -> bool:
        """判断是否需要重命名"""
        # 完全相同
        if original == suggested:
            return False
        
        # 原命名过于简单
        if len(original) < 15:
            return True
        
        # 建议命名包含更多信息
        if len(suggested.split('·')) > len(original.split('·')):
            return True
        
        # 原命名缺少关键信息
        if understanding.quality_level == '已验证精品' and '终极版' not in original:
            return True
        
        return False
    
    def _generate_reason(self, original: str, suggested: str,
                        understanding: FileUnderstanding,
                        coexistence: CoexistenceDecision) -> str:
        """生成命名理由"""
        reasons = []
        
        if coexistence.coexistence_type == 'version':
            reasons.append(f"版本文件，建议标准化命名")
        elif coexistence.coexistence_type == 'variant':
            reasons.append(f"变体文件，建议区分版本类型")
        
        if len(original) < 15:
            reasons.append(f"原命名过于简单")
        
        if understanding.quality_level == '已验证精品' and '终极版' not in original:
            reasons.append(f"内容质量高，建议添加质量标记")
        
        return "；".join(reasons) if reasons else "命名已较好"
    
    def _calculate_confidence(self, understanding: FileUnderstanding,
                            coexistence: CoexistenceDecision) -> float:
        """计算置信度"""
        score = 0.6
        
        # 内容理解质量
        if len(understanding.full_content) > 1000:
            score += 0.1
        
        # 实体提取
        if len(understanding.key_entities) >= 2:
            score += 0.1
        
        # 共存关系明确
        if coexistence.coexistence_type != 'distinct':
            score += 0.1
        
        return min(score, 1.0)
    
    def _generate_alternatives(self, understanding: FileUnderstanding,
                              primary: str) -> List[str]:
        """生成备选命名"""
        alternatives = []
        
        # 简化版
        parts = primary.split('·')
        if len(parts) > 2:
            alternatives.append('·'.join(parts[1:]))
        
        # 加日期版
        date_str = datetime.now().strftime("%Y%m%d")
        alternatives.append(f"{date_str}-{primary}")
        
        return alternatives[:2]


class FileProcessingPipeline:
    """文件处理流水线"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.content_reader = ContentReader()
        self.content_understander = ContentUnderstander()
        self.coexistence_analyzer = None  # 需要现有文件列表初始化
        self.naming_advisor = NamingAdvisor()
    
    def process_file(self, file_path: Path, 
                    existing_files: List[Path] = None) -> ProcessingResult:
        """
        处理单个文件的完整流程
        
        流程:
        1. 深度读取内容
        2. 理解内容实质
        3. 分析共存关系
        4. 提供命名建议
        5. 生成最终推荐
        """
        print(f"\n{'='*60}")
        print(f"📄 处理文件: {file_path.name}")
        print(f"{'='*60}")
        
        # Step 1: 深度读取
        print("\n1️⃣ 深度读取内容...")
        full_content, preview = self.content_reader.read_file(file_path)
        print(f"   内容长度: {len(full_content)} 字符")
        
        # Step 2: 理解内容
        print("\n2️⃣ 理解内容实质...")
        understanding = self.content_understander.understand(file_path, full_content, preview)
        print(f"   核心主题: {understanding.core_topic}")
        print(f"   内容类型: {understanding.content_type}")
        print(f"   质量等级: {understanding.quality_level}")
        print(f"   关键实体: {', '.join([e['name'] for e in understanding.key_entities])}")
        print(f"   核心概念: {', '.join(understanding.core_concepts)}")
        
        # Step 3: 分析共存
        print("\n3️⃣ 分析共存关系...")
        self.coexistence_analyzer = CoexistenceAnalyzer(existing_files)
        coexistence = self.coexistence_analyzer.analyze_coexistence(understanding)
        print(f"   共存类型: {coexistence.coexistence_type}")
        print(f"   是否共存: {'是' if coexistence.should_coexist else '否'}")
        print(f"   建议操作: {coexistence.suggested_action}")
        if coexistence.related_files:
            print(f"   相关文件: {len(coexistence.related_files)} 个")
        
        # Step 4: 命名建议
        print("\n4️⃣ 提供命名建议...")
        naming = self.naming_advisor.advise(understanding, coexistence)
        print(f"   原命名: {naming.original_name}")
        print(f"   建议命名: {naming.suggested_name}")
        print(f"   是否重命名: {'是' if naming.should_rename else '否'}")
        print(f"   置信度: {naming.confidence:.0%}")
        
        # Step 5: 生成最终推荐
        final_recommendation = self._generate_final_recommendation(
            understanding, coexistence, naming
        )
        
        action_plan = self._generate_action_plan(understanding, coexistence, naming)
        
        return ProcessingResult(
            understanding=understanding,
            coexistence=coexistence,
            naming=naming,
            final_recommendation=final_recommendation,
            action_plan=action_plan
        )
    
    def _generate_final_recommendation(self, understanding: FileUnderstanding,
                                      coexistence: CoexistenceDecision,
                                      naming: NamingDecision) -> str:
        """生成最终推荐"""
        parts = []
        
        # 内容理解
        parts.append(f"识别为「{understanding.content_type}」，主题「{understanding.core_topic}」")
        
        # 共存决策
        if coexistence.coexistence_type == 'duplicate':
            parts.append(f"检测到重复，建议跳过")
        elif coexistence.coexistence_type == 'version':
            parts.append(f"作为版本文件共存")
        elif coexistence.coexistence_type == 'variant':
            parts.append(f"作为变体文件共存")
        
        # 命名决策
        if naming.should_rename:
            parts.append(f"重命名为「{naming.suggested_name}」")
        
        return "；".join(parts)
    
    def _generate_action_plan(self, understanding: FileUnderstanding,
                             coexistence: CoexistenceDecision,
                             naming: NamingDecision) -> Dict:
        """生成行动计划"""
        return {
            'read_content': True,
            'analyze_content': True,
            'check_coexistence': True,
            'should_rename': naming.should_rename,
            'should_move': coexistence.should_coexist,
            'target_name': naming.suggested_name if naming.should_rename else understanding.file_path.name,
            'coexistence_type': coexistence.coexistence_type,
            'related_files': [str(f) for f in coexistence.related_files],
            'confidence': naming.confidence
        }
    
    def generate_processing_report(self, result: ProcessingResult) -> str:
        """生成处理报告"""
        report = []
        report.append(f"# 文件处理报告")
        report.append(f"**文件**: {result.understanding.file_path}")
        report.append(f"**处理时间**: {datetime.now().isoformat()}")
        report.append("")
        
        # 内容理解
        report.append("## 内容理解")
        report.append(f"- **核心主题**: {result.understanding.core_topic}")
        report.append(f"- **内容类型**: {result.understanding.content_type}")
        report.append(f"- **质量等级**: {result.understanding.quality_level}")
        report.append(f"- **关键实体**: {', '.join([e['name'] for e in result.understanding.key_entities])}")
        report.append(f"- **核心概念**: {', '.join(result.understanding.core_concepts)}")
        if result.understanding.technical_features:
            report.append(f"- **技术特性**: {', '.join(result.understanding.technical_features)}")
        report.append("")
        
        # 共存分析
        report.append("## 共存分析")
        report.append(f"- **共存类型**: {result.coexistence.coexistence_type}")
        report.append(f"- **是否共存**: {'是' if result.coexistence.should_coexist else '否'}")
        report.append(f"- **理由**: {result.coexistence.reason}")
        report.append(f"- **建议操作**: {result.coexistence.suggested_action}")
        if result.coexistence.related_files:
            report.append(f"- **相关文件**: ")
            for f in result.coexistence.related_files:
                report.append(f"  - {f.name}")
        report.append("")
        
        # 命名建议
        report.append("## 命名建议")
        report.append(f"- **原命名**: {result.naming.original_name}")
        report.append(f"- **建议命名**: {result.naming.suggested_name}")
        report.append(f"- **是否重命名**: {'是' if result.naming.should_rename else '否'}")
        report.append(f"- **理由**: {result.naming.reason}")
        report.append(f"- **置信度**: {result.naming.confidence:.0%}")
        if result.naming.alternatives:
            report.append(f"- **备选命名**: {', '.join(result.naming.alternatives)}")
        report.append("")
        
        # 最终推荐
        report.append("## 最终推荐")
        report.append(result.final_recommendation)
        report.append("")
        
        # 行动计划
        report.append("## 行动计划")
        for key, value in result.action_plan.items():
            report.append(f"- {key}: {value}")
        
        return '\n'.join(report)


def demo():
    """演示处理流程"""
    base_path = Path(__file__).resolve().parent.parent.parent  # 当前工作区根目录
    pipeline = FileProcessingPipeline(str(base_path))
    
    # 模拟现有文件
    existing = [
        base_path / "03-资产库" / "AI技能" / "示例技能.md",
    ]
    
    # 测试新文件
    test_file = Path(base_path) / "01-收件箱" / "文档.md"
    
    if test_file.exists():
        result = pipeline.process_file(test_file, existing)
        report = pipeline.generate_processing_report(result)
        print(report)
    else:
        print(f"测试文件不存在: {test_file}")


if __name__ == "__main__":
    demo()
