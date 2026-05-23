# Production Hardening — Knowledge Management MCP Server

**Date**: 2026-05-19
**Status**: Draft

## Problem

The Knowledge Management MCP Server and associated scripts have full test coverage and pass all static analysis checks, but are not ready for production use. Four gaps remain:

1. Long-running tasks (`run_maintenance`, `run_backup`, `rebuild_index`) block the MCP event loop.
2. All MCP tool handlers lack input validation — any malformed parameter crashes.
3. No error classification — all errors return `{"error": "..."}` with no way to distinguish user mistakes from system failures.
4. Legacy `print()` calls in several scripts interfere with stdio-based MCP transport.

## Scope

Hardening the existing codebase for production deployment. No feature additions, no architectural restructuring.

---

## 1. Async Background Task Manager

### Goal
Prevent long-running tasks from blocking the MCP event loop.

### Design

Introduce a lightweight `TaskManager` class in `mcp_server.py`:

```python
class TaskManager:
    def __init__(self):
        self._tasks: dict[str, asyncio.Task] = {}
        self._results: dict[str, Any] = {}

    async def start(self, name: str, coro) -> str:
        task_id = f"{name}_{uuid4().hex[:8]}"
        self._tasks[task_id] = asyncio.create_task(self._run(task_id, coro))
        return task_id

    async def _run(self, task_id: str, coro):
        try:
            result = await coro
            self._results[task_id] = {"status": "done", "result": result}
        except Exception as e:
            self._results[task_id] = {"status": "failed", "error": str(e)}
        finally:
            self._tasks.pop(task_id, None)

    def get_status(self, task_id: str) -> dict | None:
        if task_id in self._tasks:
            return {"task_id": task_id, "status": "running"}
        return self._results.get(task_id)
```

### Long-Running Tools (make async)
- `rebuild_index`, `run_maintenance`, `run_backup`
- `watch_inbox`, `enhanced_scan_inbox`
- `run_file_pipeline`, `project_decision_workflow`
- `analyze_project_relationships`

### New MCP Tools
1. **`get_task_status`** — `(task_id: string) → {task_id, status, result?, error?}`
2. All long-running tools above return `{task_id, status: "started"}` immediately instead of blocking.

### Files Changed
- `mcp_server.py`

---

## 2. Input Validation

### Goal
Every MCP tool handler validates its parameters before doing work.

### Design

Add a lightweight `validate_params()` function in `mcp_server.py`:

```python
def validate_params(params: dict, schema: dict[str, tuple[type, bool, str]]):
    """Validate params against schema.
    
    schema: {param_name: (type, required, description)}
    """
    for name, (ptype, required, desc) in schema.items():
        if required and name not in params:
            raise UserError(f"Missing required parameter: {name} ({desc})")
        if name in params and not isinstance(params[name], ptype):
            raise UserError(f"Parameter '{name}' must be {ptype.__name__}, got {type(params[name]).__name__}")
```

### Tools with Parameter Validation

| Tool | Parameters | Validations |
|------|-----------|-------------|
| `search_all` | query: str, limit: int | limit ≥ 1, query non-empty |
| `vector_search` | query: str, limit: int | limit ≥ 1, query non-empty |
| `search_memory` | query: str, context: str\|None | query non-empty |
| `keyword_search` | keywords: list[str] | non-empty list |
| `analyze_content` | path: str | path is valid and exists |
| `route_content` | path: str | path non-empty |
| `process_file` | path: str | path is valid and exists |
| `extract_docx_text` | path: str | path ends with .docx, exists |
| `run_file_pipeline` | path: str | path is valid and exists |
| `project_decision_workflow` | path: str | path is valid and exists |
| `analyze_project_relationships` | path: str\|None | if set, path is valid |
| `run_workflow` | name: str, context: str\|None | name in known workflows |

### Files Changed
- `mcp_server.py`

---

## 3. Error Classification

### Goal
Return structured errors that allow the caller to distinguish mistake from system failure.

### Design

New file `.workbuddy/scripts/errors.py`:

```python
class AppError(Exception):
    def __init__(self, message: str, error_type: str):
        self.message = message
        self.type = error_type
        super().__init__(message)

class UserError(AppError):
    def __init__(self, message: str):
        super().__init__(message, "user")

class SystemError(AppError):
    def __init__(self, message: str):
        super().__init__(message, "system")

class UnexpectedError(AppError):
    def __init__(self, message: str = "Internal error"):
        super().__init__(message, "unexpected")
```

### Error Handler in MCP Server

Replace bare `except Exception:` blocks:

```python
try:
    ...
except UserError as e:
    return {"error": e.message, "type": e.type}
except SystemError as e:
    logger.error(f"System error: {e.message}")
    return {"error": e.message, "type": e.type}
except Exception as e:
    logger.exception("Unexpected error")
    return {"error": "Internal error", "type": "unexpected"}
```

### Files Changed
- `.workbuddy/scripts/errors.py` (new)
- `mcp_server.py` (error handler wrapper)

---

## 4. Legacy `print()` → `logging`

### Goal
All scripts use `logging.getLogger(__name__)` instead of `print()`, preventing stderr pollution of MCP stdio transport.

### Design

Affected scripts:
- `.workbuddy/scripts/auto_organizer.py`
- `.workbuddy/scripts/content_analyzer.py`
- `.workbuddy/scripts/inbox_watcher.py`
- `.workbuddy/scripts/smart_router.py`
- `.workbuddy/scripts/project_relationship_manager.py`
- `.workbuddy/scripts/maintenance_task.py`
- `.workbuddy/scripts/enhanced_inbox_watcher.py`

Each gets:
```python
import logging
logger = logging.getLogger(__name__)
```

And `print()` / `print(f"...")` replaced with `logger.info(...)`, `logger.warning(...)`, `logger.error(...)`.

### Files Changed
- 7 script files

---

## 5. Deployment Artifacts

### Goal
Containerized deployment ready in one command.

### Design

**Dockerfile:**
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements-lock.txt .
RUN pip install --no-cache-dir -r requirements-lock.txt
COPY . .
ENV PYTHONPATH=/app/.workbuddy/scripts
CMD ["python", "mcp_server.py"]
```

**docker-compose.yml:**
```yaml
services:
  km-server:
    build: .
    stdin_open: true
    tty: true
    volumes:
      - ./data:/app/data
      - ./:/workspace
    environment:
      - LOG_LEVEL=INFO
      - PYTHONPATH=/app/.workbuddy/scripts
```

**deploy/README.md** — single-page deployment guide covering prerequisites, env vars, volume mounts.

### Files Changed
- `Dockerfile` (new)
- `docker-compose.yml` (new)
- `deploy/README.md` (new)

---

## Testing Strategy

| Component | Test approach | Tests affected |
|-----------|--------------|----------------|
| TaskManager | Unit test: start task, get status, verify non-blocking | `test_mcp_handlers.py` |
| validate_params | Unit test: valid, missing, wrong type | `test_mcp_handlers.py` |
| Error classes | Unit test: raise + catch each type | New file or `test_mcp_handlers.py` |
| print→logging | Manual inspection + CI ruff check | None (no behavior change) |
| Docker | Build test in CI | `.github/workflows/test.yml` |

Existing 103 tests must remain passing throughout.

---

## Success Criteria

- [ ] All 8 long-running MCP tools return immediately with `task_id`, non-blocking
- [ ] All 12 parameter-accepting MCP tools validate input before executing
- [ ] All errors return `{error, type}` with correct classification
- [ ] Zero `print()` calls in `.workbuddy/scripts/` (only `logger.*`)
- [ ] `docker build -t km-server .` succeeds
- [ ] Existing 103 tests still pass
