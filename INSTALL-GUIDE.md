# 通用知识库框架 — 安装指南

> 本指南帮助你在 10 分钟内完成知识库框架的安装和启动。

---

## 前置要求

| 环境 | 最低版本 | 推荐 |
|------|---------|------|
| Python | 3.8 | 3.10+ |
| pip | 21.0 | 最新 |
| 操作系统 | Windows 10 / Ubuntu 20.04 / macOS 11 | Windows 11 / Ubuntu 22.04 |

---

## 快速安装（3 步）

### 步骤 1：克隆仓库

```bash
git clone https://github.com/letplaylimited-MARK/knowledge-base-manager.git
cd knowledge-base-manager
```

### 步骤 2：安装依赖

```bash
pip install -r requirements.txt
```

### 步骤 3：验证安装

```bash
python verify_install.py
```

如果显示 "验证通过！项目可正常运行。"，说明安装成功。

---

## 配置环境（可选）

如果你需要使用 AI 模型功能：

```bash
# 1. 复制配置模板
cp .env.example .env

# 2. 编辑 .env，填入你的 API 密钥
# 示例：
OPENAI_API_KEY=sk-xxxxxxxx
ZHIPU_API_KEY=xxxxxxxx.xxxxxx
```

---

## 启动服务

### 方式 A：Web 界面

```bash
python app.py
# 打开浏览器访问 http://localhost:5000
```

### 方式 B：MCP Server（供 AI 工具集成）

```bash
python mcp_server.py
```

### 方式 C：命令行工具

```bash
# 更新知识索引
python .workbuddy/scripts/update_index.py

# 搜索内容
python .workbuddy/scripts/search_content.py "关键词"
```

---

## 常见问题

### Q: pip install 报错？
**A:** 确保 Python >= 3.8，尝试 `pip install --upgrade pip` 后重试。

### Q: verify_install.py 显示 FAIL？
**A:** 根据提示修复对应项，通常是依赖未安装或目录缺失。

### Q: 如何重置项目？
**A:** 运行 `00-快速开始/setup.bat`（Windows）或删除后重新 clone。

---

## 下一步

- [快速上手指南](快速上手指南.md) — 3 分钟学会基本操作
- [用户指南](README.md) — 了解完整功能
- [API文档](API文档.md) — 开发者接口参考
