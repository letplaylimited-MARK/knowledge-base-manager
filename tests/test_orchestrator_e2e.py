import pytest


class MockAdapter:
    def chat(self, model, messages):
        assert model is not None
        assert len(messages) >= 2
        return f"Mock response for {model}: task received"


class MockMemoryOS:
    def __init__(self, **kwargs):
        self.calls = []

    def add_memory(self, **kwargs):
        self.calls.append(kwargs)


@pytest.fixture(autouse=True)
def mock_memoryos(monkeypatch):
    import memoryos as mo
    monkeypatch.setattr(mo, "MemoryOS", MockMemoryOS)


class TestOrchestratorE2E:
    def test_execute_with_mock_adapter(self):
        from agent_orchestrator import AgentOrchestrator, Agent

        orch = AgentOrchestrator(model_adapter=MockAdapter())
        agent = Agent(name="test-agent", role="coordinator", model="openai-gpt4", instructions="Test instructions")
        result = orch.execute(agent, "Hello, do something")
        assert "Mock response" in result
        assert "openai-gpt4" in result

    def test_load_agent_then_execute(self):
        from agent_orchestrator import AgentOrchestrator

        orch = AgentOrchestrator(model_adapter=MockAdapter())
        agent = orch.load_agent("协调员")
        assert agent is not None, "Agent '协调员' should be loadable"
        assert agent.role is not None
        result = orch.execute(agent, "Analyze this file")
        assert "Mock response" in result

    def test_assign_role_then_execute(self):
        from agent_orchestrator import AgentOrchestrator, Agent

        orch = AgentOrchestrator(model_adapter=MockAdapter())
        agent = Agent(name="scanner-test", role="scanner", model="anthropic-claude3", instructions="scan")
        task = "Find all markdown files"
        enhanced = orch.assign_role(agent, task)
        assert "Find all markdown files" in enhanced
        assert len(enhanced) > len(task)

        result = orch.execute(agent, task)
        assert "Mock response" in result
