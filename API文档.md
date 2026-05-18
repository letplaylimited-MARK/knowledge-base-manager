# API文档

> 版本：V2.0 | 更新：2026-04-21

---

## 脚本API

### update_index.py

```bash
python .workbuddy/scripts/update_index.py [选项]
```

**选项**:
- `--config`: 配置文件路径
- `--verbose`: 详细输出
- `--dry-run`: 试运行

### search_content.py

```bash
python .workbuddy/scripts/search_content.py "关键词" [选项]
```

**选项**:
- `--path`: 搜索路径
- `--type`: 搜索类型 (concept/entity/all)
- `--limit`: 结果数量

### extract_docx.py

```bash
python .workbuddy/scripts/extract_docx.py <文件> [选项]
```

**选项**:
- `--output`: 输出文件
- `--format`: 输出格式 (txt/md/json)

### backup.py

```bash
python .workbuddy/脚本/backup.py [选项]
```

**选项**:
- `--path`: 备份路径
- `--compress`: 压缩备份

---

## 知识库API

### 读取知识

```python
from pathlib import Path

def read_knowledge(entity_name):
    path = Path(f"05-知识沉淀/wiki/entities/{entity_name}.md")
    return path.read_text()
```

### 写入知识

```python
def write_knowledge(entity_name, content):
    path = Path(f"05-知识沉淀/wiki/entities/{entity_name}.md")
    path.write_text(content)
```

### 搜索

```python
def search(query):
    results = []
    for p in Path("05-知识沉淀/wiki/").rglob("*.md"):
        if query in p.read_text():
            results.append(p)
    return results
```

---

*更多API请参考源码注释*