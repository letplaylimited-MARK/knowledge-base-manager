#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动整理引擎 - 深度理解内容 + 智能优化命名 + 自动分类
"""

import os
from path_setup import setup_scripts_only; setup_scripts_only()

from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime

from content_analyzer import ContentAnalyzer, ContentInsight
from naming_optimizer import NamingOptimizer, NamingSuggestion

@dataclass
class OrganizationPlan:
    """整理计划"""
    file_path: Path
    content_insight: ContentInsight
    naming_suggestion: NamingSuggestion
    target_directory: str
    target_name: str
    should_rename: bool
    should_move: bool
    confidence: float
    reasoning: str

class AutoOrganizer:
    """自动整理引擎"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.content_analyzer = ContentAnalyzer()
        self.naming_optimizer = NamingOptimizer()

        # 目录路由规则
        self.directory_routes = {
            'AI技能代码': '03-资产库/AI技能/',
            '提示词': '03-资产库/提示词/',
            '模板': '03-资产库/模板/',
            '会议纪要': '02-对话记录/',
            '分析报告': '04-输出成果/报告/',
            '概念定义': '05-知识沉淀/wiki/concepts/',
            '实体定义': '05-知识沉淀/wiki/entities/',
            '来源摘要': '05-知识沉淀/wiki/sources/',
            '比较分析': '05-知识沉淀/wiki/comparisons/',
        }

    def analyze_file(self, file_path: Path) -> OrganizationPlan:
        """
        分析单个文件，生成整理计划

        Args:
            file_path: 文件路径

        Returns:
            OrganizationPlan: 整理计划
        """
        print(f"\n📄 分析文件: {file_path.name}")

        # 1. 深度内容分析
        content_insight = self.content_analyzer.analyze_file(file_path)
        print(f"   核心主题: {content_insight.core_topic}")
        print(f"   内容类型: {content_insight.content_type}")
        print(f"   质量等级: {content_insight.quality_level}")

        # 2. 命名优化建议
        analysis_dict = {
            'core_topic': content_insight.core_topic,
            'content_type': content_insight.content_type,
            'quality_level': content_insight.quality_level,
            'key_entities': content_insight.key_entities,
            'confidence': content_insight.confidence
        }
        naming_suggestion = self.naming_optimizer.analyze_and_suggest(
            file_path, analysis_dict
        )

        # 3. 确定目标目录
        target_dir = self._determine_target_directory(content_insight)

        # 4. 决策：是否重命名、是否移动
        should_rename = self.naming_optimizer.should_rename(naming_suggestion)
        should_move = self._should_move(file_path, target_dir)

        # 5. 确定最终目标名称
        if should_rename:
            target_name = naming_suggestion.suggested_name
        else:
            target_name = file_path.name

        # 6. 计算整体置信度
        confidence = (content_insight.confidence + naming_suggestion.confidence) / 2

        # 7. 生成理由
        reasoning = self._generate_reasoning(
            file_path, content_insight, naming_suggestion,
            should_rename, should_move, target_dir
        )

        return OrganizationPlan(
            file_path=file_path,
            content_insight=content_insight,
            naming_suggestion=naming_suggestion,
            target_directory=target_dir,
            target_name=target_name,
            should_rename=should_rename,
            should_move=should_move,
            confidence=confidence,
            reasoning=reasoning
        )

    def _determine_target_directory(self, insight: ContentInsight) -> str:
        """确定目标目录"""
        content_type = insight.content_type

        # 直接匹配
        if content_type in self.directory_routes:
            return self.directory_routes[content_type]

        # 模糊匹配
        for type_key, directory in self.directory_routes.items():
            if type_key in content_type or content_type in type_key:
                return directory

        # 基于核心主题推断
        topic = insight.core_topic
        if '知识' in topic or '概念' in topic:
            return '05-知识沉淀/wiki/concepts/'
        elif '数据' in topic or '分析' in topic:
            return '04-输出成果/报告/'
        elif 'AI' in topic or '模型' in topic:
            return '03-资产库/AI技能/'

        # 默认
        return '01-收件箱/'

    def _should_move(self, file_path: Path, target_dir: str) -> bool:
        """判断是否需要移动"""
        current_dir = os.path.relpath(str(file_path.parent), str(self.base_path))

        # 已经在正确位置
        if target_dir in current_dir or current_dir in target_dir:
            return False

        # 在收件箱，需要移动
        if '01-收件箱' in str(file_path):
            return True

        # 其他情况，建议移动
        return True

    def _generate_reasoning(self, file_path: Path, insight: ContentInsight,
                           naming: NamingSuggestion, should_rename: bool,
                           should_move: bool, target_dir: str) -> str:
        """生成决策理由"""
        reasons = []

        # 内容分析
        reasons.append(f"内容识别为「{insight.content_type}」，核心主题「{insight.core_topic}」")

        # 重命名理由
        if should_rename:
            reasons.append(f"建议重命名：{naming.reason}")
        else:
            reasons.append("命名已较好，建议保持")

        # 移动理由
        if should_move:
            reasons.append(f"建议移动至「{target_dir}」")
        else:
            reasons.append("已在合适位置")

        return "；".join(reasons)

    def generate_plan_report(self, plan: OrganizationPlan) -> str:
        """生成整理计划报告"""
        report = []
        report.append("# 文件整理计划")
        report.append("")
        report.append(f"**原文件**: `{plan.file_path}`")
        report.append(f"**分析置信度**: {plan.confidence:.0%}")
        report.append("")

        # 内容洞察
        report.append("## 内容洞察")
        report.append(f"- **核心主题**: {plan.content_insight.core_topic}")
        report.append(f"- **内容类型**: {plan.content_insight.content_type}")
        report.append(f"- **质量等级**: {plan.content_insight.quality_level}")

        if plan.content_insight.key_entities:
            report.append(f"- **关键实体**: {', '.join([e['name'] for e in plan.content_insight.key_entities[:3]])}")

        if plan.content_insight.concepts:
            report.append(f"- **核心概念**: {', '.join(plan.content_insight.concepts[:5])}")

        report.append("")

        # 整理建议
        report.append("## 整理建议")

        if plan.should_rename:
            report.append(f"✅ **重命名**: `{plan.file_path.name}` → `{plan.target_name}`")
            report.append(f"   理由: {plan.naming_suggestion.reason}")
        else:
            report.append(f"⏭️ **命名**: 保持 `{plan.file_path.name}`")

        if plan.should_move:
            report.append(f"✅ **移动**: → `{plan.target_directory}`")
        else:
            report.append(f"⏭️ **位置**: 已在 `{plan.target_directory}`")

        report.append("")
        report.append(f"**综合理由**: {plan.reasoning}")

        # 备选
        if plan.naming_suggestion.alternatives:
            report.append("")
            report.append("## 备选命名")
            for i, alt in enumerate(plan.naming_suggestion.alternatives, 1):
                report.append(f"{i}. `{alt}`")

        # 执行建议
        report.append("")
        report.append("## 执行建议")
        if plan.confidence >= 0.8:
            report.append("✅ **高置信度**，建议自动执行")
        elif plan.confidence >= 0.6:
            report.append("⚠️ **中等置信度**，建议确认后执行")
        else:
            report.append("❓ **低置信度**，建议人工审核")

        return '\n'.join(report)

    def execute_plan(self, plan: OrganizationPlan, dry_run: bool = True) -> bool:
        """
        执行整理计划

        Args:
            plan: 整理计划
            dry_run: 是否仅模拟，不实际执行

        Returns:
            bool: 是否成功
        """
        print(f"\n{'='*60}")
        print("执行整理计划")
        print(f"{'='*60}")

        if dry_run:
            print("[模拟模式] 不实际执行文件操作")

        success = True

        # 1. 移动文件
        if plan.should_move:
            target_path = self.base_path / plan.target_directory / plan.target_name
            print("\n移动:")
            print(f"  从: {plan.file_path}")
            print(f"  到: {target_path}")

            if not dry_run:
                try:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    # 实际移动逻辑（这里用复制代替）
                    import shutil
                    shutil.move(str(plan.file_path), str(target_path))
                    print("  ✅ 完成")
                except Exception as e:
                    print(f"  ❌ 失败: {e}")
                    success = False

        # 2. 重命名（如果在原位置）
        elif plan.should_rename:
            new_path = plan.file_path.parent / plan.target_name
            print("\n重命名:")
            print(f"  从: {plan.file_path.name}")
            print(f"  到: {plan.target_name}")

            if not dry_run:
                try:
                    plan.file_path.rename(new_path)
                    print("  ✅ 完成")
                except Exception as e:
                    print(f"  ❌ 失败: {e}")
                    success = False

        else:
            print("\n无需操作，文件已在合适位置")

        return success

    def post_process(self, plan: OrganizationPlan) -> Dict:
        """处理后操作：索引 + 记忆"""
        from memoryos import MemoryOS
        from vector_search import index_file

        target = self.base_path / plan.target_directory / plan.target_name

        # 1. 向量索引
        indexed = index_file(target)

        # 2. 记忆记录
        try:
            mem = MemoryOS(str(self.base_path / ".workbuddy" / "记忆层" / "memory_data"))
            mem.add_memory(
                content=f"[{datetime.now().strftime('%H:%M')}] 处理: {target.name} -> {plan.target_directory} [{plan.content_insight.content_type}]",
                memory_type="episodic",
                metadata={"file": str(target), "type": plan.content_insight.content_type}
            )
        except Exception as e:
            print(f"  [memory] skipped: {e}")

        return {"indexed": indexed, "memory_recorded": True}

    def process_and_store(self, file_path: Path, dry_run: bool = False) -> Dict:
        """完整流水线：分析 -> 路由 -> 移动 -> 索引 -> 记忆"""
        plan = self.analyze_file(file_path)
        success = self.execute_plan(plan, dry_run=dry_run)

        if success and not dry_run:
            post = self.post_process(plan)
            return {"plan": plan, "executed": True, **post}

        return {"plan": plan, "executed": False}

    def scan_and_organize(self, directory: Path, dry_run: bool = True) -> List[OrganizationPlan]:
        """
        扫描目录并生成整理计划

        Args:
            directory: 要扫描的目录
            dry_run: 是否仅模拟

        Returns:
            List[OrganizationPlan]: 整理计划列表
        """
        print(f"\n🔍 扫描目录: {directory}")

        plans = []
        supported_extensions = {'.txt', '.md', '.docx', '.json'}

        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix in supported_extensions:
                # 跳过隐藏文件
                if file_path.name.startswith('.'):
                    continue

                plan = self.analyze_file(file_path)
                plans.append(plan)

                # 打印简要信息
                action = []
                if plan.should_rename:
                    action.append("重命名")
                if plan.should_move:
                    action.append("移动")

                action_str = "+".join(action) if action else "保持"
                print(f"   [{action_str}] {file_path.name} ({plan.confidence:.0%})")

        print(f"\n共分析 {len(plans)} 个文件")
        return plans


def main():
    """主函数"""
    base_path = str(Path(__file__).resolve().parent.parent.parent)
    organizer = AutoOrganizer(base_path)

    # 扫描收件箱
    inbox_path = Path(base_path) / "01-收件箱"

    if not inbox_path.exists():
        print(f"收件箱不存在: {inbox_path}")
        return

    # 生成整理计划
    plans = organizer.scan_and_organize(inbox_path, dry_run=True)

    if not plans:
        print("没有发现需要整理的文件")
        return

    # 生成完整报告
    print(f"\n{'='*60}")
    print("生成详细报告...")
    print(f"{'='*60}")

    for i, plan in enumerate(plans, 1):
        report = organizer.generate_plan_report(plan)

        # 保存报告
        report_path = Path(base_path) / ".workbuddy" / "reports" / f"organize_plan_{i}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"报告已保存: {report_path}")

    # 汇总
    print(f"\n{'='*60}")
    print("整理计划汇总")
    print(f"{'='*60}")

    rename_count = sum(1 for p in plans if p.should_rename)
    move_count = sum(1 for p in plans if p.should_move)
    high_confidence = sum(1 for p in plans if p.confidence >= 0.8)

    print(f"总文件数: {len(plans)}")
    print(f"建议重命名: {rename_count}")
    print(f"建议移动: {move_count}")
    print(f"高置信度(≥80%): {high_confidence}")


if __name__ == "__main__":
    main()
