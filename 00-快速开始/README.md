# 通用知识库框架 - 5分钟快速入门

> 本指南将帮助您3分钟内上手通用知识库框架

---

## 准备工作

- Python 3.8+
- Windows / macOS / Linux

## 第一步：初始化

```bash
# Windows
00-快速开始\setup.bat

# macOS / Linux
python .workbuddy/scripts/update_index.py
```

初始化脚本会：① 安装依赖 ② 创建目录结构 ③ 更新知识索引

## 第二步：了解核心目录

| 目录 | 用途 | 怎么用 |
|------|------|--------|
| `01-收件箱/` | 放新文件 | 文件丢进去，AI自动处理 |
| `03-资产库/` | 可复用资产 | 提示词、脚本、模板 |
| `05-知识沉淀/wiki/` | 知识库 | 概念、实体、来源、比较 |
| `.workbuddy/` | 系统核心 | 脚本、记忆、AI协作 |

## 第三步：添加知识点

1. 在 `05-知识沉淀/wiki/concepts/` 创建 `新概念.md`
2. 添加内容（Markdown格式 + frontmatter）
3. 运行更新：
```bash
python .workbuddy/scripts/update_index.py
```

## 第四步：搜索知识

```bash
python .workbuddy/scripts/search_content.py "您的查询关键词"
```

## 常用操作

### 管理知识
```bash
# 备份知识库
python .workbuddy/scripts/backup.py

# 系统维护
python .workbuddy/scripts/maintenance_task.py
```

### 查看文档

| 文档 | 位置 | 适合谁 |
|------|------|--------|
| 结构体系 | `docs/结构体系.md` | 想了解框架全貌 |
| 三体体系 | `docs/三体体系.md` | 理解三体系集成 |
| 验证指南 | `docs/验证指南.md` | 需要交付验证 |
| AI模型配置 | `docs/AI模型配置指南.md` | 配置AI大模型 |
| API文档 | `API文档.md` | 开发者参考 |

---

## 常见问题

### Q: 初始化时报错？
A: 检查Python版本 (`python --version`)，确保 >= 3.8

### Q: 如何配置AI模型？
A: 编辑 `.workbuddy/AI协作体系/模型配置/` 目录下的YAML文件

### Q: 如何自定义智能体？
A: 编辑 `.workbuddy/AI协作体系/智能体池/智能体定义.md`

### Q: 目录结构找不到？
A: 运行 `setup.bat` 自动创建标准目录

---

*开始使用通用知识库框架，零配置开箱即用！*