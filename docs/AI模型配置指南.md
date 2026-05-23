# AI模型配置指南

> **版本**: V1.0  
> **更新时间**: 2026-05-17

本指南说明如何在通用知识库框架中配置和使用各种AI大模型，实现真正的多模型支持。

## 📋 配置目录结构

所有AI模型配置文件存放在：
`.workbuddy\AI协作体系\模型配置\`

目录结构：
```
模型配置/
├── 模型配置说明.md          # 本说明文件
├── openai-gpt4.yaml         # OpenAI GPT-4配置示例
├── anthropic-claude3.yaml   # Anthropic Claude 3配置示例
├── zhipu-glm4.yaml          # 智谱AI GLM-4配置示例
├── yi-light.yaml            # 零一万物Yi-Light配置示例
└── ...                      # 可根据需求添加更多模型配置
```

## 🔧 配置文件格式

每个模型配置文件应为YAML格式，包含以下字段：

```yaml
# 模型基本信息
model_name: "模型显示名称"
provider: "提供商名称"  # openai, anthropic, google, meta, deepseek, zhipu, baichuan, yi, ollama, custom
model_version: "具体模型版本"  # 如: gpt-4-turbo-preview

# API连接配置
api_key: "您的API密钥"  # 建议使用环境变量或安全 vault
api_base: "API基础URL"  # 如: https://api.openai.com/v1
api_version: "API版本"  # 如: v1 (可选)

# 模型参数
temperature: 0.7          # 采样温度 (0.0-2.0)
max_tokens: 2048          # 最大生成token数
top_p: 0.9               # nucleus sampling参数
frequency_penalty: 0.0   # 频率惩罚 (-2.0-2.0)
presence_penalty: 0.0    # 存在惩罚 (-2.0-2.0)

# 特殊功能支持
supports_streaming: true # 是否支持流式输出
supports_functions: true # 是否支持函数调用
supports_vision: false   # 是否支持视觉输入
supports_embedding: false # 是否支持嵌入向量生成

# 速率限制 (可选)
rate_limit:
  requests_per_minute: 60
  tokens_per_minute: 90000

# 代理设置 (可选)
proxy:
  http: "http://proxy.example.com:8080"
  https: "http://proxy.example.com:8080"
```

## 🚀 使用方法

### 步骤1：准备API密钥
为保护敏感信息，建议使用环境变量存储API密钥：

```bash
# 在系统环境变量中设置（Windows PowerShell）
$env:OPENAI_API_KEY="sk-your-openai-key-here"
$env:ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"
$env:ZHIPU_API_KEY="your-zhipu-key-here"
$env:YI_API_KEY="your-yi-key-here"

# 或在用户级别永久设置
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'your-key', 'User')
```

### 步骤2：创建或编辑模型配置文件
在 `.workbuddy/AI协作体系/模型配置/` 目录中：
1. 参考现有示例文件创建新的配置文件
2. 使用环境变量引用保护敏感信息：`api_key: "${OPENAI_API_KEY}"`
3. 根据需求调整模型参数

### 步骤3：在智能体中引用模型
编辑智能体定义时，在 `model_config` 部分指定要使用的模型：

```yaml
model_config:
  model_name: "model-identifier"  # 对应配置文件名（不含.yaml后缀）
  provider: "model-provider"      # 可选字段用于验证
```

例如：
```yaml
model_config:
  model_name: "openai-gpt4"  # 将使用 openai-gpt4.yaml 配置
  provider: "openai"
```

### 步骤4：验证配置
检查模型配置文件是否就位：
```bash
# 检查配置文件是否存在
dir .workbuddy\AI协作体系\模型配置\*.yaml

# 验证索引完整性
python .workbuddy/scripts/update_index.py
```

## 📝 配置示例

### OpenAI GPT-4 配置
```yaml
model_name: "OpenAI GPT-4 Turbo"
provider: "openai"
model_version: "gpt-4-turbo-preview"

api_key: "${OPENAI_API_KEY}"
api_base: "https://api.openai.com/v1"
api_version: "v1"

temperature: 0.7
max_tokens: 4096
top_p: 0.9
frequency_penalty: 0.0
presence_penalty: 0.0

supports_streaming: true
supports_functions: true
supports_vision: true
supports_embedding: true

rate_limit:
  requests_per_minute: 500
  tokens_per_minute: 90000
```

### Anthropic Claude 3 配置
```yaml
model_name: "Anthropic Claude 3 Opus"
provider: "anthropic"
model_version: "claude-3-opus-20240229"

api_key: "${ANTHROPIC_API_KEY}"
api_base: "https://api.anthropic.com"
api_version: "v1"

temperature: 0.7
max_tokens: 4096
top_p: 0.9
frequency_penalty: 0.0
presence_penalty: 0.0

supports_streaming: true
supports_functions: false  # Claude 目前不支持函数调用（但支持工具使用）
supports_vision: true
supports_embedding: false

rate_limit:
  requests_per_minute: 50
  tokens_per_minute: 100000
```

### 本地部署模型（Ollama）配置
```yaml
model_name: "Ollama Llama 3"
provider: "ollama"
model_version: "llama3"

api_base: "http://localhost:11434"
api_version: "v1"

temperature: 0.7
max_tokens: 2048
top_p: 0.9
frequency_penalty: 0.0
presence_penalty: 0.0

supports_streaming: true
supports_functions: true
supports_vision: false
supports_embedding: false
```

### 自定义API端点配置
```yaml
model_name: "自定义模型API"
provider: "custom"
model_version: "v1.0"

api_key: "${CUSTOM_API_KEY}"
api_base: "https://api.example.com/v1"
api_version: "v1"

temperature: 0.7
max_tokens: 2048
top_p: 0.9
frequency_penalty: 0.0
presence_penalty: 0.0

supports_streaming: true
supports_functions: true
supports_vision: false
supports_embedding: false
```

## 🔐 安全最佳实践

1. **使用环境变量**：永远不要将API密钥直接写入配置文件
2. **最小权限原则**：为不同用途创建不同的API密钥，只授予必要的权限
3. **定期轮换**：定期更新API密钥以降低泄露风险
4. **监控使用**：定期检查API使用情况以发现异常
5. **限制IP范围**：如果API提供商支持，限制密钥只能从特定IP使用
6. **使用代理**：在企业环境中考虑使用API代理进行统一管理

## 💡 高级使用技巧

### 模型选择策略
不同任务选择不同的模型可以优化成本和性能：

| 任务类型 | 推荐模型 | 原因 |
|----------|----------|------|
| 复杂推理和决策 | GPT-4, Claude 3 Opus | 强大的理解和推理能力 |
| 快速响应和聊天 | GPT-3.5, Claude 3 Haiku | 更快的响应速度 |
| 代码生成 | GPT-4 Turbo, DeepSeek-Coder | 特别优化的代码能力 |
| 多模态处理 | GPT-4V, Claude 3 Vision | 支持图像输入 |
| 本地隐私敏感 | Ollama Llama 3 | 数据不离开本地环境 |
| 成本敏感 | Yi-Light, GLM-4 | 性价比更高的选择 |

### 动态模型切换
在高级使用场景中，可以根据任务特性动态选择模型：
- 简单查询使用快速廉价模型
- 复杂分析使用强大推理模型
- 创意写作使用擅长生成的模型
- 代码任务使用专门的代码模型

### 批量处理优化
对于批量处理任务：
1. 使用支持更高速率限制的模型
2. 调整temperature降低随机性提高一致性
3. 考虑使用批量API端点（如果可用）
4. 实现重试机制和指数 backoff

## 🔄 维护和更新

### 添加新模型支持
1. 研究新模型的API文档和参数
2. 在模型配置目录中创建新的YAML文件
3. 参现有配置文件的格式和结构
4. 测试配置是否正确加载
5. 在智能体定义中引用新模型进行验证

### 更新现有配置
1. 定期检查模型提供商的API更新
2. 根据新功能更新supports_*字段
3. 调整速率限制和其他参数
4. 保持配置文件的注释和说明更新

### 故障排除
如果遇到模型配置问题：
1. 检查YAML语法是否正确
2. 验证环境变量是否正确设置
3. 确认模型名称与配置文件名匹配
4. 检查API密钥是否有效和未过期
5. 查看系统日志了解具体错误信息

## 📖 参考文档

- `.workbuddy/AI协作体系/AI协调协作系统.md` - 详细的AI协作系统说明
- `.workbuddy/AI协作体系/智能体池/智能体定义.md` - 智能体定义和使用说明
- `.workbuddy/AI协作体系/项目模板/项目配置.md` - 项目级智能体配置示例
- `.workbuddy/AI协作体系/模型配置/模型配置说明.md` - 模型配置系统说明

## ✅ 验证您的配置

为了确保您的模型配置正确，请执行以下检查：

1. **文件存在检查**：确认`.workbuddy/AI协作体系/模型配置/{model_name}.yaml`文件存在
2. **YAML语法检查**：使用YAML验证工具检查文件格式是否正确
3. **环境变量检查**：确认所有使用的环境变量都已正确设置
4. **字段完整性检查**：验证所有必需字段都存在且类型正确
5. **索引检查**：运行 `python .workbuddy/scripts/update_index.py` 确认系统完整性

---
*通过遵循此配置指南，您可以轻松在通用知识库框架中集成和使用各种AI大模型，实现真正的"零配置开箱即用"多模型智能体协作平台。*"