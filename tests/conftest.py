import sys
from pathlib import Path

# Ensure script modules are importable
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / ".workbuddy" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))
from path_setup import setup  # noqa: E402
setup()
