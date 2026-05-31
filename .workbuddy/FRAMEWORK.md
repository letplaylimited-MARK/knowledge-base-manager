# 通用知识库框架 - V2.0

> **版本**: V2.0
> **更新日期**: 2026-05-23
> **定位**: 通用知识库框架，集成了知识图谱 + MemoryOS 记忆引擎 + AI 多模型协作的"三体协同"系统

---

## 一、项目架构

### 1.1 目录结构（V2.0）

```
[项目名称]/
├── 00-快速开始/                # 入门指南和安装脚本
│   ├── README.md
│   └── setup.bat
├── 01-收件箱/                  # 新文件入口
│   ├── README.md
│   └── 待处理/
├── 02-对话记录/                # 对话存档
│   └── README.md
├── 03-资产库/                  # 可复用资产
│   ├── README.md
│   └── AI技能/
├── 04-输出成果/                # 产出物
│   └── README.md
├── 05-知识沉淀/                # Wiki 知识库
│   └── wiki/
│       ├── concepts/           # 概念定义
│       ├── entities/           # 实体记录
│       ├── sources/            # 信息来源
│       └── comparisons/        # 对比分析
├── 06-参考资料/                # 外部参考
│   └── README.md
├── 07-项目文档/                # 项目特有
│   └── README.md
├── 99-归档/                   # 历史归档
├── docs/                      # 系统文档
│   ├── 结构体系.md
│   ├── 三体体系.md
│   ├── 验证指南.md
│   ├── 完整使用指南.md
│   ├── AI模型配置指南.md
│   └── superpowers/           # 开发计划与规格
├── tests/                     # 测试套件（15个测试文件，107个用例）
├── .github/workflows/         # CI/CD 配置
├── .workbuddy/                # 核心系统
│   ├── scripts/               # 24个自动化脚本
│   │   ├── knowledge_db/      # 知识库子模块
│   │   │   ├── file_scanner.py
│   │   │   └── relation_discovery.py
│   │   ├── vector_search.py   # FAISS语义搜索
│   │   ├── smart_router.py    # 智能路由
│   │   ├── agent_orchestrator.py  # Agent编排
│   │   ├── model_adapter.py   # 多模型适配器
│   │   ├── memoryos.py        # 记忆引擎（位于 记忆层/）
│   │   └── ... (共24个脚本)
│   ├── templates/             # Web UI 模板
│   ├── AI协作体系/            # AI 多模型协作
│   │   ├── AI协作/
│   │   ├── 智能体池/
│   │   ├── 角色库/            # 6个角色定义
│   │   ├── 模型配置/
│   │   └── 项目模板/
│   ├── 记忆层/                # MemoryOS 记忆系统
│   │   ├── memoryos.py
│   │   ├── MEMORY.md
│   │   ├── memory_data/
│   │   ├── 任务记忆/
│   │   ├── 经验库/
│   │   └── 项目知识/
│   ├── 流程/                  # 工作流程文档
│   ├── 七角色/                # 协作角色定义
│   ├── config/
│   ├── index/                 # 搜索索引
│   └── backup/                # 备份
├── app.py                     # Flask Web 入口
├── mcp_server.py              # MCP 协议服务器（20个工具）
├── requirements.txt           # 依赖声明
├── requirements-lock.txt      # 依赖锁定
├── README.md                  # 项目说明
├── README-EN.md               # English version
├── AGENTS.md                  # AI Agent 行为规则
├── API文档.md                 # API 文档
└── FRAMEWORK.md               # 框架说明（本文件）
```

---

## 二、三体协同架构（V2.0 核心）

### 2.1 知识图谱体系
- **路径**: `05-知识沉淀/wiki/`
- **结构**: concepts（概念）/ entities（实体）/ sources（来源）/ comparisons（对比）
- **检索**: 文件扫描关键词检索 + SQLite 索引 + FAISS 向量语义搜索（混合检索）

### 2.2 MemoryOS 记忆引擎
- **路径**: `.workbuddy/记忆层/`
- **能力**: 短期/中期/长期记忆，JSON/JSONL 文件持久化
- **持久化**: `memory_data/` 目录（已纳入 .gitignore）

### 2.3 AI 协作系统
- **路径**: `.workbuddy/AI协作体系/`
- **模型**: OpenAI GPT-4 / Anthropic Claude 3 / 智谱 GLM-4 / 零一 Yi-Light
- **角色**: 6 个预定义角色（协调员/扫描员/分析师/推荐员/架构师/观察员）

---

## 三、双入口架构

### 3.1 Flask Web UI
```bash
python app.py
# 访问 http://127.0.0.1:5000
```

### 3.2 MCP Server
- **工具数**: 20 个 MCP tools
- **覆盖**: 搜索、索引、管理、编排、记忆存取、收件箱监控
- **入口**: `python mcp_server.py`

---

## 四、命名规范

### 4.1 文件命名
```
格式: [主题]·[类型]-[特性]-[版本]-[日期].[扩展名]
```

### 4.2 目录命名
```
格式: [序号]-[目录名]/
```

### 4.3 标签规范
```
#平台运营 #主播体系 #知识管理 #AI协作 #MCP
状态: #已验证 #待测试 #零幻觉
```

---

## 五、Git 使用规范

### 5.1 提交规范
```
格式: [类型] 简短描述
类型: ✨新功能 🔧优化 📝文档 🐛修复 🚀重大更新 🗑️清理
```

### 5.2 分支规范
```
main          # 主分支，稳定版本
├── dev       # 开发分支
├── feature/* # 功能分支
└── fix/*     # 修复分支
```

---

## 六、依赖说明

| 类别 | 依赖 | 说明 |
|------|------|------|
| 核心 | flask, mcp, pyyaml, numpy | 必须安装 |
| AI模型 | openai, anthropic, zhipuai | 按需安装 |
| 向量搜索 | sentence-transformers, faiss-cpu | 约1.5GB，可选 |
| 文档处理 | python-docx, openpyxl, markdown, beautifulsoup4 | 可选 |
| 监控 | watchdog | 可选 |
| 测试 | pytest, pytest-cov, pytest-asyncio | 开发依赖 |

> 推荐使用 `requirements-lock.txt` 安装以获取稳定版本。

---

## 七、模板文件索引

| 文件 | 用途 | 路径 |
|------|------|------|
| README.md | 项目说明 | ./README.md |
| AGENTS.md | Agent 行为规则 | ./AGENTS.md |
| docs/结构体系.md | 结构说明 | docs/结构体系.md |
| docs/三体体系.md | 三体协同说明 | docs/三体体系.md |
| docs/验证指南.md | 验证标准 | docs/验证指南.md |
| docs/完整使用指南.md | 完整使用指南 | docs/完整使用指南.md |
| API文档.md | API 文档 | ./API文档.md |

---

## 八、交付配置

### 交付前检查清单

```
□ .gitignore 正确配置（不排除核心脚本）
□ requirements-lock.txt 与 requirements.txt 一致
□ 所有文档版本号统一为 V2.0
□ 测试套件 107/107 全通过
□ CI/CD 配置完整（Python 3.12/3.13/3.14）
□ FRAMEWORK.md 与实际目录结构一致（本文件）
□ 无敏感文件泄露（.env、.coverage 等已排除）
```

---

*本框架可复刻到任何新项目。V2.0 核心价值在于"三体协同"——知识图谱 + MemoryOS + AI多模型协作，并通过 MCP 协议暴露为标准化的 AI 工具接口。*
