"""Unified sys.path setup for all project modules."""
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
_MEMORY_DIR = _SCRIPTS_DIR.parent / "记忆层"


def setup():
    """Add scripts/ and 记忆层/ to sys.path if not already present."""
    scripts_str = str(_SCRIPTS_DIR)
    memory_str = str(_MEMORY_DIR)
    if scripts_str not in sys.path:
        sys.path.insert(0, scripts_str)
    if memory_str not in sys.path:
        sys.path.insert(0, memory_str)


def setup_scripts_only():
    """Add only scripts/ to sys.path (for standalone scripts)."""
    scripts_str = str(_SCRIPTS_DIR)
    if scripts_str not in sys.path:
        sys.path.insert(0, scripts_str)
