import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable


@dataclass
class Step:
    name: str
    handler: Callable[..., Awaitable[Any]]
    args: dict = field(default_factory=dict)


class WorkflowEngine:
    def __init__(self):
        self._workflows: dict[str, list[Step]] = {}

    def define(self, name: str, steps: list[Step]):
        self._workflows[name] = steps

    async def run(self, name: str, context: dict = None) -> dict:
        steps = self._workflows.get(name)
        if not steps:
            raise ValueError(f"Unknown workflow: {name}")
        ctx = context or {}
        results = {}
        for step in steps:
            merged_args = {**step.args, **ctx}
            result = await step.handler(**merged_args)
            results[step.name] = result
            ctx[step.name] = result
        return {"workflow": name, "results": results}
