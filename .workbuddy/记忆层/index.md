# MemoryOS 风格记忆系统索引

## 快速导航

| 文件 | 说明 |
|------|------|
| [memoryos.py](memoryos.py) | 核心引擎 (三层记忆 + 五种类型) |
| [config.yaml](config.yaml) | MemoryOS 标准配置 |
| [README.md](README.md) | 完整使用文档 |

## 核心组件

### 三层记忆

| 层 | 类 | 容量 | 淘汰规则 |
|----|-----|------|----------|
| 短期 | `ShortTermMemory` | 7条 | FIFO |
| 中期 | `MidTermMemory` | 1000条 | 热度淘汰 |
| 长期 | `LongTermMemory` | 100条 | 持久化 |

### 五种记忆类型

| 类型 | 说明 | 存储位置 |
|------|------|----------|
| episodic | 情景记忆 | short_term/ |
| semantic | 语义记忆 | mid_term/ + long_term/knowledge/ |
| procedural | 程序记忆 | mid_term/ + long_term/strategies/ |
| emotional | 情感记忆 | long_term/user_profile/ |
| somatic | 躯体记忆 | 实时监控 |

## 配置参数

```yaml
capacity:
  short_term: 7
  mid_term: 1000
  long_term_knowledge: 100

heat:
  mid_term_threshold: 5.0
  similarity_threshold: 0.7
  decay_factor: 0.95
```

## 与现有架构集成

```
数据库管理/
├── raw/                    ← 原始资料
├── processed/              ← 处理后
├── knowledge/             ← Layer 2: 知识库
├── 向量数据库/            ← Layer 3: ChromaDB
├── AIP接口/               ← Layer 4: API
└── memory/                ← NEW: MemoryOS 记忆系统
    ├── memoryos.py        ← 核心引擎
    ├── short_term/        ← 短期记忆
    ├── mid_term/          ← 中期记忆
    └── long_term/         ← 长期记忆
```

## 状态

- [x] 核心引擎 (memoryos.py)
- [x] 配置文件 (config.yaml)
- [x] 使用文档 (README.md)
- [x] 三层记忆实现
- [x] 五种记忆类型支持
- [ ] ChromaDB 集成
- [ ] 混合检索引擎
- [ ] 评估模块
