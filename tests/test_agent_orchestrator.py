

class TestAgentLoader:
    def test_load_by_cn_name(self):
        from agent_orchestrator import AgentLoader
        loader = AgentLoader()
        agent = loader.load("协调员")
        assert agent is not None
        assert agent.name == "协调员"
        assert agent.role == "coordinator"

    def test_load_by_en_type(self):
        from agent_orchestrator import AgentLoader
        loader = AgentLoader()
        agent = loader.load("analyzer")
        assert agent is not None
        assert agent.role == "analyzer"

    def test_load_nonexistent(self):
        from agent_orchestrator import AgentLoader
        loader = AgentLoader()
        assert loader.load("不存在的智能体999") is None

    def test_list_agents(self):
        from agent_orchestrator import AgentLoader
        loader = AgentLoader()
        agents = loader.list_agents()
        assert len(agents) >= 4
        names = {a.name for a in agents}
        assert "协调员" in names
        assert "推荐员" in names


class TestRoleLoader:
    def test_load_analyzer(self):
        from agent_orchestrator import RoleLoader
        rl = RoleLoader()
        role = rl.load("analyzer")
        assert role is not None
        assert "分析师" in role

    def test_load_coordinator(self):
        from agent_orchestrator import RoleLoader
        rl = RoleLoader()
        role = rl.load("coordinator")
        assert role is not None
        assert "协调员" in role

    def test_load_scanner(self):
        from agent_orchestrator import RoleLoader
        rl = RoleLoader()
        role = rl.load("scanner")
        assert role is not None
        assert "扫描员" in role

    def test_load_unknown_type_falls_through(self):
        from agent_orchestrator import RoleLoader
        rl = RoleLoader()
        assert rl.load("zzz_nonexistent_role") is None


class TestAgentOrchestrator:
    def test_load_and_execute(self):
        from agent_orchestrator import AgentOrchestrator
        ao = AgentOrchestrator()
        agent = ao.load_agent("coordinator")
        assert agent is not None
        assert agent.model == "openai-gpt4"

    def test_assign_role_appends_task(self):
        from agent_orchestrator import Agent, AgentOrchestrator
        ao = AgentOrchestrator()
        agent = Agent(name="test", role="analyzer", model="test", instructions="do work")
        result = ao.assign_role(agent, "my task")
        assert "my task" in result
        assert "分析师" in result or "分析" in result
