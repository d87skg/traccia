"""
Traccia Python SDK v0.1.0

Usage:
    import traccia

    session = traccia.start(objective="Generate Report")
    session.record("api_call", payload={"endpoint": "/v1/report"})
    session.finish()
    session.export("task.evidence")
"""

import sys
from pathlib import Path

# 绝对路径定位到 traccia/reference/python
_PROJECT_ROOT = Path("D:/Traccia")
_reference_path = _PROJECT_ROOT / "traccia" / "reference" / "python"

if str(_reference_path) not in sys.path:
    sys.path.insert(0, str(_reference_path))

from .session import TracciaSession

__version__ = "0.1.0"


def start(objective: str) -> "TracciaSession":
    """创建一个新的 Traccia Session"""
    return TracciaSession(objective=objective)