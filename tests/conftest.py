import sys
from pathlib import Path

# Ensure script modules are importable
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / ".workbuddy" / "scripts"
MEMORY_DIR = Path(__file__).resolve().parent.parent / ".workbuddy" / "记忆层"
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(MEMORY_DIR))
