#!/usr/bin/env python3
"""
开箱即用自举引导模块
clone 后首次运行 app.py 时自动创建演示数据 + 构建搜索索引
"""

from pathlib import Path
import os as _os

WORKSPACE = Path(__file__).resolve().parent.parent.parent

# ============================================================
# 演示数据模板（嵌入在代码中，无需外部文件）
# ============================================================

DEMO_FILES = {
    # ---- 文件1: 会议纪要 ----
    "2026-05-22-项目周会纪要.md": """\
# 2026-05-22 项目周会纪要

## 会议信息
- **时间**: 2026年5月22日 14:00-15:30
- **地点**: 线上腾讯会议
- **主持人**: 李明
- **参会人**: 王芳、张伟、陈静、赵云

## 议程

### 1. 上周工作回顾
- 知识库框架V2.0 核心功能开发完成
- 测试覆盖率达到50%
- 文档更新至V2.0

### 2. 本周计划
- 补充Wiki知识库条目（目标：10条）
- 完成收件箱演示数据准备
- 端到端管道验证

### 3. 技术讨论
- 讨论了向量搜索的性能优化方案
- 确认使用 FAISS HNSW 作为默认索引算法
- 张伟提出增加批量导入功能，暂定V2.1实现

### 4. 待办事项
- [ ] 李明: 完成集成测试报告
- [ ] 王芳: 准备3个业务场景演示案例
- [ ] 陈静: 优化搜索响应时间至500ms内
- [ ] 赵云: 编写用户操作手册

### 下一步
下次会议时间：2026年5月29日 14:00
""",

    # ---- 文件2: 概念定义 ----
    "概念-嵌入向量.md": """\
# 嵌入向量

嵌入向量（Embedding）是将自然语言文本转化为固定维度的实数向量的技术。通过预训练的深度学习模型（如 sentence-transformers），语义相近的文本会被映射到向量空间中相近的位置。

在知识库系统中，嵌入向量是连接原始文本和语义搜索能力的关键桥梁：
1. 文本输入 → 预训练模型编码 → 高维向量
2. 相似度计算 → 余弦相似度 / 欧氏距离
3. 向量索引 → FAISS 构建 ANN 索引
4. 查询时同样生成查询向量 → 在索引中搜索相似文档

常见嵌入模型对比：
- all-MiniLM-L6-v2: 384维，速度快，适合中文混合场景
- text2vec-large-chinese: 1024维，中文最优
- multilingual-e5-large: 1024维，多语言支持好

当前系统使用 all-MiniLM-L6-v2 作为默认模型，通过 `vector_search.py` 统一管理嵌入和索引。
""",

    # ---- 文件3: 实体文档 ----
    "实体-NamingOptimizer.md": """\
# NamingOptimizer

## 概述
NamingOptimizer（命名优化器）是知识库自动整理管道的核心组件之一，负责为待入库文件生成符合系统命名规范的优化文件名。

## 技术规格
- **位置**: `.workbuddy/scripts/naming_optimizer.py`
- **输入**: 文件路径 + `content_analysis` 字典
- **输出**: `NamingSuggestion` dataclass
- **命名格式**: `质量标记·核心主题·内容类型`

## 角色定位
NamingOptimizer 在 `auto_organizer.py` 的处理流程中处于第2步（内容分析 → 命名优化 → 目录路由），其输出直接影响文件的最终存放位置和可检索性。

## 命名规则
1. 最多3个部分，用中点 `·` 分隔
2. 总长度不超过80字符
3. 质量标记从预设词库中选取（如"终极版"=5,"已验证"=5,"草稿"=1）
4. 内容类型从预设词库中选取（如"会议纪要""分析报告""技术文档"）

## 与其他组件的关系
- **被调用**: `auto_organizer.py` 在 `analyze_file()` 中调用
- **依赖**: `content_analyzer.py` 的 `ContentInsight` 结果作为输入
- **输出**: 生成的 `NamingSuggestion` 被 `auto_organizer.py` 的 `execute_plan()` 用于实际文件重命名

## 质量标记体系
| 标记 | 分值 | 适用场景 |
|------|------|----------|
| 终极版 | 5 | 经过多次修订的最终版本 |
| 已验证 | 5 | 经过审核确认准确的内容 |
| 正式版 | 4 | 已定稿发布 |
| 初稿 | 2 | 首次编写的原始版本 |
| 草稿 | 1 | 未完成的临时版本 |
| 占位 | 0 | 占位文件 |
""",

    # ---- 文件4: 代码示例 ----
    "批量导入处理器设计.md": '''\
# 批量文件导入处理器

## 功能描述
自动扫描指定目录，批量导入文件到知识库系统。支持 .md/.txt/.json/.docx 格式，自动分类路由。

## 使用场景
- 迁移旧知识库数据
- 批量导入会议记录
- 从其他系统导出后导入

## 核心架构

```python
import os
from pathlib import Path
from .auto_organizer import AutoOrganizer
from .content_analyzer import ContentAnalyzer

class BatchImporter:
    """批量文件导入器"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.organizer = AutoOrganizer()
        self.analyzer = ContentAnalyzer()
        self.stats = {"total": 0, "success": 0, "skipped": 0, "failed": 0}
    
    def import_directory(self, source_dir: str) -> dict:
        """导入整个目录的文件"""
        files = list(Path(source_dir).glob("*"))
        self.stats["total"] = len(files)
        
        for file_path in files:
            if not file_path.is_file():
                continue
            try:
                result = self.organizer.process_and_store(
                    str(file_path), dry_run=False
                )
                if result.get("status") == "success":
                    self.stats["success"] += 1
                else:
                    self.stats["skipped"] += 1
            except Exception as e:
                self.stats["failed"] += 1
                print(f"导入失败: {file_path} - {e}")
        
        return self.stats
```

## 依赖
- auto_organizer.py: 文件处理和路由
- content_analyzer.py: 内容分析
- Python >= 3.8

## 配置
通过 `.workbuddy/config/batch_import.json` 配置过滤规则和默认标签。

## 注意事项
- 大文件（>10MB）建议分批处理
- .docx 文件需要 python-docx 依赖
- 导入前建议先做 dry-run 预览
''',

    # ---- 文件5: 项目规划 ----
    "V2.1产品规划.md": """\
# V2.1 产品规划

## 版本目标
在V2.0稳定基础上，引入AI辅助分类和团队协作能力。

## 核心功能

### 1. AI智能分类
- 基于大语言模型自动识别文档类型
- 多标签分类支持（一篇文档可同时属于多个类别）
- 分类置信度评分和人工复核机制

### 2. 团队协作
- 多人共享知识库
- 评论和标注功能
- 变更历史和版本对比

### 3. 性能优化
- 搜索响应时间 < 200ms（当前目标500ms）
- 支持10万级文档索引
- 增量索引更新（避免全量重建）

### 4. 集成扩展
- REST API 完善
- Webhook 通知
- 第三方工具集成（飞书/企业微信/钉钉）

## 技术选型
| 模块 | 技术 | 原因 |
|------|------|------|
| AI分类 | GPT-4o-mini / 本地模型 | 成本与效果平衡 |
| 实时协作 | WebSocket + CRDT | 低延迟冲突解决 |
| 全文搜索 | SQLite FTS5 | 零依赖，嵌入部署 |
| 通知 | Webhook + SSE | 标准协议，广泛支持 |

## 时间线
- 2026年6月: AI分类原型
- 2026年7月: 团队协作MVP
- 2026年8月: 性能优化和集成测试
- 2026年9月: V2.1正式发布
""",
}


# ============================================================
# 自举引导逻辑
# ============================================================

def ensure_demo_data(force: bool = False) -> int:
    """确保 01-收件箱/ 中有演示数据，返回创建的文件数"""
    inbox = WORKSPACE / "01-收件箱"
    inbox.mkdir(parents=True, exist_ok=True)

    # 检查是否已有足够数据
    existing = [f for f in inbox.glob("*.md") if f.name != "README.md"]
    if len(existing) >= 3 and not force:
        return 0

    created = 0
    for filename, content in DEMO_FILES.items():
        target = inbox / filename
        if not target.exists() or force:
            target.write_text(content, encoding="utf-8")
            created += 1

    return created


def ensure_search_index(force: bool = False) -> dict:
    """确保搜索索引存在，返回索引统计"""
    index_db = WORKSPACE / ".workbuddy" / "index" / "search_index.db"

    # FAISS 路径：非 ASCII 路径下 C fopen 无法处理，回退到 TEMP
    _faiss_path = WORKSPACE / ".workbuddy" / "index" / "vectors.faiss"
    if str(_faiss_path).isascii():
        faiss_file = _faiss_path
    else:
        faiss_file = Path(_os.environ.get("TEMP", _os.environ.get("TMPDIR", "/tmp"))) / "km_vectors.faiss"

    # 检查索引是否有效
    has_db = index_db.exists()
    has_faiss = faiss_file.exists()

    if has_db and has_faiss and not force:
        import sqlite3
        conn = sqlite3.connect(str(index_db))
        count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        conn.close()
        if count >= 3:
            return {"documents": count, "faiss": has_faiss, "rebuilt": False}

    # 需要重建
    import sys
    _scripts = str(Path(__file__).resolve().parent)
    if _scripts not in sys.path:
        sys.path.insert(0, _scripts)

    from vector_search import rebuild_index, build_faiss_index, HAS_VECTOR

    doc_count = rebuild_index()

    vec_count = 0
    if HAS_VECTOR:
        vec_count = build_faiss_index()

    return {"documents": doc_count, "faiss": vec_count > 0, "rebuilt": True}


def bootstrap(force: bool = False) -> dict:
    """
    主入口: 执行开箱即用引导流程
    返回: {"demo_files": int, "index": dict}
    """
    result = {}

    # Step 1: 演示数据
    demo_count = ensure_demo_data(force=force)
    result["demo_files"] = demo_count

    # Step 2: 搜索索引
    index_result = ensure_search_index(force=force)
    result["index"] = index_result

    return result


def print_bootstrap_report(result: dict) -> None:
    """打印引导报告"""
    print()
    print("=" * 50)
    print("  开箱即用引导报告")
    print("=" * 50)

    demo = result["demo_files"]
    if demo > 0:
        print(f"  演示数据: 已创建 {demo} 个文件")
    else:
        print(f"  演示数据: 已就绪（跳过）")

    idx = result["index"]
    if idx.get("rebuilt"):
        print(f"  文档索引: {idx['documents']} 条 (SQLite)")
        print(f"  向量索引: {'已构建' if idx['faiss'] else '不可用（缺少依赖）'}")
    else:
        print(f"  搜索索引: {idx['documents']} 条文档, 已就绪（跳过）")

    print("=" * 50)
    print()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="开箱即用引导工具")
    parser.add_argument("--force", action="store_true", help="强制重建")
    args = parser.parse_args()

    print("[自举引导] 开始...")
    result = bootstrap(force=args.force)
    print_bootstrap_report(result)
    print("[自举引导] 完成 — 现在可以启动 python app.py 进行搜索")
