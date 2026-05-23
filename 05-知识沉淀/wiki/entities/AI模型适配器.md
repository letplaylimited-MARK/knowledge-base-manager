---
title: AI模型适配器
type: entity
aliases: [Model Adapter, AI适配器, 多模型支持]
category: 系统组件
tags: [AI模型, OpenAI, Claude, GLM-4, Yi-Light, 适配器模式]
confidence: high
created: 2026-05-23
updated: 2026-05-23
---

# AI模型适配器

## 概述

AI模型适配器（Model Adapter）是本系统AI协作层的核心组件。它通过统一的适配器接口，封装对不同AI模型提供商的调用差异，使上层业务逻辑可以无缝切换底层模型，支持 OpenAI GPT-4、Anthropic Claude 3、智谱GLM-4 和零一Yi-Light 四种模型。

## 技术属性

| 属性 | 值 |
|------|-----|
| 实现文件 | `.workbuddy/scripts/model_adapter.py` |
| 设计模式 | 适配器模式 (Adapter Pattern) |
| 支持模型 | GPT-4, Claude 3, GLM-4, Yi-Light |
| 认证方式 | API Key (各厂商独立) |

## 适配的模型

### OpenAI GPT-4
- **提供商**: OpenAI
- **API**: `https://api.openai.com/v1/chat/completions`
- **优势**: 综合能力强，生态完善
- **配置**: `OPENAI_API_KEY` 环境变量

### Anthropic Claude 3
- **提供商**: Anthropic
- **API**: `https://api.anthropic.com/v1/messages`
- **优势**: 长上下文理解，安全对齐
- **配置**: `ANTHROPIC_API_KEY` 环境变量

### 智谱 GLM-4
- **提供商**: 智谱AI (ZhipuAI)
- **API**: `https://open.bigmodel.cn/api/paas/v4/chat/completions`
- **优势**: 中文优化，国产合规
- **配置**: `ZHIPU_API_KEY` 环境变量

### 零一 Yi-Light
- **提供商**: 零一万物 (01.AI)
- **API**: `https://api.lingyiwanwu.com/v1/chat/completions`
- **优势**: 高性价比，快速响应
- **配置**: `YI_API_KEY` 环境变量

## 适配器接口

```python
class ModelAdapter:
    def chat(self, messages: list, model: str = None) -> str
    def stream_chat(self, messages: list, model: str = None) -> Generator
    def get_available_models(self) -> list
    def set_default_model(self, model: str) -> None
```

## 使用示例

```python
from .workbuddy.scripts.model_adapter import ModelAdapter

adapter = ModelAdapter()
response = adapter.chat([
    {"role": "system", "content": "你是知识管理助手"},
    {"role": "user", "content": "总结今天的知识条目"}
], model="gpt-4")
```

## 配置指南

详见 `docs/AI模型配置指南.md`：
- API Key获取方式
- 模型参数调优
- 故障排除

## 与其他组件的关系

- **被依赖**: `agent_orchestrator.py` 通过适配器调用AI进行决策
- **依赖**: 各大模型厂商的API
- **配置**: 通过 `config/` 和环境变量管理认证信息

## 参考来源

- 系统实现: `.workbuddy/scripts/model_adapter.py`
- 配置文档: `docs/AI模型配置指南.md`

---
*此实体记录了系统的多AI模型接入层*
