import random, copy
from typing import Dict, Any

class EntropyInjector:
    """Inject structural uncertainty into tool outputs to trigger semantic residuals."""

    def __init__(self, drift_rate: float = 0.5, silent_fail_rate: float = 0.3, corrupt_rate: float = 0.2):
        self.drift_rate = drift_rate
        self.silent_fail_rate = silent_fail_rate
        self.corrupt_rate = corrupt_rate

    def inject(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Apply randomized entropy to a tool output dictionary."""
        result = copy.deepcopy(output)
        rand = random.random()
        if rand < self.drift_rate:
            result = self._schema_drift(result)
        elif rand < self.drift_rate + self.silent_fail_rate:
            result = self._silent_failure(result)
        elif rand < self.drift_rate + self.silent_fail_rate + self.corrupt_rate:
            result = self._partial_corruption(result)
        return result

    def _schema_drift(self, output: Dict) -> Dict:
        # Add an unexpected field to simulate schema change
        output["unexpected_field"] = "drifted_value"
        output["confidence"] = random.uniform(0, 1)
        return output

    def _silent_failure(self, output: Dict) -> Dict:
        # Return success status but null/empty result
        output["status"] = "success"
        output["result"] = None
        output["error"] = "hidden failure"
        return output

    def _partial_corruption(self, output: Dict) -> Dict:
        # Remove a key that agent might depend on
        output.pop("result", None)
        output.pop("data", None)
        return output
