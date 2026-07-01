from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class Recorder(ABC):
    """Recorder: translate runtime events into Protocol objects."""

    @abstractmethod
    def observe_llm(self, prompt: str, response: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Record an LLM interaction. Returns event_id."""
        ...

    @abstractmethod
    def observe_tool(self, tool_name: str, input: Dict[str, Any], output: Dict[str, Any],
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """Record a tool execution. Returns event_id."""
        ...

    @abstractmethod
    def observe_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> str:
        """Record an error. Returns event_id."""
        ...
