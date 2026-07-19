import sys
from pathlib import Path
from typing import Dict, Any, Tuple

_src_path = Path(__file__).parent.parent.parent
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

from recorder.mapper import CanonicalMapper

class LangChainCanonicalMapper(CanonicalMapper):
    """Maps LangChain events to canonical types."""
    def map(self, raw_event: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        event_type = raw_event.get("event_type", "")
        payload = raw_event.get("payload", {})
        # Simple mapping logic
        if event_type == "llm_call":
            return ("llm.request", payload)
        elif event_type == "tool_call":
            return ("tool.invoke", payload)
        elif event_type == "error":
            return ("error.generic", payload)
        else:
            return (event_type, payload)
