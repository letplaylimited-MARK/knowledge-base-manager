---
title: MemoryOS 记忆引擎
type: entity
aliases: [MemoryOS, 记忆引擎, 记忆操作系统]
category: 系统组件
tags: [MemoryOS, 记忆管理, 核心引擎, STM, MTM, LTM]
confidence: high
created: 2026-05-23
updated: 2026-05-23
---

# MemoryOS 记忆引擎

## 概述

MemoryOS 是本系统的核心记忆管理引擎，负责知识的持久化存储、检索和维护。它是"三体体系"中记忆层的实现，管理短期/中期/长期三级记忆架构。

## 技术属性

| 属性 | 值 |
|------|-----|
| 实现文件 | `.workbuddy/记忆层/memoryos.py` |
| 核心类 | `MemoryOS` |
| 存储后端 | SQLite (结构化) + FAISS (向量) |
| 数据目录 | `.workbuddy/memory_data/` |
| 依赖 | numpy, sqlite3, faiss-cpu |

## 核心能力

1. **三级存储管理**: STM队列、MTM数据库表、LTM向量索引的统一抽象
2. **记忆检索**: 支持关键词搜索 (`search_memory`) 和语义搜索
3. **记忆巩固**: 定期将高价值MTM记忆升级到LTM
4. **自动维护**: 过期记忆清理、索引优化、碎片整理
5. **相似度计算**: 词级Jaccard相似度用于去重和聚类

## 暴露的MCP工具

通过 `mcp_server.py` 暴露：
- `search_memory` — 跨层级记忆搜索
- `run_maintenance` — 触发记忆维护任务

## 关键方法

```python
class MemoryOS:
    def store(self, content: str, metadata: dict) -> str
    def search(self, query: str, tier: str = "all") -> list
    def consolidate(self) -> int  # 巩固MTM→LTM
    def maintain(self) -> dict    # 维护清理
    def get_stats(self) -> dict   # 获取统计信息
```

## 与其他组件的关系

- **被依赖**: agent_orchestrator.py 通过 MemoryOS 记录 Agent 决策
- **依赖**: vector_search.py 提供向量索引能力
- **协同**: smart_router.py 将记忆检索集成到混合检索流程

## 参考来源

- [[记忆层级]] — 三级记忆架构的详细解释
- 系统实现: `.workbuddy/记忆层/memoryos.py`

---
*此实体记录了系统的核心记忆管理组件*
