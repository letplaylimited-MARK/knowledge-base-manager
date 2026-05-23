import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from path_setup import setup_scripts_only; setup_scripts_only()
from agent_orchestrator import AgentOrchestrator, AgentLoader

ao = AgentOrchestrator()

# Test load by Chinese name
for name in ['协调员', '信息扫描员', '分析员', '推荐员']:
    agent = ao.load_agent(name)
    print(f'load({name!r}): {agent.name if agent else "NONE"}')

# Test load by English type
for atype in ['coordinator', 'scanner', 'analyzer', 'recommender']:
    agent = ao.load_agent(atype)
    print(f'load({atype!r}): {agent.name if agent else "NONE"} -> model={agent.model if agent else "?"}')

# Test list_all
loader = AgentLoader()
agents = loader.list_agents()
print(f'\nTotal agents: {len(agents)}')
for a in agents:
    print(f'  name={a.name!r}, role={a.role!r}, model={a.model!r}')
