# 知识图谱索引

> 版本: V2.0 | 更新: 2026-05-23

## 知识图谱结构

| 组件 | 路径 | 条目数 | 功能 |
|------|------|--------|------|
| 概念 | concepts/ | 4 | 核心概念定义 |
| 实体 | entities/ | 3 | 系统组件实体 |
| 源摘要 | sources/ | 1 | 原始知识摘要 |
| 比较 | comparisons/ | 1 | 对比分析 |

## 概念 (concepts/)

- [向量语义搜索](concepts/向量语义搜索.md) — 基于深度嵌入的语义检索技术
- [混合检索](concepts/混合检索.md) — 关键词+语义的融合检索策略
- [记忆层级](concepts/记忆层级.md) — STM/MTM/LTM 三级记忆架构
- [知识图谱](concepts/知识图谱.md) — 图结构知识组织方法

## 实体 (entities/)

- [MemoryOS 记忆引擎](entities/MemoryOS记忆引擎.md) — 核心记忆管理组件
- [MCP Server](entities/MCP-Server.md) — 20工具的协议服务入口
- [AI模型适配器](entities/AI模型适配器.md) — 多AI模型统一调用接口

## 源摘要 (sources/)

- [示例知识来源](sources/示例知识来源.md)

## 比较 (comparisons/)

- [示例比较分析](comparisons/示例比较分析.md)

## 使用指南

1. 在 `concepts/` 目录创建新概念（使用一致的 frontmatter 格式）
2. 在 `entities/` 目录创建新实体
3. 使用 `sources/` 记录知识来源
4. 使用 `comparisons/` 进行对比分析
5. 使用 `[[条目名]]` 建立跨条目引用
6. 运行 `update_index.py` 更新 SQLite + FAISS 索引

---
*本索引由系统管理，添加新知识后运行 update_index.py 同步*
