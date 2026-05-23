#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目决策工作流
Project Decision Workflow

核心流程：
1. 文件丢入 → 2. 深度分析 → 3. 项目识别 → 4. 关联发现 → 5. 决策询问 → 6. 执行重组
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List
from dataclasses import dataclass, field
import hashlib


@dataclass
class ProcessingDecision:
    """处理决策"""
    decision_id: str
    file_path: str
    decision_type: str                      # "new_project", "existing_project", "shared", "dispersed"
    target_location: str
    reasoning: str
    confidence: float
    requires_confirmation: bool
    alternatives: List[Dict] = field(default_factory=list)

    def to_dict(self):
        return {
            "decision_id": self.decision_id,
            "file_path": self.file_path,
            "decision_type": self.decision_type,
            "target_location": self.target_location,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "requires_confirmation": self.requires_confirmation,
            "alternatives": self.alternatives
        }


@dataclass
class ProjectInsight:
    """项目洞察"""
    insight_type: str                       # "pattern", "relation", "suggestion", "warning"
    description: str
    affected_files: List[str]
    recommended_action: str
    priority: str = "normal"                # "high", "normal", "low"

    def to_dict(self):
        return {
            "insight_type": self.insight_type,
            "description": self.description,
            "affected_files": self.affected_files,
            "recommended_action": self.recommended_action,
            "priority": self.priority
        }


class ProjectDecisionWorkflow:
    """项目决策工作流"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.decisions: List[ProcessingDecision] = []
        self.insights: List[ProjectInsight] = []
        self.processing_log: List[Dict] = []

    # ═══════════════════════════════════════════════════════════════
    # 第一步：接收新文件
    # ═══════════════════════════════════════════════════════════════

    def receive_new_file(self, file_path: str, content: str) -> Dict:
        """接收新文件，启动处理流程"""
        print(f"📥 接收新文件: {file_path}")

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "file_path": file_path,
            "content_length": len(content),
            "stage": "received"
        }
        self.processing_log.append(log_entry)

        return {
            "status": "received",
            "file_path": file_path,
            "next_step": "深度内容分析"
        }

    # ═══════════════════════════════════════════════════════════════
    # 第二步：深度内容分析
    # ═══════════════════════════════════════════════════════════════

    def deep_content_analysis(self, file_path: str, content: str) -> Dict:
        """深度分析文件内容"""
        print(f"🔍 深度分析内容: {file_path}")

        # 分析文件特征
        analysis = {
            "file_path": file_path,
            "content_summary": content[:500] + "..." if len(content) > 500 else content,
            "content_length": len(content),
            "detected_themes": self._extract_themes(content),
            "detected_entities": self._extract_entities(content),
            "detected_projects": self._detect_project_mentions(content),
            "quality_indicators": self._assess_quality_indicators(content),
            "version_info": self._extract_version_info(file_path, content)
        }

        # 记录日志
        self.processing_log.append({
            "timestamp": datetime.now().isoformat(),
            "file_path": file_path,
            "stage": "content_analysis",
            "themes": analysis["detected_themes"],
            "entities": analysis["detected_entities"]
        })

        return analysis

    def _extract_themes(self, content: str) -> List[str]:
        """提取主题"""
        themes = []

        theme_keywords = {
            "风控审核": ["风控", "审核", "风险", "违规", "检测", "预警"],
            "数据分析": ["数据", "分析", "报表", "统计", "指标", "可视化"],
            "主播管理": ["主播", "管理", "运营", "培训", "考核", "诊断"],
            "Prompt工程": ["Prompt", "提示词", "AI", "生成", "LLM"],
            "会议记录": ["会议", "讨论", "决策", "纪要", "议题"],
            "项目管理": ["项目", "需求", "设计", "方案", "规划"],
            "知识沉淀": ["知识", "方法", "经验", "总结", "最佳实践"]
        }

        for theme, keywords in theme_keywords.items():
            score = sum(2 if kw in content else 0 for kw in keywords)
            if score >= 4:
                themes.append(theme)

        return themes

    def _extract_entities(self, content: str) -> List[Dict]:
        """提取实体"""
        import re

        entities = []

        # 主播名
        anchor_pattern = r'主播[：:]?\s*([\u4e00-\u9fa5A-Za-z]+)'
        for match in re.finditer(anchor_pattern, content):
            entities.append({
                "type": "主播",
                "name": match.group(1),
                "context": content[max(0, match.start()-20):match.end()+20]
            })

        # 系统/工具
        system_pattern = r'(风控|审核|数据分析|日报|Prompt|提示词)系统'
        for match in re.finditer(system_pattern, content):
            entities.append({
                "type": "系统",
                "name": match.group(1),
                "context": ""
            })

        # 指标数据
        metric_pattern = r'(钻石|收益|收入|流水|在线|观看)\s*[：:]?\s*(\d+)'
        for match in re.finditer(metric_pattern, content):
            entities.append({
                "type": "指标",
                "name": f"{match.group(1)}={match.group(2)}",
                "context": ""
            })

        return entities

    def _detect_project_mentions(self, content: str) -> List[str]:
        """检测提到的项目"""
        projects = []

        # 从内容中识别可能的项目名称
        project_indicators = [
            "风控审核系统", "数据分析系统", "主播管理系统",
            "Prompt库", "知识库", "运营体系"
        ]

        for indicator in project_indicators:
            if indicator in content:
                projects.append(indicator)

        return projects

    def _assess_quality_indicators(self, content: str) -> Dict:
        """评估质量指标"""
        indicators = {
            "has_examples": "示例" in content or "Example" in content,
            "has_templates": "模板" in content or "Template" in content,
            "has_instructions": "说明" in content or "Instructions" in content,
            "is_structured": content.count("#") > 3 or content.count("-") > 10,
            "has_metrics": any(c.isdigit() for c in content),
            "length_category": "long" if len(content) > 3000 else "medium" if len(content) > 1000 else "short"
        }

        return indicators

    def _extract_version_info(self, file_path: str, content: str) -> Dict:
        """提取版本信息"""
        import re

        version_info = {
            "detected_version": None,
            "is_final": False,
            "is_draft": False
        }

        # 从文件名提取
        file_name = Path(file_path).name

        if "终极版" in file_name or "final" in file_name.lower():
            version_info["is_final"] = True

        if "草稿" in file_name or "draft" in file_name.lower():
            version_info["is_draft"] = True

        version_match = re.search(r'V(\d+\.?\d*)', file_name + " " + content)
        if version_match:
            version_info["detected_version"] = f"V{version_match.group(1)}"

        return version_info

    # ═══════════════════════════════════════════════════════════════
    # 第三步：项目识别与匹配
    # ═══════════════════════════════════════════════════════════════

    def identify_project_match(self, file_analysis: Dict,
                               existing_projects: List[Dict]) -> Dict:
        """识别文件与现有项目的匹配关系"""
        print(f"🎯 识别项目匹配: {file_analysis['file_path']}")

        matches = []

        for project in existing_projects:
            score = self._calculate_project_match_score(file_analysis, project)
            if score > 0.3:  # 阈值
                matches.append({
                    "project_id": project.get("id"),
                    "project_name": project.get("name"),
                    "match_score": score,
                    "match_reasons": self._explain_match_reasons(file_analysis, project)
                })

        # 按匹配度排序
        matches.sort(key=lambda x: x["match_score"], reverse=True)

        result = {
            "file_path": file_analysis["file_path"],
            "top_matches": matches[:3],
            "match_type": self._determine_match_type(matches),
            "recommendation": self._generate_match_recommendation(matches, file_analysis)
        }

        return result

    def _calculate_project_match_score(self, file_analysis: Dict,
                                        project: Dict) -> float:
        """计算文件与项目的匹配分数"""
        score = 0.0

        # 主题匹配
        file_themes = set(file_analysis.get("detected_themes", []))
        project_themes = set(project.get("themes", []))
        theme_overlap = len(file_themes & project_themes)
        score += theme_overlap * 0.3

        # 实体匹配
        file_entities = {e["name"] for e in file_analysis.get("detected_entities", [])}
        project_entities = set(project.get("entities", []))
        entity_overlap = len(file_entities & project_entities)
        score += entity_overlap * 0.2

        # 项目名称提及
        if project.get("name") in file_analysis.get("detected_projects", []):
            score += 0.5

        return min(score, 1.0)

    def _explain_match_reasons(self, file_analysis: Dict, project: Dict) -> List[str]:
        """解释匹配原因"""
        reasons = []

        file_themes = set(file_analysis.get("detected_themes", []))
        project_themes = set(project.get("themes", []))
        shared_themes = file_themes & project_themes
        if shared_themes:
            reasons.append(f"共同主题: {', '.join(shared_themes)}")

        file_entities = {e["name"] for e in file_analysis.get("detected_entities", [])}
        project_entities = set(project.get("entities", []))
        shared_entities = file_entities & project_entities
        if shared_entities:
            reasons.append(f"共享实体: {', '.join(list(shared_entities)[:3])}")

        return reasons

    def _determine_match_type(self, matches: List[Dict]) -> str:
        """确定匹配类型"""
        if not matches:
            return "no_match"

        top_score = matches[0]["match_score"]

        if top_score > 0.8:
            return "strong_match"
        elif top_score > 0.5:
            return "moderate_match"
        elif top_score > 0.3:
            return "weak_match"
        else:
            return "no_match"

    def _generate_match_recommendation(self, matches: List[Dict],
                                        file_analysis: Dict) -> Dict:
        """生成匹配建议"""
        if not matches:
            return {
                "action": "create_new_project",
                "reason": "未找到匹配的项目，建议创建新项目或作为分散文件管理",
                "confidence": 0.7
            }

        top_match = matches[0]

        if top_match["match_score"] > 0.8:
            return {
                "action": "add_to_existing",
                "target_project": top_match["project_name"],
                "reason": f"与项目 '{top_match['project_name']}' 高度匹配（{top_match['match_score']:.2f}）",
                "confidence": top_match["match_score"]
            }
        elif len(matches) >= 2 and matches[1]["match_score"] > 0.5:
            return {
                "action": "needs_decision",
                "candidates": [m["project_name"] for m in matches[:2]],
                "reason": "多个项目匹配度相近，需要人工决策",
                "confidence": 0.5
            }
        else:
            return {
                "action": "create_new_project",
                "reason": "匹配度不足，建议创建新项目",
                "confidence": 0.6
            }

    # ═══════════════════════════════════════════════════════════════
    # 第四步：生成决策询问
    # ═══════════════════════════════════════════════════════════════

    def generate_decision_questions(self, file_analysis: Dict,
                                     match_result: Dict) -> List[Dict]:
        """生成需要用户确认的决策问题"""
        print(f"❓ 生成决策问题: {file_analysis['file_path']}")

        questions = []

        recommendation = match_result.get("recommendation", {})
        action = recommendation.get("action")

        if action == "create_new_project":
            questions.append({
                "question_id": f"q_{int(hashlib.md5(file_analysis['file_path'].encode()).hexdigest()[:8], 16) % 10000}",
                "type": "project_creation",
                "question": f"文件 '{Path(file_analysis['file_path']).name}' 未找到强匹配项目",
                "context": {
                    "detected_themes": file_analysis.get("detected_themes", []),
                    "detected_entities": [e["name"] for e in file_analysis.get("detected_entities", [])[:5]],
                    "content_length": file_analysis.get("content_length")
                },
                "options": [
                    {
                        "id": "create_independent",
                        "label": "创建独立项目",
                        "description": "这是一个独立的项目，需要完整管理"
                    },
                    {
                        "id": "create_sub_project",
                        "label": "作为子项目",
                        "description": "这是某个大项目的一部分"
                    },
                    {
                        "id": "keep_dispersed",
                        "label": "保持分散",
                        "description": "暂时不形成项目，按主题分散存储"
                    },
                    {
                        "id": "analyze_more",
                        "label": "需要更多分析",
                        "description": "先不决定，继续观察其他文件"
                    }
                ]
            })

        elif action == "add_to_existing":
            target = recommendation.get("target_project")
            questions.append({
                "question_id": f"q_{int(hashlib.md5(file_analysis['file_path'].encode()).hexdigest()[:8], 16) % 10000}",
                "type": "project_addition",
                "question": f"建议将文件加入项目 '{target}'",
                "context": {
                    "target_project": target,
                    "match_score": recommendation.get("confidence"),
                    "detected_themes": file_analysis.get("detected_themes", [])
                },
                "options": [
                    {
                        "id": "confirm_add",
                        "label": "确认加入",
                        "description": f"加入项目 '{target}'"
                    },
                    {
                        "id": "create_separate",
                        "label": "创建独立项目",
                        "description": "虽然有关联，但应该独立管理"
                    },
                    {
                        "id": "shared_component",
                        "label": "作为共享组件",
                        "description": "这个文件可能被多个项目使用"
                    },
                    {
                        "id": "defer",
                        "label": "暂不决定",
                        "description": "先放入收件箱，稍后决定"
                    }
                ]
            })

        elif action == "needs_decision":
            candidates = recommendation.get("candidates", [])
            questions.append({
                "question_id": f"q_{int(hashlib.md5(file_analysis['file_path'].encode()).hexdigest()[:8], 16) % 10000}",
                "type": "multi_project_choice",
                "question": "文件可能与多个项目相关",
                "context": {
                    "candidates": candidates,
                    "detected_themes": file_analysis.get("detected_themes", [])
                },
                "options": [
                    {
                        "id": f"join_{candidates[0]}",
                        "label": f"加入 '{candidates[0]}'",
                        "description": "选择第一个项目"
                    },
                    {
                        "id": f"join_{candidates[1]}",
                        "label": f"加入 '{candidates[1]}'",
                        "description": "选择第二个项目"
                    },
                    {
                        "id": "shared",
                        "label": "作为共享资源",
                        "description": "两个项目都引用这个文件"
                    },
                    {
                        "id": "new_project",
                        "label": "创建新项目",
                        "description": "这是一个独立的新项目"
                    }
                ]
            })

        # 添加命名优化问题
        current_name = Path(file_analysis['file_path']).name
        suggested_name = self._suggest_optimized_name(file_analysis)

        if suggested_name != current_name:
            questions.append({
                "question_id": f"q_name_{hash(file_analysis['file_path']) % 10000}",
                "type": "naming_optimization",
                "question": "建议优化文件命名",
                "context": {
                    "current_name": current_name,
                    "suggested_name": suggested_name,
                    "reasoning": self._explain_naming_reasoning(file_analysis)
                },
                "options": [
                    {
                        "id": "accept_suggestion",
                        "label": f"接受建议: {suggested_name}",
                        "description": "使用优化后的命名"
                    },
                    {
                        "id": "keep_original",
                        "label": f"保持原样: {current_name}",
                        "description": "不修改文件名"
                    },
                    {
                        "id": "custom_name",
                        "label": "自定义命名",
                        "description": "我自己决定命名"
                    }
                ]
            })

        return questions

    def _suggest_optimized_name(self, file_analysis: Dict) -> str:
        """建议优化的文件名"""
        current_name = Path(file_analysis['file_path']).name

        # 如果已经有良好命名，保持不变
        if len(current_name) > 15 and any(c in current_name for c in ['-', '_', '·']):
            return current_name

        # 构建新命名
        parts = []

        # 质量标记
        quality = file_analysis.get("version_info", {})
        if quality.get("is_final"):
            parts.append("终极版")
        elif quality.get("detected_version"):
            parts.append(quality["detected_version"])

        # 主题
        themes = file_analysis.get("detected_themes", [])
        if themes:
            parts.append(themes[0])

        # 实体
        entities = file_analysis.get("detected_entities", [])
        if entities:
            parts.append(entities[0]["name"])

        # 文件类型
        if "Prompt" in file_analysis.get("content_summary", ""):
            parts.append("Prompt模板")
        elif "数据分析" in file_analysis.get("content_summary", ""):
            parts.append("数据分析")

        # 扩展名
        ext = Path(file_analysis['file_path']).suffix

        return "·".join(parts) + ext if parts else current_name

    def _explain_naming_reasoning(self, file_analysis: Dict) -> str:
        """解释命名建议的原因"""
        reasons = []

        current_name = Path(file_analysis['file_path']).name

        if len(current_name) < 15:
            reasons.append("当前命名过于简单，缺乏描述性")

        themes = file_analysis.get("detected_themes", [])
        if themes and not any(t in current_name for t in themes):
            reasons.append(f"建议添加主题标识: {themes[0]}")

        quality = file_analysis.get("version_info", {})
        if quality.get("is_final") and "终极版" not in current_name:
            reasons.append("检测到高质量内容，建议添加质量标记")

        return "; ".join(reasons) if reasons else "基于内容分析优化命名"

    # ═══════════════════════════════════════════════════════════════
    # 第五步：执行决策
    # ═══════════════════════════════════════════════════════════════

    def execute_decision(self, file_path: str, decision: Dict,
                         user_choice: str) -> Dict:
        """执行用户决策"""
        print(f"✅ 执行决策: {file_path} -> {user_choice}")

        result = {
            "file_path": file_path,
            "decision": user_choice,
            "actions": [],
            "new_location": None,
            "new_name": None,
            "relations_established": []
        }

        # 根据决策类型执行不同操作
        if "create" in user_choice:
            # 创建新项目
            result["actions"].append("create_project")
            result["new_location"] = f"07-项目文档/{self._generate_project_name(file_path)}/"

        elif "join" in user_choice or "add" in user_choice:
            # 加入现有项目
            result["actions"].append("add_to_project")
            # 从user_choice中提取项目名
            project_name = user_choice.replace("join_", "").replace("add_", "")
            result["new_location"] = f"07-项目文档/{project_name}/"
            result["relations_established"].append({
                "type": "project_member",
                "target": project_name
            })

        elif "shared" in user_choice or "component" in user_choice:
            # 作为共享组件
            result["actions"].append("create_shared_component")
            result["new_location"] = "05-知识沉淀/共享组件/"

        elif "dispersed" in user_choice or "keep" in user_choice:
            # 分散存储
            result["actions"].append("dispersed_storage")
            # 根据主题分散
            result["new_location"] = self._determine_dispersed_location(file_path)

        # 处理命名优化
        if "accept" in user_choice or "suggestion" in user_choice:
            # 这里需要实际的命名建议
            result["actions"].append("rename_file")

        # 记录决策
        self.decisions.append(ProcessingDecision(
            decision_id=f"d_{len(self.decisions):04d}",
            file_path=file_path,
            decision_type=user_choice,
            target_location=result["new_location"] or "保持原位",
            reasoning=f"用户选择: {user_choice}",
            confidence=0.9,
            requires_confirmation=False
        ))

        return result

    def _generate_project_name(self, file_path: str) -> str:
        """生成项目名称"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d")
        base_name = Path(file_path).stem[:20]
        return f"{timestamp}-{base_name}"

    def _determine_dispersed_location(self, file_path: str) -> str:
        """确定分散存储位置"""
        # 这里应该基于内容分析
        # 简化处理
        return "05-知识沉淀/待分类/"

    # ═══════════════════════════════════════════════════════════════
    # 第六步：生成洞察报告
    # ═══════════════════════════════════════════════════════════════

    def generate_insights(self, all_files_analysis: List[Dict]) -> List[ProjectInsight]:
        """生成项目洞察"""
        print("💡 生成项目洞察...")

        insights = []

        # 1. 发现潜在项目模式
        theme_clusters = self._cluster_by_theme(all_files_analysis)
        for theme, files in theme_clusters.items():
            if len(files) >= 3:
                insights.append(ProjectInsight(
                    insight_type="pattern",
                    description=f"发现'{theme}'主题的潜在项目，包含{len(files)}个相关文件",
                    affected_files=files,
                    recommended_action=f"考虑将这些文件组织为'{theme}'项目",
                    priority="high" if len(files) >= 5 else "normal"
                ))

        # 2. 发现版本链
        version_chains = self._detect_version_chains(all_files_analysis)
        for base_name, versions in version_chains.items():
            if len(versions) >= 2:
                insights.append(ProjectInsight(
                    insight_type="relation",
                    description=f"发现'{base_name}'的版本链，共{len(versions)}个版本",
                    affected_files=[v["file_path"] for v in versions],
                    recommended_action="建立版本关联，考虑合并或保留最新版",
                    priority="normal"
                ))

        # 3. 发现孤立文件
        isolated_files = self._find_isolated_files(all_files_analysis)
        if len(isolated_files) >= 3:
            insights.append(ProjectInsight(
                insight_type="suggestion",
                description=f"发现{len(isolated_files)}个孤立文件，未找到明显关联",
                affected_files=isolated_files,
                recommended_action="检查这些文件是否可以组合成新项目，或需要进一步分析",
                priority="low"
            ))

        self.insights = insights
        return insights

    def _cluster_by_theme(self, all_files: List[Dict]) -> Dict[str, List[str]]:
        """按主题聚类"""
        clusters = {}

        for file_analysis in all_files:
            file_path = file_analysis["file_path"]
            themes = file_analysis.get("detected_themes", [])

            for theme in themes:
                if theme not in clusters:
                    clusters[theme] = []
                clusters[theme].append(file_path)

        return clusters

    def _detect_version_chains(self, all_files: List[Dict]) -> Dict[str, List[Dict]]:
        """检测版本链"""
        from collections import defaultdict

        chains = defaultdict(list)

        for file_analysis in all_files:
            file_path = file_analysis["file_path"]
            file_name = Path(file_path).stem

            # 提取基础名（去掉版本号）
            import re
            base_match = re.match(r'(.+?)[-_]?V?\d', file_name)
            if base_match:
                base_name = base_match.group(1)
                chains[base_name].append({
                    "file_path": file_path,
                    "version": file_analysis.get("version_info", {}).get("detected_version", "unknown")
                })

        return {k: v for k, v in chains.items() if len(v) >= 2}

    def _find_isolated_files(self, all_files: List[Dict]) -> List[str]:
        """找到孤立文件"""
        isolated = []

        for file_analysis in all_files:
            themes = file_analysis.get("detected_themes", [])
            entities = file_analysis.get("detected_entities", [])

            if len(themes) == 0 and len(entities) == 0:
                isolated.append(file_analysis["file_path"])

        return isolated

    # ═══════════════════════════════════════════════════════════════
    # 完整工作流执行
    # ═══════════════════════════════════════════════════════════════

    def process_new_file(self, file_path: str, content: str,
                         existing_projects: List[Dict] = None) -> Dict:
        """处理新文件的完整工作流"""

        print("=" * 60)
        print("🔄 启动项目决策工作流")
        print("=" * 60)

        # 1. 接收文件
        _ = self.receive_new_file(file_path, content)

        # 2. 深度分析
        step2 = self.deep_content_analysis(file_path, content)

        # 3. 项目匹配
        existing_projects = existing_projects or []
        step3 = self.identify_project_match(step2, existing_projects)

        # 4. 生成决策问题
        step4 = self.generate_decision_questions(step2, step3)

        # 5. 等待用户决策（这里返回等待状态）
        result = {
            "workflow_status": "awaiting_decision",
            "file_path": file_path,
            "analysis": step2,
            "match_result": step3,
            "decision_questions": step4,
            "next_step": "等待用户确认决策"
        }

        print("\n" + "=" * 60)
        print("📋 工作流执行完成，等待用户决策")
        print("=" * 60)

        return result

    def generate_comprehensive_report(self) -> Dict:
        """生成完整报告"""
        return {
            "workflow_summary": {
                "total_decisions": len(self.decisions),
                "total_insights": len(self.insights),
                "processing_steps": len(self.processing_log)
            },
            "decisions": [d.to_dict() for d in self.decisions],
            "insights": [i.to_dict() for i in self.insights],
            "processing_log": self.processing_log
        }


# ═══════════════════════════════════════════════════════════════════
# 使用示例
# ═══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    workflow = ProjectDecisionWorkflow(
        base_path=str(Path(__file__).resolve().parent.parent.parent)
    )

    print("=" * 60)
    print("项目决策工作流系统")
    print("=" * 60)
    print()
    print("✅ 系统初始化完成")
    print("📖 使用说明：")
    print("   1. 调用 process_new_file() 处理新文件")
    print("   2. 系统会分析内容并生成决策问题")
    print("   3. 用户确认后调用 execute_decision() 执行")
    print("   4. 调用 generate_insights() 获取项目洞察")
