from dataclasses import dataclass
from pathlib import Path
import re
import sys

SCRIPTS_DIR = Path(__file__).resolve().parent
AGENT_POOL_DIR = SCRIPTS_DIR.parent / "AI协作体系" / "智能体池"
ROLE_LIB_DIR = SCRIPTS_DIR.parent / "AI协作体系" / "角色库"
MEMORY_DIR = SCRIPTS_DIR.parent / "记忆层"


@dataclass
class Agent:
    name: str
    role: str
    model: str
    instructions: str


class AgentLoader:
    def __init__(self):
        self._pool_dir = AGENT_POOL_DIR

    def load(self, name: str) -> Agent | None:
        for ext in [".md"]:
            file_path = self._pool_dir / f"{name}{ext}"
            if file_path.exists():
                return self._parse(file_path)
        for f in self._pool_dir.glob("*.md"):
            if f.stem == name:
                return self._parse(f)
        return None

    def _parse(self, file_path: Path) -> Agent | None:
        try:
            text = file_path.read_text(encoding="utf-8")
        except Exception:
            return None
        name = self._extract(text, [r"agent_name[：:]\s*[\"']?([^\"'\s#]+)", r"名称[：:]\s*(.+)", r"name[：:]\s*(.+)"])
        role = self._extract(text, [r"agent_type[：:]\s*[\"']?([^\"'\s#]+)", r"角色[：:]\s*(.+)", r"role[：:]\s*(.+)"])
        model = self._extract(text, [r"model_name[：:]\s*[\"']?([^\"'\s#]+)", r"模型[：:]\s*(.+)", r"model[：:]\s*(.+)"])
        return Agent(
            name=name or file_path.stem,
            role=role or "unknown",
            model=model or "default",
            instructions=text
        )

    def _extract(self, text: str, patterns: list[str]) -> str | None:
        for p in patterns:
            m = re.search(p, text)
            if m:
                return m.group(1).strip()
        return None


class RoleLoader:
    def __init__(self):
        self._role_dir = ROLE_LIB_DIR

    def load(self, role_name: str) -> str | None:
        for ext in [".md", ".txt", ".yaml", ".yml"]:
            file_path = self._role_dir / f"{role_name}{ext}"
            if file_path.exists():
                try:
                    return file_path.read_text(encoding="utf-8")
                except Exception:
                    return None
        for f in self._role_dir.iterdir():
            if f.is_file() and f.stem == role_name and f.suffix in [".md", ".txt", ".yaml", ".yml"]:
                try:
                    return f.read_text(encoding="utf-8")
                except Exception:
                    return None
        return None


class AgentOrchestrator:
    def __init__(self, model_adapter=None):
        self._adapter = model_adapter
        self._agent_loader = AgentLoader()
        self._role_loader = RoleLoader()

    def _get_adapter(self):
        if self._adapter is None:
            sys.path.insert(0, str(SCRIPTS_DIR))
            from model_adapter import ModelAdapter
            self._adapter = ModelAdapter()
        return self._adapter

    def load_agent(self, name: str) -> Agent | None:
        return self._agent_loader.load(name)

    def assign_role(self, agent: Agent, task: str) -> str:
        role_prompt = self._role_loader.load(agent.role)
        if role_prompt:
            return role_prompt + "\n\n" + task
        return task

    def execute(self, agent: Agent, task: str) -> str:
        adapter = self._get_adapter()
        role_task = self.assign_role(agent, task)
        messages = [
            {"role": "system", "content": agent.instructions},
            {"role": "user", "content": role_task}
        ]
        try:
            result = adapter.chat(agent.model, messages)
        except Exception as e:
            result = f"Error: {e}"
        self.save_state(agent, result)
        return result

    def save_state(self, agent: Agent, result: str):
        try:
            if str(MEMORY_DIR) not in sys.path:
                sys.path.insert(0, str(MEMORY_DIR))
            from memoryos import MemoryOS
            mos = MemoryOS(storage_path=str(MEMORY_DIR / "data"))
            mos.add_memory(
                content=f"Agent {agent.name} execution result",
                memory_type="episodic",
                metadata={
                    "agent": agent.name,
                    "role": agent.role,
                    "model": agent.model,
                    "result": result[:500],
                }
            )
        except Exception as e:
            import warnings
            warnings.warn(f"save_state failed: {e}")
