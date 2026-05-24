import sys
from pathlib import Path

for fname in ['协调员.md', '扫描员.md', '分析师.md', '推荐员.md', '架构师.md', '观察员.md']:
    p = Path('.workbuddy/AI协作体系/角色库') / fname
    if p.exists():
        t = p.read_text(encoding='utf-8')
        has_cn = any(ord(c) > 127 for c in t)
        print(f'{fname}: {len(t)} chars, has_chinese={has_cn}')
    else:
        print(f'{fname}: NOT FOUND')

# Verify RoleLoader returns all 6 roles
sys.path.insert(0, str(Path(__file__).resolve().parent))
from path_setup import setup_scripts_only  # noqa: E402
setup_scripts_only()
from agent_orchestrator import RoleLoader  # noqa: E402
rl = RoleLoader()
for atype in ['coordinator','scanner','analyzer','recommender','architect','observer']:
    role = rl.load(atype)
    print(f'  Role "{atype}" -> {"FOUND" if role else "MISSING"} ({len(role)} chars)' if role else f'  Role "{atype}" -> MISSING')
