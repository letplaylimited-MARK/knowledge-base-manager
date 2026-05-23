---
title: MCP Server
type: entity
aliases: [MCP Server, MCP服务, Model Context Protocol Server]
category: 系统组件
tags: [MCP, API, 工具暴露, STDIO, Server]
confidence: high
created: 2026-05-23
updated: 2026-05-23
---

# MCP Server

## 概述

MCP (Model Context Protocol) Server 是本系统的对外API入口之一。它通过 MCP 协议暴露 20 个工具给 AI 客户端（如 Claude Desktop、WorkBuddy 等），使外部AI能够调用本系统的知识检索、文件处理、记忆管理和工作流编排能力。

## 技术属性

| 属性 | 值 |
|------|-----|
| 实现文件 | `mcp_server.py` |
| 协议 | MCP (Model Context Protocol) |
| 通信方式 | stdio (标准输入/输出) |
| 工具数量 | 20 |
| Python版本 | 3.8+ |

## 暴露的20个MCP工具

### 搜索类 (4)
1. `search_all` — 混合搜索（关键词+语义）
2. `vector_search` — 纯语义向量搜索
3. `search_memory` — 记忆层搜索
4. `keyword_search` — SQLite FTS5关键词搜索

### 内容处理类 (5)
5. `analyze_content` — 内容智能分析
6. `route_content` — 内容智能路由分发
7. `process_file` — 单文件处理管道
8. `extract_docx_text` — Word文档文本提取
9. `analyze_project_relationships` — 项目关系分析

### 索引/维护类 (3)
10. `rebuild_index` — 重建全文+向量索引
11. `run_maintenance` — 运行系统维护
12. `run_backup` — 执行备份

### 工作流类 (3)
13. `run_file_pipeline` — 批量文件处理管道
14. `project_decision_workflow` — 项目决策工作流
15. `run_workflow` — 通用工作流执行

### 查询/监控类 (5)
16. `get_status` — 系统状态查询
17. `get_graph` — 知识图谱查询
18. `watch_inbox` — 收件箱监控
19. `get_content_stats` — 内容统计
20. `enhanced_scan_inbox` — 增强收件箱扫描

## 配置方式

在 MCP 客户端配置中添加：
```json
{
  "mcpServers": {
    "knowledge-framework": {
      "command": "python",
      "args": ["mcp_server.py"],
      "cwd": "/path/to/project"
    }
  }
}
```

## 与其他组件的关系

- **依赖**: `.workbuddy/scripts/` 下所有工具脚本
- **并列**: `app.py` (Flask Web UI) 提供另一入口
- **被依赖**: AI客户端通过此接口使用系统能力

## 参考来源

- 系统实现: `mcp_server.py` (主入口)
- 文档: `API文档.md`、`快速上手指南.md`

---
*此实体记录了系统的MCP API入口点*
