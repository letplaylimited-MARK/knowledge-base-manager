#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目-文件多维关系管理系统
Project-File Multi-dimensional Relationship Manager

核心能力：
1. 识别项目边界 vs 分散文件
2. 发现跨项目文件关联
3. 支持动态项目重组
4. 多维度项目视图
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class FileRelationType(Enum):
    """文件关系类型"""
    SAME_PROJECT = "same_project"           # 同一项目
    CROSS_PROJECT = "cross_project"         # 跨项目共享
    DEPENDENCY = "dependency"               # 依赖关系
    REFERENCE = "reference"                 # 引用关系
    VERSION_CHAIN = "version_chain"         # 版本链
    VARIANT = "variant"                     # 变体关系
    SIMILAR = "similar"                     # 相似关系
    TEMPORAL = "temporal"                   # 时间关联
    ENTITY_SHARED = "entity_shared"         # 共享实体


class ProjectType(Enum):
    """项目类型"""
    INDEPENDENT = "independent"             # 独立项目（完整闭环）
    SHARED_COMPONENT = "shared_component"   # 共享组件（被多项目引用）
    SUB_PROJECT = "sub_project"             # 子项目（属于更大项目）
    EMERGING = "emerging"                   # 新兴项目（正在形成）
    DISPERSED = "dispersed"                 # 分散文件（未形成项目）


@dataclass
class FileSignature:
    """文件特征签名"""
    file_path: str
    file_name: str
    content_hash: str
    entity_set: Set[str] = field(default_factory=set)
    concept_set: Set[str] = field(default_factory=set)
    topic_keywords: Set[str] = field(default_factory=set)
    related_people: Set[str] = field(default_factory=set)
    file_type: str = ""
    quality_level: str = ""
    version_info: str = ""
    
    def to_dict(self):
        return {
            "file_path": self.file_path,
            "file_name": self.file_name,
            "content_hash": self.content_hash,
            "entity_set": list(self.entity_set),
            "concept_set": list(self.concept_set),
            "topic_keywords": list(self.topic_keywords),
            "related_people": list(self.related_people),
            "file_type": self.file_type,
            "quality_level": self.quality_level,
            "version_info": self.version_info
        }


@dataclass
class ProjectCandidate:
    """项目候选（分析中的潜在项目）"""
    candidate_id: str
    name: str
    files: List[str] = field(default_factory=list)
    core_entities: Set[str] = field(default_factory=set)
    core_concepts: Set[str] = field(default_factory=set)
    project_type: ProjectType = ProjectType.EMERGING
    cohesion_score: float = 0.0              # 内聚度评分
    boundary_clarity: float = 0.0            # 边界清晰度
    confidence: float = 0.0                   # 置信度
    
    def to_dict(self):
        return {
            "candidate_id": self.candidate_id,
            "name": self.name,
            "files": self.files,
            "core_entities": list(self.core_entities),
            "core_concepts": list(self.core_concepts),
            "project_type": self.project_type.value,
            "cohesion_score": self.cohesion_score,
            "boundary_clarity": self.boundary_clarity,
            "confidence": self.confidence
        }


@dataclass
class CrossProjectRelation:
    """跨项目关系"""
    relation_id: str
    source_project: str
    target_project: str
    relation_type: FileRelationType
    shared_files: List[str] = field(default_factory=list)
    shared_entities: Set[str] = field(default_factory=set)
    relation_strength: float = 0.0
    
    def to_dict(self):
        return {
            "relation_id": self.relation_id,
            "source_project": self.source_project,
            "target_project": self.target_project,
            "relation_type": self.relation_type.value,
            "shared_files": self.shared_files,
            "shared_entities": list(self.shared_entities),
            "relation_strength": self.relation_strength
        }


@dataclass
class ProjectReorganizationProposal:
    """项目重组提案"""
    proposal_id: str
    proposal_type: str                      # "merge", "split", "extract", "create"
    description: str
    affected_files: Dict[str, str] = field(default_factory=dict)  # file -> action
    new_project_structure: Dict = field(default_factory=dict)
    benefits: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    confidence: float = 0.0
    requires_confirmation: bool = True
    
    def to_dict(self):
        return {
            "proposal_id": self.proposal_id,
            "proposal_type": self.proposal_type,
            "description": self.description,
            "affected_files": self.affected_files,
            "new_project_structure": self.new_project_structure,
            "benefits": self.benefits,
            "risks": self.risks,
            "confidence": self.confidence,
            "requires_confirmation": self.requires_confirmation
        }


class ProjectRelationshipManager:
    """项目关系管理器"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.files: Dict[str, FileSignature] = {}
        self.projects: Dict[str, ProjectCandidate] = {}
        self.cross_relations: List[CrossProjectRelation] = []
        self.reorganization_history: List[Dict] = []
        
    # ═══════════════════════════════════════════════════════════════
    # 第一阶段：深度分析文件特征
    # ═══════════════════════════════════════════════════════════════
    
    def analyze_file_signature(self, file_path: str, content: str) -> FileSignature:
        """分析文件特征签名"""
        import hashlib
        
        file_name = Path(file_path).name
        content_hash = hashlib.md5(content.encode()).hexdigest()[:16]
        
        # 提取实体
        entities = self._extract_entities(content)
        
        # 提取概念
        concepts = self._extract_concepts(content)
        
        # 提取主题关键词
        topics = self._extract_topics(content)
        
        # 提取相关人员
        people = self._extract_people(content)
        
        # 识别文件类型
        file_type = self._classify_file_type(content, file_name)
        
        # 评估质量等级
        quality = self._assess_quality(content, file_name)
        
        # 提取版本信息
        version = self._extract_version(file_name, content)
        
        return FileSignature(
            file_path=file_path,
            file_name=file_name,
            content_hash=content_hash,
            entity_set=entities,
            concept_set=concepts,
            topic_keywords=topics,
            related_people=people,
            file_type=file_type,
            quality_level=quality,
            version_info=version
        )
    
    def _extract_entities(self, content: str) -> Set[str]:
        """提取实体（主播名、指标、系统等）"""
        entities = set()
        
        # 主播名模式
        anchor_patterns = [
            r'主播[：:]?\s*([\u4e00-\u9fa5A-Za-z]+)',
            r'([\u4e00-\u9fa5]{2,4})\s*主播',
            r'主播\s*([A-Z][a-z]+)',
        ]
        for pattern in anchor_patterns:
            matches = re.findall(pattern, content)
            entities.update([f"主播:{m}" for m in matches])
        
        # 指标模式
        metric_patterns = [
            r'(钻石|收益|收入|流水)\s*[：:]?\s*(\d+)',
            r'(在线|观看|粉丝)\s*[：:]?\s*(\d+)',
        ]
        for pattern in metric_patterns:
            matches = re.findall(pattern, content)
            for m in matches:
                entities.add(f"指标:{m[0]}={m[1]}")
        
        # 系统/工具模式
        system_patterns = [
            r'(风控|审核|数据分析|日报|Prompt|提示词)系统',
            r'(ChatGPT|Claude|DeepSeek|通义千问|Kimi)',
        ]
        for pattern in system_patterns:
            matches = re.findall(pattern, content)
            entities.update([f"系统:{m}" for m in matches])
        
        return entities
    
    def _extract_concepts(self, content: str) -> Set[str]:
        """提取核心概念"""
        concepts = set()
        
        concept_keywords = [
            "零幻觉", "跨AI", "批量处理", "实时", "自动化",
            "agen", "gen", "风控", "审核", "数据分析",
            "Prompt工程", "提示词", "运营", "主播管理"
        ]
        
        for keyword in concept_keywords:
            if keyword in content:
                concepts.add(keyword)
        
        return concepts
    
    def _extract_topics(self, content: str) -> Set[str]:
        """提取主题关键词"""
        topics = set()
        
        # 基于内容长度和关键词密度提取主题
        topic_indicators = {
            "风控审核": ["风控", "审核", "风险", "违规", "检测"],
            "数据分析": ["数据", "分析", "报表", "统计", "指标"],
            "主播管理": ["主播", "管理", "运营", "培训", "考核"],
            "Prompt工程": ["Prompt", "提示词", "AI", "生成"],
            "会议记录": ["会议", "讨论", "决策", "纪要"],
            "项目文档": ["项目", "需求", "设计", "方案"]
        }
        
        for topic, indicators in topic_indicators.items():
            score = sum(1 for ind in indicators if ind in content)
            if score >= 2:
                topics.add(topic)
        
        return topics
    
    def _extract_people(self, content: str) -> Set[str]:
        """提取相关人员"""
        people = set()
        
        # 常见人名模式
        name_patterns = [
            r'([\u4e00-\u9fa5]{2,3})(?:老师|师傅|经理|主管|总监)',
            r'(?:汇报人|负责人|主讲)[：:]\s*([\u4e00-\u9fa5]{2,3})',
        ]
        
        for pattern in name_patterns:
            matches = re.findall(pattern, content)
            people.update(matches)
        
        return people
    
    def _classify_file_type(self, content: str, file_name: str) -> str:
        """分类文件类型"""
        if "Prompt" in content or "提示词" in content:
            return "Prompt模板"
        elif "风控" in content and ("审核" in content or "检测" in content):
            return "风控系统文档"
        elif "数据分析" in content or "报表" in content:
            return "数据分析文档"
        elif "主播" in content and ("诊断" in content or "分析" in content):
            return "主播诊断报告"
        elif "会议" in content or "纪要" in content:
            return "会议纪要"
        elif ".md" in file_name:
            return "Markdown文档"
        elif ".txt" in file_name:
            return "文本文档"
        else:
            return "其他"
    
    def _assess_quality(self, content: str, file_name: str) -> str:
        """评估质量等级"""
        if "终极版" in file_name or "已验证" in file_name:
            return "已验证精品"
        elif len(content) > 2000 and ("示例" in content or "模板" in content):
            return "内容完整"
        elif "V" in file_name or "版本" in file_name:
            return "迭代版本"
        else:
            return "标准"
    
    def _extract_version(self, file_name: str, content: str) -> str:
        """提取版本信息"""
        version_patterns = [
            r'V(\d+\.?\d*)',
            r'版本[：:]?\s*(\d+\.?\d*)',
            r'(\d+\.\d+)版',
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, file_name + " " + content)
            if match:
                return f"V{match.group(1)}"
        
        if "终极版" in file_name:
            return "final"
        
        return "unknown"
    
    # ═══════════════════════════════════════════════════════════════
    # 第二阶段：项目边界识别
    # ═══════════════════════════════════════════════════════════════
    
    def identify_project_boundaries(self, files: List[FileSignature]) -> List[ProjectCandidate]:
        """识别项目边界"""
        print("🔍 正在分析项目边界...")
        
        # 1. 基于实体重叠度聚类
        entity_groups = self._cluster_by_entity_overlap(files)
        
        # 2. 基于主题相似度聚类
        topic_groups = self._cluster_by_topic_similarity(files)
        
        # 3. 基于文件命名模式聚类
        naming_groups = self._cluster_by_naming_pattern(files)
        
        # 4. 合并聚类结果
        merged_projects = self._merge_clusters(entity_groups, topic_groups, naming_groups)
        
        # 5. 评估每个候选项目的质量
        for project in merged_projects:
            self._assess_project_quality(project)
        
        return merged_projects
    
    def _cluster_by_entity_overlap(self, files: List[FileSignature]) -> List[Set[str]]:
        """基于实体重叠度聚类"""
        from collections import defaultdict
        
        entity_to_files = defaultdict(set)
        for f in files:
            for entity in f.entity_set:
                entity_to_files[entity].add(f.file_path)
        
        # 使用并查集找到连通分量
        parent = {f.file_path: f.file_path for f in files}
        
        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        
        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py
        
        # 如果两个文件共享实体，则合并
        for entity, file_set in entity_to_files.items():
            if len(file_set) > 1:
                file_list = list(file_set)
                for i in range(1, len(file_list)):
                    union(file_list[0], file_list[i])
        
        # 收集聚类结果
        clusters = defaultdict(set)
        for f in files:
            clusters[find(f.file_path)].add(f.file_path)
        
        return list(clusters.values())
    
    def _cluster_by_topic_similarity(self, files: List[FileSignature]) -> List[Set[str]]:
        """基于主题相似度聚类"""
        clusters = []
        used = set()
        
        for f in files:
            if f.file_path in used:
                continue
            
            cluster = {f.file_path}
            used.add(f.file_path)
            
            for other in files:
                if other.file_path in used:
                    continue
                
                # 计算主题重叠度
                overlap = len(f.topic_keywords & other.topic_keywords)
                if overlap >= 1:  # 至少一个共同主题
                    cluster.add(other.file_path)
                    used.add(other.file_path)
            
            clusters.append(cluster)
        
        return clusters
    
    def _cluster_by_naming_pattern(self, files: List[FileSignature]) -> List[Set[str]]:
        """基于命名模式聚类"""
        from collections import defaultdict
        
        pattern_groups = defaultdict(set)
        
        for f in files:
            # 提取命名前缀
            name = Path(f.file_path).stem
            
            # 寻找共同前缀
            for prefix_len in range(min(10, len(name)), 2, -1):
                prefix = name[:prefix_len]
                if any(c in prefix for c in ['-', '_', '·', ' ']):
                    pattern_groups[prefix].add(f.file_path)
                    break
            else:
                pattern_groups["other"].add(f.file_path)
        
        return list(pattern_groups.values())
    
    def _merge_clusters(self, *cluster_lists) -> List[ProjectCandidate]:
        """合并多种聚类结果"""
        # 简化的合并策略：取并集
        all_files = set()
        for clusters in cluster_lists:
            for cluster in clusters:
                all_files.update(cluster)
        
        # 构建文件邻接图
        adjacency = {f: set() for f in all_files}
        
        for clusters in cluster_lists:
            for cluster in clusters:
                file_list = list(cluster)
                for i, f1 in enumerate(file_list):
                    for f2 in file_list[i+1:]:
                        adjacency[f1].add(f2)
                        adjacency[f2].add(f1)
        
        # 找到连通分量作为项目候选
        visited = set()
        projects = []
        project_id = 0
        
        for file_path in all_files:
            if file_path in visited:
                continue
            
            # BFS找到连通分量
            component = set()
            queue = [file_path]
            
            while queue:
                current = queue.pop(0)
                if current in visited:
                    continue
                visited.add(current)
                component.add(current)
                queue.extend(adjacency[current] - visited)
            
            # 创建项目候选
            project_id += 1
            project = ProjectCandidate(
                candidate_id=f"proj_{project_id:03d}",
                name=self._generate_project_name(component),
                files=list(component)
            )
            projects.append(project)
        
        return projects
    
    def _generate_project_name(self, file_paths: Set[str]) -> str:
        """生成项目名称"""
        # 基于共同实体或主题生成名称
        return f"项目_{len(file_paths)}个文件"
    
    def _assess_project_quality(self, project: ProjectCandidate):
        """评估项目质量"""
        # 计算内聚度
        if len(project.files) <= 1:
            project.cohesion_score = 1.0
            project.boundary_clarity = 1.0
            project.project_type = ProjectType.DISPERSED
            return
        
        # 收集所有实体和概念
        all_entities = set()
        all_concepts = set()
        
        for file_path in project.files:
            if file_path in self.files:
                f = self.files[file_path]
                all_entities.update(f.entity_set)
                all_concepts.update(f.concept_set)
        
        project.core_entities = all_entities
        project.core_concepts = all_concepts
        
        # 计算内聚度（共享实体比例）
        if all_entities:
            shared_count = 0
            for entity in all_entities:
                count = sum(1 for f in project.files 
                          if f in self.files and entity in self.files[f].entity_set)
                if count > 1:
                    shared_count += 1
            project.cohesion_score = shared_count / len(all_entities)
        
        # 判断项目类型
        if len(project.files) >= 3 and project.cohesion_score > 0.3:
            project.project_type = ProjectType.INDEPENDENT
        elif project.cohesion_score < 0.1:
            project.project_type = ProjectType.DISPERSED
        else:
            project.project_type = ProjectType.EMERGING
        
        project.confidence = project.cohesion_score * 0.5 + 0.5
    
    # ═══════════════════════════════════════════════════════════════
    # 第三阶段：发现跨项目关联
    # ═══════════════════════════════════════════════════════════════
    
    def discover_cross_project_relations(self) -> List[CrossProjectRelation]:
        """发现跨项目关联"""
        print("🔗 正在发现跨项目关联...")
        
        relations = []
        project_list = list(self.projects.values())
        
        for i, proj1 in enumerate(project_list):
            for proj2 in project_list[i+1:]:
                relation = self._analyze_project_relation(proj1, proj2)
                if relation:
                    relations.append(relation)
        
        self.cross_relations = relations
        return relations
    
    def _analyze_project_relation(self, proj1: ProjectCandidate, 
                                   proj2: ProjectCandidate) -> Optional[CrossProjectRelation]:
        """分析两个项目之间的关系"""
        
        # 检查共享文件
        shared_files = set(proj1.files) & set(proj2.files)
        
        # 检查共享实体
        shared_entities = proj1.core_entities & proj2.core_entities
        
        # 检查共享概念
        shared_concepts = proj1.core_concepts & proj2.core_concepts
        
        # 计算关系强度
        strength = 0.0
        
        if shared_files:
            strength += len(shared_files) * 0.3
        
        if shared_entities:
            strength += len(shared_entities) * 0.1
        
        if shared_concepts:
            strength += len(shared_concepts) * 0.1
        
        # 检查命名相似度
        name_similarity = self._calculate_name_similarity(proj1.name, proj2.name)
        strength += name_similarity * 0.2
        
        if strength < 0.2:
            return None
        
        # 确定关系类型
        if shared_files:
            relation_type = FileRelationType.CROSS_PROJECT
        elif shared_entities:
            relation_type = FileRelationType.ENTITY_SHARED
        elif shared_concepts:
            relation_type = FileRelationType.SIMILAR
        else:
            relation_type = FileRelationType.TEMPORAL
        
        return CrossProjectRelation(
            relation_id=f"rel_{proj1.candidate_id}_{proj2.candidate_id}",
            source_project=proj1.candidate_id,
            target_project=proj2.candidate_id,
            relation_type=relation_type,
            shared_files=list(shared_files),
            shared_entities=shared_entities,
            relation_strength=min(strength, 1.0)
        )
    
    def _calculate_name_similarity(self, name1: str, name2: str) -> float:
        """计算名称相似度"""
        # 简单的字符重叠度
        chars1 = set(name1)
        chars2 = set(name2)
        
        if not chars1 or not chars2:
            return 0.0
        
        intersection = chars1 & chars2
        union = chars1 | chars2
        
        return len(intersection) / len(union)
    
    # ═══════════════════════════════════════════════════════════════
    # 第四阶段：项目重组建议
    # ═══════════════════════════════════════════════════════════════
    
    def generate_reorganization_proposals(self) -> List[ProjectReorganizationProposal]:
        """生成项目重组建议"""
        print("💡 正在生成重组建议...")
        
        proposals = []
        
        # 1. 合并建议：高度关联的小项目
        merge_proposals = self._suggest_merges()
        proposals.extend(merge_proposals)
        
        # 2. 拆分建议：内聚度低的大项目
        split_proposals = self._suggest_splits()
        proposals.extend(split_proposals)
        
        # 3. 提取建议：跨项目共享文件
        extract_proposals = self._suggest_extractions()
        proposals.extend(extract_proposals)
        
        # 4. 新建项目建议：分散文件组合
        create_proposals = self._suggest_new_projects()
        proposals.extend(create_proposals)
        
        return proposals
    
    def _suggest_merges(self) -> List[ProjectReorganizationProposal]:
        """建议合并高度关联的项目"""
        proposals = []
        
        for relation in self.cross_relations:
            if relation.relation_strength > 0.7:
                proj1 = self.projects.get(relation.source_project)
                proj2 = self.projects.get(relation.target_project)
                
                if proj1 and proj2:
                    proposal = ProjectReorganizationProposal(
                        proposal_id=f"merge_{relation.relation_id}",
                        proposal_type="merge",
                        description=f"建议合并项目 '{proj1.name}' 和 '{proj2.name}'，因为它们有强关联（强度{relation.relation_strength:.2f}）",
                        affected_files={f: "合并到新项目" for f in proj1.files + proj2.files},
                        new_project_structure={
                            "name": f"{proj1.name}+{proj2.name}",
                            "files": proj1.files + proj2.files
                        },
                        benefits=[
                            "减少项目碎片化",
                            "统一管理相关文件",
                            f"共享{len(relation.shared_entities)}个实体"
                        ],
                        risks=[
                            "项目边界可能变得模糊",
                            "需要重新组织目录结构"
                        ],
                        confidence=relation.relation_strength,
                        requires_confirmation=True
                    )
                    proposals.append(proposal)
        
        return proposals
    
    def _suggest_splits(self) -> List[ProjectReorganizationProposal]:
        """建议拆分内聚度低的大项目"""
        proposals = []
        
        for project in self.projects.values():
            if len(project.files) > 5 and project.cohesion_score < 0.3:
                # 建议拆分为子项目
                sub_groups = self._identify_sub_groups(project)
                
                if len(sub_groups) > 1:
                    proposal = ProjectReorganizationProposal(
                        proposal_id=f"split_{project.candidate_id}",
                        proposal_type="split",
                        description=f"建议将项目 '{project.name}' 拆分为{len(sub_groups)}个子项目，因为当前内聚度较低({project.cohesion_score:.2f})",
                        affected_files={f: "重新分配到子项目" for f in project.files},
                        new_project_structure={
                            "original": project.name,
                            "sub_projects": [
                                {"name": f"{project.name}-子项目{i+1}", "files": list(group)}
                                for i, group in enumerate(sub_groups)
                            ]
                        },
                        benefits=[
                            "提高项目内聚度",
                            "更清晰的职责边界",
                            "便于独立管理"
                        ],
                        risks=[
                            "增加项目数量",
                            "需要维护子项目间关系"
                        ],
                        confidence=1 - project.cohesion_score,
                        requires_confirmation=True
                    )
                    proposals.append(proposal)
        
        return proposals
    
    def _identify_sub_groups(self, project: ProjectCandidate) -> List[Set[str]]:
        """识别项目内的子组"""
        # 基于实体相似度重新聚类
        files = [self.files.get(f) for f in project.files if f in self.files]
        files = [f for f in files if f]
        
        if len(files) <= 1:
            return [{f.file_path} for f in files]
        
        # 使用简单的贪心聚类
        groups = []
        used = set()
        
        for f in files:
            if f.file_path in used:
                continue
            
            group = {f.file_path}
            used.add(f.file_path)
            
            for other in files:
                if other.file_path in used:
                    continue
                
                # 计算实体相似度
                overlap = len(f.entity_set & other.entity_set)
                if overlap >= 2:  # 至少2个共同实体
                    group.add(other.file_path)
                    used.add(other.file_path)
            
            groups.append(group)
        
        return groups
    
    def _suggest_extractions(self) -> List[ProjectReorganizationProposal]:
        """建议提取共享组件"""
        proposals = []
        
        # 找出在多个项目中出现的文件
        file_project_count = {}
        for project in self.projects.values():
            for f in project.files:
                file_project_count[f] = file_project_count.get(f, 0) + 1
        
        shared_files = {f: count for f, count in file_project_count.items() if count > 1}
        
        if shared_files:
            proposal = ProjectReorganizationProposal(
                proposal_id="extract_shared",
                proposal_type="extract",
                description=f"建议提取{len(shared_files)}个共享文件为独立组件",
                affected_files={f: "提取为共享组件" for f in shared_files},
                new_project_structure={
                    "shared_component": {
                        "name": "共享组件库",
                        "files": list(shared_files.keys())
                    }
                },
                benefits=[
                    "避免重复存储",
                    "统一管理共享资源",
                    "便于版本控制"
                ],
                risks=[
                    "需要维护引用关系",
                    "修改可能影响多个项目"
                ],
                confidence=0.8,
                requires_confirmation=True
            )
            proposals.append(proposal)
        
        return proposals
    
    def _suggest_new_projects(self) -> List[ProjectReorganizationProposal]:
        """建议从分散文件创建新项目"""
        proposals = []
        
        # 找出分散的文件（不属于任何强内聚项目）
        dispersed_files = []
        for project in self.projects.values():
            if project.project_type == ProjectType.DISPERSED:
                dispersed_files.extend(project.files)
        
        if len(dispersed_files) >= 3:
            # 尝试重新聚类
            file_sigs = [self.files.get(f) for f in dispersed_files if f in self.files]
            file_sigs = [f for f in file_sigs if f]
            
            if file_sigs:
                new_clusters = self._cluster_by_entity_overlap(file_sigs)
                
                for i, cluster in enumerate(new_clusters):
                    if len(cluster) >= 3:
                        proposal = ProjectReorganizationProposal(
                            proposal_id=f"create_new_{i}",
                            proposal_type="create",
                            description=f"建议从分散文件中创建新项目，包含{len(cluster)}个相关文件",
                            affected_files={f: "归入新项目" for f in cluster},
                            new_project_structure={
                                "new_project": {
                                    "name": f"新建项目-{i+1}",
                                    "files": list(cluster)
                                }
                            },
                            benefits=[
                                "整合相关文件",
                                "形成完整项目视图",
                                "便于后续管理"
                            ],
                            risks=[
                                "项目边界需要进一步确认",
                                "可能需要调整"
                            ],
                            confidence=0.6,
                            requires_confirmation=True
                        )
                        proposals.append(proposal)
        
        return proposals
    
    # ═══════════════════════════════════════════════════════════════
    # 第五阶段：交互式确认
    # ═══════════════════════════════════════════════════════════════
    
    def generate_interactive_questions(self) -> List[Dict]:
        """生成交互式确认问题"""
        questions = []
        
        # 1. 询问项目边界问题
        for project in self.projects.values():
            if project.project_type == ProjectType.EMERGING:
                questions.append({
                    "type": "project_boundary",
                    "target": project.candidate_id,
                    "question": f"项目 '{project.name}' 包含{len(project.files)}个文件，内聚度{project.cohesion_score:.2f}。",
                    "options": [
                        "这是一个独立项目",
                        "这是更大项目的一部分（子项目）",
                        "这些文件应该分散到不同项目",
                        "需要进一步分析"
                    ],
                    "context": {
                        "files": project.files[:5],  # 显示前5个文件
                        "entities": list(project.core_entities)[:5]
                    }
                })
        
        # 2. 询问跨项目关联
        for relation in self.cross_relations:
            if relation.relation_strength > 0.5:
                proj1 = self.projects.get(relation.source_project)
                proj2 = self.projects.get(relation.target_project)
                
                if proj1 and proj2:
                    questions.append({
                        "type": "cross_project_relation",
                        "target": relation.relation_id,
                        "question": f"发现项目 '{proj1.name}' 和 '{proj2.name}' 有关联（强度{relation.relation_strength:.2f}）",
                        "options": [
                            "合并为一个项目",
                            "保持独立但建立关联",
                            "提取共享部分为组件",
                            "无实际关联，忽略"
                        ],
                        "context": {
                            "shared_entities": list(relation.shared_entities)[:5],
                            "relation_type": relation.relation_type.value
                        }
                    })
        
        return questions
    
    # ═══════════════════════════════════════════════════════════════
    # 输出和报告
    # ═══════════════════════════════════════════════════════════════
    
    def generate_comprehensive_report(self) -> Dict:
        """生成综合分析报告"""
        return {
            "analysis_summary": {
                "total_files": len(self.files),
                "identified_projects": len(self.projects),
                "cross_project_relations": len(self.cross_relations),
                "project_types": {
                    "independent": sum(1 for p in self.projects.values() if p.project_type == ProjectType.INDEPENDENT),
                    "shared_component": sum(1 for p in self.projects.values() if p.project_type == ProjectType.SHARED_COMPONENT),
                    "sub_project": sum(1 for p in self.projects.values() if p.project_type == ProjectType.SUB_PROJECT),
                    "emerging": sum(1 for p in self.projects.values() if p.project_type == ProjectType.EMERGING),
                    "dispersed": sum(1 for p in self.projects.values() if p.project_type == ProjectType.DISPERSED)
                }
            },
            "projects": [p.to_dict() for p in self.projects.values()],
            "cross_relations": [r.to_dict() for r in self.cross_relations],
            "reorganization_proposals": [p.to_dict() for p in self.generate_reorganization_proposals()],
            "interactive_questions": self.generate_interactive_questions()
        }


# ═══════════════════════════════════════════════════════════════════
# 使用示例
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # 创建管理器实例
    manager = ProjectRelationshipManager(
        base_path=str(Path(__file__).resolve().parent.parent.parent)
    )
    
    print("=" * 60)
    print("项目-文件多维关系管理系统")
    print("=" * 60)
    print()
    
    # 这里可以添加实际文件分析代码
    print("✅ 系统初始化完成")
    print("📖 使用说明：")
    print("   1. 调用 analyze_file_signature() 分析单个文件")
    print("   2. 调用 identify_project_boundaries() 识别项目")
    print("   3. 调用 discover_cross_project_relations() 发现关联")
    print("   4. 调用 generate_reorganization_proposals() 获取重组建议")
    print("   5. 调用 generate_interactive_questions() 获取确认问题")
