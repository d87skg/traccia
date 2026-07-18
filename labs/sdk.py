import sys, json
from pathlib import Path

# 确保核心模块路径
sys.path.insert(0, str(Path(__file__).parent))

from loop import run_loop
from residual import ResidualCaptureEngine
from recorder import DefaultRecorder

class ResidualLoop:
    """SDK wrapper for Traccia's closed-loop agent behavior system."""

    def __init__(self, objective: str = "SDK Session"):
        self.objective = objective
        self._history = []
        self._current_state = {}

    def run(self, iterations: int = 5, initial_evidence: str = None):
        """Run the loop and store history."""
        self._history = run_loop(iterations, initial_evidence)
        if self._history:
            self._current_state = self._history[-1]["residual"]
        return self._history

    @property
    def state(self) -> dict:
        """Return the most recent residual state."""
        return self._current_state

    @property
    def history(self) -> list:
        """Return full iteration history."""
        return self._history

    def export(self, filepath: str = "sdk_loop.json"):
        """Export history to JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.history, f, indent=2)
        return filepath
