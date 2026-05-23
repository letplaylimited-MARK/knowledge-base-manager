import pytest


class TestWorkflowEngine:
    @pytest.mark.asyncio
    async def test_define_and_run(self):
        from workflow_engine import WorkflowEngine, Step
        engine = WorkflowEngine()

        async def step_a(ctx: dict = None):
            return {"value": 1}

        engine.define("test_wf", [
            Step(name="a", handler=step_a),
        ])
        result = await engine.run("test_wf")
        assert result["workflow"] == "test_wf"
        assert result["results"]["a"]["value"] == 1

    @pytest.mark.asyncio
    async def test_steps_chain_context(self):
        from workflow_engine import WorkflowEngine, Step
        engine = WorkflowEngine()

        async def step_a(ctx: dict = None):
            return {"value": 1}

        async def step_b(a: dict = None):
            return {"sum": a["value"] + 1}

        engine.define("chain_wf", [
            Step(name="a", handler=step_a),
            Step(name="b", handler=step_b),
        ])
        result = await engine.run("chain_wf")
        assert result["results"]["a"]["value"] == 1
        assert result["results"]["b"]["sum"] == 2

    @pytest.mark.asyncio
    async def test_unknown_workflow_raises(self):
        from workflow_engine import WorkflowEngine
        engine = WorkflowEngine()
        with pytest.raises(ValueError, match="Unknown workflow"):
            await engine.run("nonexistent_wf")
