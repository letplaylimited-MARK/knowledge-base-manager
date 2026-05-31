# 03.数据库管理_文件夹整理AI应用 -- INDEX

> 定位: 通用知识库框架 **V2.0 生产级应用** | 2026-05-23
> 技术栈: Flask + SQLite + FAISS + MCP | 测试: 107/107 pass

## 文件结构
```
03.数据库管理_文件夹整理AI应用/
├── README.md
├── app.py                     Flask 主应用入口
├── requirements.txt           依赖清单
├── API文档.md                 接口文档
├── 00-快速开始/               入门引导 (setup.bat + README)
├── 01-收件箱/                 新知识入口
├── 02-对话记录/               对话存档
├── 03-资产库/                 可复用资产
├── 04-输出成果/               产出物
├── 05-知识沉淀/               知识库 (含 wiki/ 子目录)
├── 06-参考资料/               参考资料
├── 07-项目文档/               项目文档
├── 99-归档/                   历史归档
├── .workbuddy/                系统配置
│   ├── 记忆层/     持久化记忆引擎
│   ├── AI协作体系/ AI协作配置
│   └── FRAMEWORK.md 框架说明
├── docs/                      补充文档
│   └── 结构体系.md
└── tests/                     测试套件 (107/107)
```

## 关键入口
| 文件 | 用途 | 优先级 |
|------|------|--------|
| 00-快速开始/README.md | 5 分钟入门引导 | 高 |
| 00-快速开始/setup.bat | 一键初始化脚本 | 高 |
| app.py | Flask 知识库服务入口 | 高 |
| .workbuddy/FRAMEWORK.md | 框架完整说明 | 中 |
| API文档.md | HTTP 接口文档 | 中 |
| .workbuddy/记忆层/ | 长期记忆引擎 (MemoryOS 完整实现) | 中 |
| docs/结构体系.md | 目录结构详解 | 低 |

## 快速开始
```
# 一键初始化
00-快速开始/setup.bat

# 或手动
python -m venv .venv
.venv/Scripts/activate       # Windows
pip install -r requirements.txt
pytest tests/ -v             # 验证安装 (107/107)
python app.py                # 启动服务
```

## 核心功能
| 功能 | 实现位置 |
|------|----------|
| 知识图谱管理 | 05-知识沉淀/wiki/ |
| 长期记忆系统 | .workbuddy/记忆层/ (MemoryOS 三层引擎) |
| AI 协作体系 | .workbuddy/AI协作体系/ |
| 向量检索 | .workbuddy/scripts/vector_search.py (SQLite + FAISS) |
| 自动化处理 | 24 个 Python 脚本 |
