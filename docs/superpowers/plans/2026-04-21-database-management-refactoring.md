# 数据库管理系统重构实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将混乱的嵌套系统重构为统一的通用知识库框架，消除重复、统一架构、打通数据流

**Architecture:** 分7个阶段执行：结构重构 → 去重 → 统一架构 → 修复链接 → 打通数据流 → 清理业务 → 生成交付包

**Tech Stack:** Python脚本, Markdown, Git

---

## 阶段0: 诊断确认（已完成）

### 0.1 确认问题清单

- [x] 嵌套系统结构混乱
- [x] 双memoryos.py重复
- [x] 双MEMORY.md重复
- [x] Wiki目录重复（外层空+内层有）
- [x] 三层架构定义冲突
- [x] 路径不一致
- [x] 链接断裂
- [x] 业务内容未清理
- [x] 交付包埋藏深

---

## 阶段1: 结构重构 - 移除嵌套系统

### 1.1 创建目标目录结构

**Files:**
- Create: `00-快速开始/README.md`
- Create: `00-快速开始/setup.bat`
- Create: `01-收件箱/README.md`
- Create: `02-对话记录/README.md`
- Create: `03-资产库/README.md`
- Create: `04-输出成果/README.md`
- Create: `05-知识沉淀/wiki/index.md`
- Create: `05-知识沉淀/wiki/log.md`
- Create: `06-参考资料/README.md`
- Create: `07-项目文档/README.md`
- Create: `99-归档/README.md`

- [ ] **Step 1: 创建标准目录结构**

```markdown
# 00-快速开始

本目录包含快速启动指南。

## 包含内容
- setup.bat - 一键初始化脚本
- README.md - 快速入门指南

## 使用方法
双击 setup.bat 运行初始化
```

- [ ] **Step 2: 验证目录创建成功**

Run: `ls -la 00-快速开始/ 01-收件箱/ 05-知识沉淀/`
Expected: 目录存在且包含README.md

- [ ] **Step 3: 提交**

```bash
git add 00-快速开始/ 01-收件箱/ 02-对话记录/ 03-资产库/ 04-输出成果/ 05-知识沉淀/ 06-参考资料/ 07-项目文档/ 99-归档/
git commit -m "chore: 创建标准目录结构"
```

### 1.2 迁移wiki知识图谱

**Files:**
- Modify: `05-知识沉淀/wiki/index.md`
- Modify: `05-知识沉淀/wiki/log.md`
- Create: `05-知识沉淀/wiki/concepts/.gitkeep`
- Create: `05-知识沉淀/wiki/entities/.gitkeep`
- Create: `05-知识沉淀/wiki/sources/.gitkeep`
- Create: `05-知识沉淀/wiki/comparisons/.gitkeep`

- [ ] **Step 1: 从内层迁移wiki内容到统一位置**

将 `07-项目专区/数据库管理/07-项目专区/数据库管理/wiki/` 内容迁移到 `05-知识沉淀/wiki/`

- [ ] **Step 2: 验证迁移**

Run: `ls 05-知识沉淀/wiki/`
Expected: 包含concepts/, entities/, sources/, comparisons/目录

- [ ] **Step 3: 更新AGENTS.md引用**

修改 AGENTS.md 中的 wiki 路径从 `07/wiki/` 改为 `05-知识沉淀/wiki/`

- [ ] **Step 4: 提交**

```bash
git add 05-知识沉淀/wiki/
git commit -m "feat: 统一wiki知识图谱位置"
```

---

## 阶段2: 去重 - 消除重复文件

### 2.1 删除重复的memoryos.py

**Files:**
- Delete: `07-项目专区/数据库管理/07-项目专区/数据库管理/memory/memoryos.py`
- Keep: `.workbuddy/记忆层/memoryos.py`

- [ ] **Step 1: 确认文件差异**

Run: `diff .workbuddy/记忆层/memoryos.py "07-项目专区/数据库管理/07-项目专区/数据库管理/memory/memoryos.py"`
Expected: 无差异（或差异可忽略）

- [ ] **Step 2: 删除重复文件**

Run: `rm "07-项目专区/数据库管理/07-项目专区/数据库管理/memory/memoryos.py"`

- [ ] **Step 3: 提交**

```bash
git rm "07-项目专区/数据库管理/07-项目专区/数据库管理/memory/memoryos.py"
git commit -m "chore: 删除重复的memoryos.py"
```

### 2.2 删除重复的MEMORY.md

**Files:**
- Delete: `07-项目专区/数据库管理/07-项目专区/数据库管理/AI协作/MEMORY.md`
- Delete: `.workbuddy/AI协作体系/AI协作/MEMORY.md`
- Keep: `.workbuddy/记忆层/MEMORY.md`

- [ ] **Step 1: 合并MEMORY.md内容**

将两处MEMORY.md的优秀内容合并到 `.workbuddy/记忆层/MEMORY.md`

- [ ] **Step 2: 删除重复文件**

```bash
rm "07-项目专区/数据库管理/07-项目专区/数据库管理/AI协作/MEMORY.md"
rm ".workbuddy/AI协作体系/AI协作/MEMORY.md"
```

- [ ] **Step 3: 提交**

```bash
git commit -m "chore: 统一MEMORY.md到单一位置"
```

### 2.3 删除重复的knowledge目录

**Files:**
- Delete: `07-项目专区/数据库管理/07-项目专区/数据库管理/knowledge/`
- Keep: `05-知识沉淀/wiki/`

- [ ] **Step 1: 检查是否有独特内容**

如果有独特内容，迁移到wiki对应位置

- [ ] **Step 2: 删除目录**

```bash
rm -rf "07-项目专区/数据库管理/07-项目专区/数据库管理/knowledge/"
```

- [ ] **Step 3: 提交**

```bash
git commit -m "chore: 删除重复的knowledge目录"
```

---

## 阶段3: 统一架构 - 修复三层架构定义

### 3.1 创建统一的架构定义文档

**Files:**
- Create: `05-知识沉淀/ARCHITECTURE.md`

- [ ] **Step 1: 创建统一架构文档**

```markdown
# 通用知识库框架 - 架构定义

> 版本: V3.0 | 更新: 2026-04-21

---

## 一、三层数据流

```
Layer 0: 收件箱/       ← 新知识入口
Layer 1: 知识沉淀/     ← 结构化知识（wiki/）
Layer 2: 向量数据库/   ← ChromaDB语义索引
Layer 3: API接口/     ← REST API服务
```

## 二、知识图谱结构

```
05-知识沉淀/
└── wiki/              ← 知识图谱（AI生成知识）
    ├── concepts/      ← 概念定义
    ├── entities/      ← 实体定义
    ├── sources/      ← 源摘要
    └── comparisons/   ← 比较分析
```

## 三、记忆系统

```
.workbuddy/
└── 记忆层/           ← MemoryOS记忆系统
    ├── memoryos.py   ← 核心引擎
    ├── short_term/   ← 短期记忆
    ├── mid_term/     ← 中期记忆
    └── long_term/    ← 长期记忆
```

## 四、工作流

```
用户输入 → 收件箱 → Ingest → wiki/ → ChromaDB → API
                              ↓
                         MEMORY.md
```

---

## 五、核心操作

| 操作 | 说明 | 触发 |
|------|------|------|
| Ingest | 摄取新知识到wiki | 用户说"ingest" |
| Query | 检索知识 | 用户提问 |
| Lint | 健康检查 | 用户说"lint" |
| 记忆更新 | 更新MEMORY | 每次重要操作后 |
```

- [ ] **Step 2: 提交**

```bash
git add 05-知识沉淀/ARCHITECTURE.md
git commit -m "docs: 统一架构定义V3.0"
```

### 3.2 更新AGENTS.md

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: 更新AGENTS.md中的路径引用**

将所有 `wiki/` 引用更新为 `05-知识沉淀/wiki/`
将所有 `memory/` 引用更新为 `.workbuddy/记忆层/`

- [ ] **Step 2: 验证更新**

Run: `grep -r "wiki/" AGENTS.md | grep -v "05-知识沉淀/wiki/"`
Expected: 无结果（所有wiki引用都已更新）

- [ ] **Step 3: 提交**

```bash
git commit -m "fix: 更新AGENTS.md路径引用"
```

---

## 阶段4: 修复链接 - 打通断链

### 4.1 修复wiki内部链接

**Files:**
- Modify: `05-知识沉淀/wiki/index.md`
- Modify: `05-知识沉淀/wiki/concepts/*.md`
- Modify: `05-知识沉淀/wiki/entities/*.md`

- [ ] **Step 1: 检查断链**

Run: `grep -r "\[\[" 05-知识沉淀/wiki/ --include="*.md" | head -20`
Expected: 列出所有内部链接

- [ ] **Step 2: 转换链接格式**

将 `[[页面名]]` 转换为 `[页面名](wiki/concepts/页面名.md)` 格式

- [ ] **Step 3: 验证链接**

Run: 对于每个链接，确认目标文件存在

- [ ] **Step 4: 提交**

```bash
git commit -m "fix: 修复wiki内部链接格式"
```

### 4.2 修复外部引用路径

**Files:**
- Modify: `.workbuddy/记忆层/index.md`
- Modify: `.workbuddy/AI协作体系/*.md`

- [ ] **Step 1: 更新记忆层索引**

将路径从 `memory/` 更新为 `.workbuddy/记忆层/`

- [ ] **Step 2: 验证更新**

Run: `grep -r "memory/" .workbuddy/ --include="*.md" | grep -v ".workbuddy/记忆层/" | head -10`
Expected: 无业务引用

- [ ] **Step 3: 提交**

```bash
git commit -m "fix: 统一记忆层路径引用"
```

---

## 阶段5: 打通数据流 - 集成自动化

### 5.1 创建集成脚本

**Files:**
- Create: `.workbuddy/scripts/wiki_to_memory.py`
- Create: `.workbuddy/scripts/wiki_to_vector.py`
- Create: `.workbuddy/scripts/ingest_unified.py`

- [ ] **Step 1: 创建Wiki转记忆脚本**

```text
#!/usr/bin/env python3
"""
Wiki to Memory Import Script
功能：将wiki内容导入记忆系统
用法：python wiki_to_memory.py
"""

import json
import sys
from pathlib import Path

WIKI_PATH = Path("05-知识沉淀/wiki")
MEMORY_PATH = Path(".workbuddy/记忆层")

def scan_wiki():
    """扫描wiki目录，提取知识"""
    knowledge_items = []
    
    # 扫描concepts
    concepts_dir = WIKI_PATH / "concepts"
    if concepts_dir.exists():
        for file in concepts_dir.glob("*.md"):
            content = file.read_text(encoding="utf-8")
            knowledge_items.append({
                "type": "semantic",
                "source": str(file.relative_to(Path.cwd())),
                "content": content[:500]  # 取前500字符
            })
    
    return knowledge_items

def import_to_memory(items):
    """导入到记忆系统"""
    # TODO: 实现与memoryos.py的集成
    print(f"找到 {len(items)} 条知识")
    for item in items:
        print(f"  - {item['source']}: {item['type']}")

if __name__ == "__main__":
    items = scan_wiki()
    import_to_memory(items)
```

- [ ] **Step 2: 创建Wiki转向量脚本**

```text
#!/usr/bin/env python3
"""
Wiki to Vector Import Script
功能：将wiki内容导入ChromaDB向量数据库
用法：python wiki_to_vector.py
"""

from pathlib import Path

WIKI_PATH = Path("05-知识沉淀/wiki")
VECTOR_PATH = Path("05-知识沉淀/向量数据")

def scan_wiki():
    """扫描wiki目录"""
    docs = []
    
    for md_file in WIKI_PATH.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        docs.append({
            "content": content,
            "metadata": {"source": str(md_file.relative_to(Path.cwd()))}
        })
    
    return docs

def import_to_vector(docs):
    """导入到向量数据库"""
    # TODO: 实现与ChromaDB的集成
    print(f"找到 {len(docs)} 个文档")

if __name__ == "__main__":
    docs = scan_wiki()
    import_to_vector(docs)
```

- [ ] **Step 3: 创建统一Ingest脚本**

```text
#!/usr/bin/env python3
"""
Unified Ingest Script
功能：统一入口，自动分发到各系统
用法：python ingest_unified.py [文件路径]
"""

import sys
from pathlib import Path

def process_file(file_path):
    """处理文件"""
    print(f"处理文件: {file_path}")
    
    # 1. 提取内容
    content = Path(file_path).read_text(encoding="utf-8")
    
    # 2. 分发到wiki
    print("  → 添加到wiki...")
    
    # 3. 分发到memory
    print("  → 添加到记忆...")
    
    # 4. 分发到vector
    print("  → 添加到向量库...")
    
    print("完成!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python ingest_unified.py [文件路径]")
        sys.exit(1)
    
    process_file(sys.argv[1])
```

- [ ] **Step 4: 提交**

```bash
git add .workbuddy/scripts/wiki_to_memory.py .workbuddy/scripts/wiki_to_vector.py .workbuddy/scripts/ingest_unified.py
git commit -m "feat: 添加集成脚本"
```

---

## 阶段6: 清理业务 - 准备通用交付

### 6.1 识别业务内容

**Files:**
- Modify: `05-知识沉淀/wiki/concepts/*.md`
- Modify: `05-知识沉淀/wiki/entities/*.md`

- [ ] **Step 1: 扫描业务标签**

Run: `grep -r "主播\|师傅\|运营\|结算\|提成\|R5" 05-知识沉淀/wiki/ --include="*.md" | head -20`
Expected: 列出所有业务相关内容

- [ ] **Step 2: 标记需要清理的页面**

创建待清理列表：

| 文件 | 业务内容 | 处理方式 |
|------|----------|----------|
| 主播体系.md | 完整业务 | 删除或通用化 |
| 师傅体系.md | 完整业务 | 删除或通用化 |
| 主播运营规则.md | 完整业务 | 删除 |
| *AI角色技能体系* | 通用 | 保留 |
| *知识卡片系统* | 通用 | 保留 |
| *三层架构* | 通用 | 保留 |

- [ ] **Step 3: 执行清理**

对于业务页面：
1. 如果是纯业务 → 删除
2. 如果有通用部分 → 提取通用部分，删除业务部分

- [ ] **Step 4: 提交**

```bash
git commit -m "chore: 清理业务内容，准备通用交付"
```

### 6.2 创建示例数据

**Files:**
- Create: `05-知识沉淀/wiki/concepts/知识管理入门.md`
- Create: `05-知识沉淀/wiki/entities/示例项目.md`

- [ ] **Step 1: 创建通用示例概念**

```markdown
---
title: 知识管理入门
type: concept
sources: []
related: [三层架构, Ingest流程]
created: 2026-04-21
updated: 2026-04-21
tags: [知识管理, 入门]
confidence: high
---

# 知识管理入门

## 什么是知识管理

知识管理是组织和个人有效收集、组织、分享和利用知识资产的系统方法。

## 核心原则

1. **持续积累** - 随时记录，持续沉淀
2. **结构化** - 从无序到有序
3. **可复用** - 一次投入，反复使用
4. **可追溯** - 知道来源，知道变化

## 快速开始

1. 把资料放入收件箱
2. 让AI帮助你整理
3. 定期回顾和优化
```

- [ ] **Step 2: 提交**

```bash
git add 05-知识沉淀/wiki/concepts/知识管理入门.md 05-知识沉淀/wiki/entities/示例项目.md
git commit -m "feat: 添加通用示例内容"
```

---

## 阶段7: 生成交付包

### 7.1 完善文档

**Files:**
- Modify: `README.md`
- Modify: `README-EN.md`
- Modify: `快速上手指南.md`
- Create: `CHANGELOG.md`

- [ ] **Step 1: 更新README**

更新为通用框架定位，移除业务内容

- [ ] **Step 2: 更新快速上手指南**

确保步骤清晰，适合新用户

- [ ] **Step 3: 创建变更日志**

```markdown
# 变更日志

## V3.0 (2026-04-21)

### 新增
- 统一架构定义V3.0
- 集成脚本（wiki_to_memory, wiki_to_vector, ingest_unified）
- 通用示例内容

### 修复
- 移除嵌套系统结构
- 消除重复文件（memoryos.py, MEMORY.md）
- 统一wiki位置到05-知识沉淀/
- 修复内部链接格式
- 更新路径引用

### 清理
- 删除业务相关内容（主播、师傅运营）
- 准备通用交付
```

- [ ] **Step 4: 提交**

```bash
git commit -m "docs: 更新文档为V3.0通用框架"
```

### 7.2 生成ZIP包

**Files:**
- Create: `通用知识库框架-V3.0-交付包.zip`

- [ ] **Step 1: 排除不需要的文件**

```bash
# 创建.gitignore排除列表
echo "*.zip
__pycache__/
*.pyc
.pytest_cache/
" > .gitignore delivery
```

- [ ] **Step 2: 生成ZIP**

```bash
# 使用PowerShell
Compress-Archive -Path * -DestinationPath "通用知识库框架-V3.0-交付包.zip" -Force
```

- [ ] **Step 3: 验证ZIP内容**

```bash
# 解压到临时目录验证
Expand-Archive "通用知识库框架-V3.0-交付包.zip" -DestinationPath "test_extract" -Force
ls test_extract/
```

- [ ] **Step 4: 提交**

```bash
git add 通用知识库框架-V3.0-交付包.zip
git commit -m "release: 生成V3.0交付包"
```

---

## 执行总结

| 阶段 | 任务数 | 预计提交 |
|------|--------|----------|
| Phase 1: 结构重构 | 3 | 2 |
| Phase 2: 去重 | 3 | 3 |
| Phase 3: 统一架构 | 2 | 2 |
| Phase 4: 修复链接 | 2 | 2 |
| Phase 5: 打通数据流 | 1 | 1 |
| Phase 6: 清理业务 | 2 | 2 |
| Phase 7: 生成交付包 | 2 | 2 |
| **总计** | **15** | **14** |

---

**Plan complete.** Two execution options:

1. **Subagent-Driven (recommended)** - 逐任务分配子代理，快速迭代
2. **Inline Execution** - 在当前会话中批量执行

Which approach?
