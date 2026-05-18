# 🧠 MemoryOS 风格记忆系统

> 参考: [BAI-LAB/MemoryOS](https://github.com/BAI-LAB/MemoryOS) (EMNLP 2025 Oral)

## 核心特性

- **三层记忆**: Short-term → Mid-term → Long-term
- **热度驱动**: 基于访问频率和交互长度的动态晋升机制
- **五种记忆类型**: Episodic / Semantic / Procedural / Emotional / Somatic
- **混合检索**: Vector + Graph 并行查询
- **自动进化**: 反馈闭环机制

## 目录结构

```
memory/
├── memoryos.py          ← 核心引擎
├── config.yaml          ← MemoryOS 风格配置
├── short_term/          ← 短期记忆 (FIFO淘汰)
│   └── YYYY-MM-DD.jsonl
├── mid_term/            ← 中期记忆 (热度晋升)
│   ├── episodic.json
│   ├── semantic.json
│   └── ...
├── long_term/           ← 长期记忆 (持久化)
│   ├── user_profile/
│   ├── knowledge/
│   └── strategies/
└── chromadb/            ← 向量存储 (可选)
```

## 核心参数 (MemoryOS 标准)

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `short_term_capacity` | 7 | 短期记忆容量 |
| `mid_term_capacity` | 1000 | 中期记忆容量 |
| `mid_term_heat_threshold` | 5.0 | 热度阈值 |
| `similarity_threshold` | 0.7 | 相似度阈值 |

## 使用方法

### 1. 初始化

```python
from memory.memoryos import MemoryOS, MemoryConfig

memory = MemoryOS(
    storage_path='.',  # 记忆数据存储在当前目录
    config=MemoryConfig(
        short_term_capacity=7,
        mid_term_heat_threshold=5.0
    )
)
```

### 2. 添加记忆

```python
# 情景记忆 (发生了什么)
memory.add_memory(
    content="完成数据库管理Layer分层设计",
    memory_type='episodic',
    metadata={'project': '数据库管理'}
)

# 语义记忆 (知道什么)
memory.add_memory(
    content="三层架构 = raw + processed + knowledge",
    memory_type='semantic',
    metadata={'concept': 'architecture'}
)

# 程序记忆 (怎么做)
memory.add_memory(
    content="做事顺序 = 先求有 + 再求丰富 + 提炼精华",
    memory_type='procedural',
    metadata={'pattern': 'workflow'}
)

# 情感记忆 (偏好什么)
memory.add_memory(
    content="用户偏好简洁直接的回复",
    memory_type='emotional',
    metadata={'preference': 'concise'}
)
```

### 3. 检索记忆

```python
results = memory.retrieve(
    query="架构设计",
    memory_types=['semantic', 'procedural']
)

# 返回:
# - short_term: 短期记忆
# - mid_term: 中期记忆
# - long_term: 长期记忆
# - context: 用户画像/知识/策略
```

### 4. 获取状态

```python
summary = memory.get_memory_summary()
# {
#   "short_term_count": 7,
#   "mid_term_count": 45,
#   "long_term_knowledge": 23,
#   "user_profile": {...}
# }
```

## 记忆流转机制

```
┌─────────────────────────────────────────────────────────────────┐
│                    记忆生命周期                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  【输入】                                                         │
│  raw/ 执行记录 → episodic/ 情景记忆                               │
│       ↓ extract                                                  │
│  semantic/ 语义记忆 (提炼为概念)                                 │
│       ↓ compress                                                 │
│  procedural/ 程序记忆 (提炼为模式)                                │
│                                                                  │
│  【热度晋升】                                                     │
│  Short-term (7条) → Mid-term (热度≥5.0) → Long-term            │
│                                                                  │
│  【检索】                                                         │
│  Hybrid Retriever ← 同时查询三层记忆                             │
│     ├─ 短期: 最近交互                                            │
│     ├─ 中期: 热度高的整合片段                                    │
│     └─ 长期: 用户画像/知识/策略                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 与知识图谱集成

```python
# 混合检索 (Vector + Graph)
class HybridRetriever:
    def retrieve(self, query):
        # 1. 向量检索 (semantic search)
        vector_results = vector_db.query(query)

        # 2. 图谱检索 (relationship search)
        graph_results = graph_db.query(query)

        # 3. 混合排序
        return self.merge_and_rank(vector_results, graph_results)
```

## 评估指标

| 指标 | 说明 |
|------|------|
| Context Precision | 上下文精确度 |
| Context Recall | 上下文召回率 |
| Faithfulness | 忠实度 (不幻觉) |
| Answer Relevancy | 答案相关性 |

## 参考资料

- [MemoryOS 论文](https://arxiv.org/abs/2506.06326)
- [MemoryOS GitHub](https://github.com/BAI-LAB/MemoryOS)
- [MemoryOS 文档](https://bai-lab.github.io/MemoryOS/docs)
